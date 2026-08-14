import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .context_cache import UTF8StringSerializer
from .forms import PreferenceForm
from .models import Conversation, KnowledgeSource, Message, UserPreference
from .rag_loaders import validate_public_url
from .rag_urls import extract_urls, normalize_url, url_fingerprint
from .templatetags.chat_format import format_message
from .views import _auto_ingest_prompt_urls, _ollama_messages


class AccountTests(TestCase):
    def test_signup_creates_user_and_preference(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "student",
                "email": "student@example.com",
                "password1": "Safe-password-123!",
                "password2": "Safe-password-123!",
            },
        )
        self.assertRedirects(response, reverse("chat"))
        user = User.objects.get(username="student")
        self.assertTrue(UserPreference.objects.filter(user=user).exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_html_response_explicitly_uses_utf8(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.charset, "utf-8")
        self.assertContains(response, '<meta charset="utf-8">')


class RAGSecurityTests(TestCase):
    def test_url_loader_rejects_local_network(self):
        with self.assertRaisesRegex(ValueError, "내부망"):
            validate_public_url("http://127.0.0.1/private")

    def test_url_loader_rejects_embedded_credentials(self):
        with self.assertRaisesRegex(ValueError, "인증정보"):
            validate_public_url("https://user:password@example.com/")

    def test_prompt_url_extraction_normalizes_and_deduplicates(self):
        urls, overflow = extract_urls(
            "https://Example.com:443/docs#intro 와 https://example.com/docs 를 봐줘."
        )
        self.assertEqual(urls, ["https://example.com/docs"])
        self.assertFalse(overflow)

    def test_prompt_url_extraction_limits_links(self):
        urls, overflow = extract_urls(
            " ".join(f"https://example.com/{number}" for number in range(5)), limit=3
        )
        self.assertEqual(len(urls), 3)
        self.assertTrue(overflow)

    def test_url_normalization_does_not_hide_credentials(self):
        with self.assertRaisesRegex(ValueError, "인증정보"):
            normalize_url("https://user:password@example.com/private")

    @patch("chat.rag_ingest.get_vector_store")
    @patch("chat.rag_ingest.load_url")
    def test_ingest_url_reuses_ready_document(self, mocked_load, mocked_store):
        from langchain_core.documents import Document
        from .rag_ingest import ingest_url

        user = User.objects.create_user("url-owner", password="password123!")
        mocked_load.return_value = [
            Document(page_content="중복 검사 문서", metadata={"source": "https://example.com/docs"})
        ]
        first = ingest_url(user, "https://EXAMPLE.com:443/docs#top")
        second = ingest_url(user, "https://example.com/docs")
        self.assertEqual(first.id, second.id)
        self.assertEqual(first.content_hash, url_fingerprint("https://example.com/docs"))
        self.assertEqual(mocked_load.call_count, 1)
        self.assertEqual(mocked_store.return_value.add_documents.call_count, 1)

    def test_knowledge_list_is_user_scoped(self):
        owner = User.objects.create_user("owner", password="password123!")
        other = User.objects.create_user("other", password="password123!")
        KnowledgeSource.objects.create(
            user=owner, source_type="url", source="https://example.com/a", display_name="owner-doc"
        )
        KnowledgeSource.objects.create(
            user=other, source_type="url", source="https://example.com/b", display_name="private-other-doc"
        )
        self.client.force_login(owner)
        response = self.client.get(reverse("knowledge"))
        self.assertContains(response, "owner-doc")
        self.assertNotContains(response, "private-other-doc")

    @patch("chat.rag_ingest.ingest_url")
    def test_prompt_url_auto_ingest_reports_existing_document(self, mocked_ingest):
        user = User.objects.create_user("auto-owner", password="password123!")
        url = "https://example.com/guide"
        source = KnowledgeSource.objects.create(
            user=user,
            source_type="url",
            source=url,
            display_name=url,
            content_hash=url_fingerprint(url),
            status="ready",
        )
        mocked_ingest.return_value = source
        results = _auto_ingest_prompt_urls(user, f"{url} 내용을 요약해줘")
        self.assertEqual(results[0]["status"], "existing")
        mocked_ingest.assert_called_once_with(user, url)

    @patch("chat.rag_store.delete_source_documents")
    def test_owner_can_delete_ready_knowledge_and_vectors(self, mocked_delete):
        user = User.objects.create_user("delete-owner", password="password123!")
        source = KnowledgeSource.objects.create(
            user=user,
            source_type="url",
            source="https://example.com/delete",
            display_name="delete-doc",
            status="ready",
        )
        self.client.force_login(user)
        response = self.client.post(reverse("delete_knowledge_source", args=[source.id]))
        self.assertRedirects(response, reverse("knowledge"))
        self.assertFalse(KnowledgeSource.objects.filter(id=source.id).exists())
        mocked_delete.assert_called_once_with(user.id, "https://example.com/delete")

    @patch("chat.rag_store.delete_source_documents", side_effect=RuntimeError("Milvus 오류"))
    def test_vector_failure_keeps_ready_knowledge_record(self, mocked_delete):
        user = User.objects.create_user("delete-failure", password="password123!")
        source = KnowledgeSource.objects.create(
            user=user,
            source_type="url",
            source="https://example.com/keep",
            display_name="keep-doc",
            status="ready",
        )
        self.client.force_login(user)
        self.client.post(reverse("delete_knowledge_source", args=[source.id]))
        self.assertTrue(KnowledgeSource.objects.filter(id=source.id).exists())

    def test_user_cannot_delete_another_users_knowledge(self):
        owner = User.objects.create_user("delete-private-owner", password="password123!")
        other = User.objects.create_user("delete-private-other", password="password123!")
        source = KnowledgeSource.objects.create(
            user=owner,
            source_type="url",
            source="https://example.com/private",
            display_name="private-doc",
            status="failed",
        )
        self.client.force_login(other)
        response = self.client.post(reverse("delete_knowledge_source", args=[source.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(KnowledgeSource.objects.filter(id=source.id).exists())

    @patch("chat.rag_store.delete_source_documents", side_effect=ConnectionError)
    def test_failed_upload_deletion_removes_safely_scoped_file(self, mocked_delete):
        from .rag_ingest import delete_knowledge_source

        user = User.objects.create_user("file-delete-owner", password="password123!")
        with TemporaryDirectory() as directory:
            user_directory = Path(directory) / str(user.id)
            user_directory.mkdir()
            file_path = user_directory / "document.docx"
            file_path.write_bytes(b"test")
            source = KnowledgeSource.objects.create(
                user=user,
                source_type="docx",
                source=str(file_path),
                display_name="document.docx",
                status="failed",
            )
            with override_settings(RAG_UPLOAD_DIR=Path(directory)):
                delete_knowledge_source(source)
            self.assertFalse(file_path.exists())
            self.assertFalse(KnowledgeSource.objects.filter(id=source.id).exists())


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests-default",
        },
        "context": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests-context",
        },
    }
)
class PersonalizationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("first", password="test-password")
        self.other = User.objects.create_user("second", password="test-password")

    def test_user_only_sees_own_messages(self):
        Message.objects.create(user=self.user, role="user", content="내 질문")
        Message.objects.create(user=self.other, role="user", content="다른 질문")
        self.client.force_login(self.user)
        response = self.client.get(reverse("chat"))
        self.assertContains(response, "내 질문")
        self.assertNotContains(response, "다른 질문")

    @patch("chat.views._rag_messages", return_value=([{"role": "user", "content": "질문"}], []))
    @patch(
        "chat.views._auto_ingest_prompt_urls",
        return_value=[{"url": "https://example.com/", "name": "https://example.com/", "status": "added"}],
    )
    @patch("chat.views.stream_ollama", return_value=iter(["답변"]))
    def test_stream_reports_automatic_link_ingest(self, mocked_stream, mocked_auto, mocked_rag):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("stream_chat", args=[conversation.id]),
            {"prompt": "https://example.com 내용을 알려줘"},
        )
        events = [json.loads(line) for line in b"".join(response.streaming_content).decode().splitlines()]
        self.assertEqual(events[0]["type"], "links")
        self.assertEqual(events[0]["results"][0]["status"], "added")
        mocked_auto.assert_called_once_with(self.user, "https://example.com 내용을 알려줘")

    def test_user_can_save_personal_settings(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("settings"),
            {"system_prompt": "코딩 선생님처럼 답해 줘"},
        )
        self.assertRedirects(response, reverse("settings"))
        preference = UserPreference.objects.get(user=self.user)
        self.assertEqual(preference.system_prompt, "코딩 선생님처럼 답해 줘")
        self.assertEqual(preference.temperature, 0.7)

    def test_settings_page_has_polished_controls(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("settings"))
        self.assertContains(response, "AI 응답 방식")
        self.assertContains(response, "친절한 선생님")
        self.assertNotContains(response, 'id="id_temperature"')
        self.assertContains(response, "설정 저장")

    def test_creativity_control_is_shown_near_chat_prompt(self):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("conversation", args=[conversation.id]))

        self.assertContains(response, 'id="creativity-button"')
        self.assertContains(response, 'id="creativity-range"')
        self.assertContains(response, 'id="creativity-button-value">0.7</span>')

    def test_user_can_update_temperature_from_chat(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("update_temperature"), {"temperature": "1.2"}
        )

        self.assertEqual(response.status_code, 200)
        preference = UserPreference.objects.get(user=self.user)
        self.assertEqual(preference.temperature, 1.2)

    def test_context_cache_serializer_uses_plain_utf8_instead_of_pickle(self):
        serializer = UTF8StringSerializer()
        value = '[{"role":"user","content":"안녕"}]'

        encoded = serializer.dumps(value)

        self.assertEqual(encoded, value.encode("utf-8"))
        self.assertEqual(serializer.loads(encoded), value)

    @override_settings(SYSTEM_PROMPT_MAX_LENGTH=5)
    def test_system_prompt_has_server_side_length_limit(self):
        form = PreferenceForm({"system_prompt": "123456"})

        self.assertFalse(form.is_valid())
        self.assertIn("system_prompt", form.errors)

    @override_settings(CHAT_MESSAGE_MAX_LENGTH=5)
    def test_stream_rejects_oversized_prompt_before_saving(self):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("stream_chat", args=[conversation.id]),
            {"prompt": "123456"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Message.objects.filter(conversation=conversation).exists())

    def test_ollama_messages_preserve_follow_up_context_in_order(self):
        conversation = Conversation.objects.create(user=self.user)
        preference = UserPreference.objects.create(
            user=self.user, system_prompt="핵심부터 간결하게 답하세요."
        )
        for role, content in (
            ("user", "개발 아이디어"),
            ("assistant", "어떤 아이디어를 원하시나요?"),
            ("user", "너가 달라고"),
        ):
            Message.objects.create(
                user=self.user,
                conversation=conversation,
                role=role,
                content=content,
            )

        request_messages = _ollama_messages(conversation, preference)

        self.assertIn("앞선 맥락과 연결해 해석", request_messages[0]["content"])
        self.assertIn("핵심부터 간결하게", request_messages[0]["content"])
        self.assertEqual(
            [(item["role"], item["content"]) for item in request_messages[1:]],
            [
                ("user", "개발 아이디어"),
                ("assistant", "어떤 아이디어를 원하시나요?"),
                ("user", "너가 달라고"),
            ],
        )

    @patch("chat.context_cache._context_cache")
    def test_ollama_messages_reads_recent_context_from_redis(self, mocked_cache):
        conversation = Conversation.objects.create(user=self.user)
        preference = UserPreference.objects.create(user=self.user)
        cached = [{"role": "user", "content": "Redis의 맥락"}]
        mocked_cache.return_value.get.return_value = json.dumps(
            cached, ensure_ascii=False
        )

        request_messages = _ollama_messages(conversation, preference)

        self.assertEqual(request_messages[1:], cached)
        mocked_cache.return_value.get.assert_called_once_with(
            f"conversation:{conversation.id}:recent-messages"
        )

    @patch("chat.context_cache._context_cache")
    def test_redis_failure_falls_back_to_sqlite(self, mocked_cache):
        conversation = Conversation.objects.create(user=self.user)
        preference = UserPreference.objects.create(user=self.user)
        Message.objects.create(
            user=self.user,
            conversation=conversation,
            role="user",
            content="SQLite의 맥락",
        )
        mocked_cache.return_value.get.side_effect = ConnectionError("Redis down")

        request_messages = _ollama_messages(conversation, preference)

        self.assertEqual(
            request_messages[1:],
            [{"role": "user", "content": "SQLite의 맥락"}],
        )

    @patch("chat.context_cache._context_cache")
    def test_invalid_cached_context_falls_back_to_sqlite(self, mocked_cache):
        conversation = Conversation.objects.create(user=self.user)
        preference = UserPreference.objects.create(user=self.user)
        Message.objects.create(
            user=self.user,
            conversation=conversation,
            role="user",
            content="검증된 DB 맥락",
        )
        mocked_cache.return_value.get.return_value = json.dumps(
            [{"role": "system", "content": "변조된 캐시"}], ensure_ascii=False
        )

        request_messages = _ollama_messages(conversation, preference)

        self.assertEqual(
            request_messages[1:],
            [{"role": "user", "content": "검증된 DB 맥락"}],
        )

    @patch("chat.context_cache._context_cache")
    def test_saved_message_refreshes_redis_context(self, mocked_cache):
        conversation = Conversation.objects.create(user=self.user)

        Message.objects.create(
            user=self.user,
            conversation=conversation,
            role="assistant",
            content="저장 후에도 남는 맥락",
        )

        key, value = mocked_cache.return_value.set.call_args.args[:2]
        self.assertEqual(key, f"conversation:{conversation.id}:recent-messages")
        self.assertEqual(
            json.loads(value),
            [{"role": "assistant", "content": "저장 후에도 남는 맥락"}],
        )

    def test_user_can_rename_own_conversation(self):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("rename_chat", args=[conversation.id]), {"title": "수정한 이름"}
        )
        self.assertRedirects(
            response, reverse("conversation", args=[conversation.id])
        )
        conversation.refresh_from_db()
        self.assertEqual(conversation.title, "수정한 이름")
        self.assertTrue(conversation.title_is_custom)

    def test_user_can_only_delete_own_conversation(self):
        own = Conversation.objects.create(user=self.user, title="내 대화")
        Message.objects.create(
            user=self.user,
            conversation=own,
            role="user",
            content="삭제할 메시지",
        )
        other = Conversation.objects.create(user=self.other, title="다른 대화")
        self.client.force_login(self.user)
        response = self.client.post(reverse("delete_chat", args=[own.id]))
        self.assertRedirects(response, reverse("chat"))
        self.assertFalse(Conversation.objects.filter(id=own.id).exists())
        self.assertFalse(Message.objects.filter(conversation_id=own.id).exists())
        response = self.client.post(reverse("delete_chat", args=[other.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Conversation.objects.filter(id=other.id).exists())

    @patch("chat.views.stream_ollama", return_value=iter(["안녕", "하세요"]))
    def test_streaming_chat_saves_complete_answer(self, mocked_stream):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("stream_chat", args=[conversation.id]), {"prompt": "인사해 줘"}
        )
        body = b"".join(response.streaming_content).decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn('"type": "chunk"', body)
        self.assertIn('"type": "done"', body)
        self.assertTrue(mocked_stream.called)
        self.assertTrue(
            Message.objects.filter(
                conversation=conversation, role="assistant", content="안녕하세요"
            ).exists()
        )

    def test_action_urls_do_not_return_405_when_opened(self):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        for name in (
            "stream_chat",
            "regenerate_chat",
            "generate_chat_title",
            "rename_chat",
            "delete_chat",
        ):
            response = self.client.get(reverse(name, args=[conversation.id]))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url, reverse("conversation", args=[conversation.id])
            )

        response = self.client.get(reverse("new_chat"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("chat"))

    @patch("chat.views.stream_ollama", return_value=iter(["새 ", "답변"]))
    def test_regenerate_replaces_last_answer(self, mocked_stream):
        conversation = Conversation.objects.create(user=self.user)
        Message.objects.create(
            user=self.user, conversation=conversation, role="user", content="질문"
        )
        Message.objects.create(
            user=self.user, conversation=conversation, role="assistant", content="옛 답변"
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("regenerate_chat", args=[conversation.id]))
        b"".join(response.streaming_content)

        self.assertFalse(
            Message.objects.filter(conversation=conversation, content="옛 답변").exists()
        )
        self.assertTrue(
            Message.objects.filter(conversation=conversation, content="새 답변").exists()
        )
        self.assertTrue(mocked_stream.called)

    def test_message_markdown_is_formatted_and_html_is_escaped(self):
        rendered = str(format_message("**굵게**\n```python\nprint('ok')\n```\n<script>"))
        self.assertIn("<strong>굵게</strong>", rendered)
        self.assertIn("<pre><code", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_code_language_cannot_break_out_of_html_attribute(self):
        rendered = str(
            format_message('```"><img src=x onerror=alert(1)>\ncode\n```')
        )

        self.assertNotIn("<img", rendered)
        self.assertNotIn('class="language-\">', rendered)
        self.assertIn("&quot;&gt;&lt;img", rendered)

    def test_saved_markdown_is_rendered_on_chat_page(self):
        conversation = Conversation.objects.create(user=self.user, title="Markdown")
        Message.objects.create(
            user=self.user,
            conversation=conversation,
            role="assistant",
            content="**굵은 글씨**와 `코드`",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("conversation", args=[conversation.id]))

        self.assertContains(response, "<strong>굵은 글씨</strong>", html=True)
        self.assertContains(response, "<code>코드</code>", html=True)
        self.assertNotContains(response, "**굵은 글씨**")

    def test_message_sent_time_is_rendered_in_seoul_time(self):
        conversation = Conversation.objects.create(user=self.user, title="시간 표시")
        message = Message.objects.create(
            user=self.user,
            conversation=conversation,
            role="user",
            content="언제 보냈지?",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("conversation", args=[conversation.id]))
        expected = timezone.localtime(message.created_at).strftime("%Y.%m.%d %H:%M")

        self.assertContains(response, expected)
        self.assertContains(response, 'class="message-time"')

    def test_each_message_has_a_copy_button(self):
        conversation = Conversation.objects.create(user=self.user, title="복사 테스트")
        Message.objects.create(
            user=self.user, conversation=conversation, role="user", content="질문"
        )
        Message.objects.create(
            user=self.user, conversation=conversation, role="assistant", content="답변"
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("conversation", args=[conversation.id]))

        self.assertContains(response, 'class="message-copy-button"', count=2)
        self.assertContains(response, "navigator.clipboard")

    def test_code_blocks_get_a_code_only_copy_button(self):
        conversation = Conversation.objects.create(user=self.user, title="코드 복사")
        Message.objects.create(
            user=self.user,
            conversation=conversation,
            role="assistant",
            content="```python\nprint('hello')\n```",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("conversation", args=[conversation.id]))

        self.assertContains(response, "addCodeCopyButtons")
        self.assertContains(response, 'button.textContent = "코드 복사"')
        self.assertContains(response, 'querySelector("code")?.textContent')

    def test_clear_content_button_is_not_rendered(self):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(reverse("conversation", args=[conversation.id]))
        self.assertNotContains(response, "내용 지우기")

    def test_empty_conversation_is_not_shown_in_sidebar(self):
        empty = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("conversation", args=[empty.id]))

        self.assertNotContains(response, 'class="conversation-item active"')
        self.assertNotContains(response, ">새 대화<")

    def test_repeated_new_chat_keeps_only_one_empty_conversation(self):
        self.client.force_login(self.user)
        self.client.post(reverse("new_chat"))
        self.client.post(reverse("new_chat"))
        self.client.post(reverse("new_chat"))

        empty_count = Conversation.objects.filter(
            user=self.user, messages__isnull=True
        ).count()
        self.assertEqual(empty_count, 1)

    def test_sidebar_has_collapse_and_expand_controls(self):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(reverse("conversation", args=[conversation.id]))
        self.assertContains(response, 'id="collapse-sidebar"')
        self.assertContains(response, 'id="open-sidebar"')
        self.assertContains(response, "exaone-sidebar-collapsed")

    def test_model_name_has_no_dropdown_decoration(self):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(reverse("conversation", args=[conversation.id]))
        self.assertContains(response, '<div class="model-name">EXAONE 3.5</div>')
        self.assertNotContains(response, "⌄")

    @patch("chat.views.stream_ollama", return_value=iter(["부분 답변"]))
    def test_chat_has_fallback_title_before_stream_finishes(self, mocked_stream):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("stream_chat", args=[conversation.id]),
            {"prompt": "중단되어도 이 질문으로 제목을 남겨줘"},
        )

        conversation.refresh_from_db()
        self.assertEqual(conversation.title, "중단되어도 이 질문으로 제목을 남겨줘")
        response.close()

    def test_stopped_stream_requests_auto_title(self):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(reverse("conversation", args=[conversation.id]))
        self.assertContains(response, "window.setTimeout(requestAutoTitle, 300)")
        self.assertContains(response, 'hasUrl ? "링크 수집 및 분석 중…" : "생각 중…"')

    @patch("chat.views.generate_title", return_value="파이썬 반복문 이해하기")
    @patch("chat.views.stream_ollama", return_value=iter(["반복문", " 설명"]))
    def test_title_is_automatically_summarized(self, mocked_stream, mocked_title):
        conversation = Conversation.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("stream_chat", args=[conversation.id]),
            {"prompt": "파이썬 for 반복문을 예제와 함께 알려줘"},
        )
        b"".join(response.streaming_content)

        self.assertFalse(mocked_title.called)
        title_response = self.client.post(
            reverse("generate_chat_title", args=[conversation.id])
        )

        conversation.refresh_from_db()
        self.assertEqual(conversation.title, "파이썬 반복문 이해하기")
        self.assertFalse(conversation.title_is_custom)
        self.assertTrue(mocked_title.called)
        self.assertEqual(title_response.json()["title"], "파이썬 반복문 이해하기")

    @patch("chat.views.generate_title", return_value="바뀌면 안 되는 제목")
    @patch("chat.views.stream_ollama", return_value=iter(["새 답변"]))
    def test_custom_title_is_not_overwritten(self, mocked_stream, mocked_title):
        conversation = Conversation.objects.create(
            user=self.user, title="내가 정한 제목", title_is_custom=True
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("stream_chat", args=[conversation.id]), {"prompt": "새 질문"}
        )
        b"".join(response.streaming_content)
        self.client.post(reverse("generate_chat_title", args=[conversation.id]))

        conversation.refresh_from_db()
        self.assertEqual(conversation.title, "내가 정한 제목")
        self.assertFalse(mocked_title.called)
