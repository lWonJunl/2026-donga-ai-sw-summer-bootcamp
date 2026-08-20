import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import KnowledgeIngestForm, PreferenceForm, SignUpForm
from .context_cache import recent_messages
from .models import Conversation, KnowledgeSource, Message, UserPreference
from .ollama import ask_ollama, generate_title, stream_ollama

CONTEXT_INSTRUCTION = """당신은 이전 대화를 이어서 답하는 대화형 AI입니다.
대화 기록을 시간 순서대로 읽고 사용자의 마지막 메시지를 반드시 앞선 맥락과 연결해 해석하세요.
마지막 메시지가 짧거나 주어와 목적어가 생략되어 있으면 직전 질문과 답변을 바탕으로 자연스럽게 의미를 복원하세요.
이미 대화에서 확인할 수 있는 내용을 다시 묻지 말고, 합리적으로 추론할 수 있으면 바로 요청을 수행하세요.
앞선 맥락만으로 여러 해석이 가능할 때에만 짧게 확인 질문을 하세요."""


def signup(request):
    if request.user.is_authenticated:
        return redirect("chat")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserPreference.objects.create(user=user)
            login(request, user)
            return redirect("chat")
    else:
        form = SignUpForm()
    return render(request, "chat/signup.html", {"form": form})


def _current_conversation(user, conversation_id=None):
    orphans = user.chat_messages.filter(conversation__isnull=True)
    if orphans.exists():
        previous = Conversation.objects.create(user=user, title="이전 대화")
        orphans.update(conversation=previous)
    if conversation_id is not None:
        conversation = get_object_or_404(
            Conversation, id=conversation_id, user=user
        )
    else:
        conversation = user.conversations.first() or Conversation.objects.create(
            user=user
        )

    # 새 채팅을 여러 번 눌러 생긴 다른 빈 대화는 남기지 않습니다.
    user.conversations.filter(messages__isnull=True).exclude(
        id=conversation.id
    ).delete()
    return conversation


def _save_prompt(user, conversation, prompt):
    message = Message.objects.create(
        user=user, conversation=conversation, role="user", content=prompt
    )
    # 스트리밍이 중단되거나 브라우저가 닫혀도 최소한의 제목은 남깁니다.
    if not conversation.title_is_custom and conversation.title == "새 대화":
        conversation.title = prompt[:40]
    conversation.save()
    _audit_message(user.id, conversation.id, "user", prompt)
    return message


def _prompt_error(prompt):
    if not prompt:
        return "메시지를 입력하세요."
    if len(prompt) > settings.CHAT_MESSAGE_MAX_LENGTH:
        return f"메시지는 {settings.CHAT_MESSAGE_MAX_LENGTH:,}자 이하여야 합니다."
    return None


def _ollama_messages(conversation, preference):
    recent = recent_messages(conversation)
    return [
        {
            "role": "system",
            "content": (
                f"{CONTEXT_INSTRUCTION}\n\n사용자 개인 설정:\n"
                f"{preference.system_prompt[:settings.SYSTEM_PROMPT_MAX_LENGTH]}"
            ),
        },
        *recent,
    ]


def _rag_messages(user, conversation, preference, prompt):
    base_messages = _ollama_messages(conversation, preference)
    try:
        from .rag_pipeline import prepare_rag_messages

        return prepare_rag_messages(
            user, conversation, preference, prompt, base_messages
        )
    except ImportError:
        return base_messages, []


def _audit_message(user_id, conversation_id, role, content):
    try:
        from .rag_pipeline import audit_message

        audit_message(user_id, conversation_id, role, content)
    except ImportError:
        pass


def _auto_ingest_prompt_urls(user, prompt):
    try:
        from .rag_ingest import ingest_url
        from .rag_urls import extract_urls, url_fingerprint
    except ImportError:
        return []

    urls, overflow = extract_urls(prompt, settings.RAG_AUTO_URL_LIMIT)
    results = []
    for url in urls:
        fingerprint = url_fingerprint(url)
        already_ready = KnowledgeSource.objects.filter(
            user=user,
            source_type="url",
            status="ready",
            content_hash=fingerprint,
        ).exists() or KnowledgeSource.objects.filter(
            user=user,
            source_type="url",
            status="ready",
            source=url,
        ).exists()
        try:
            source = ingest_url(user, url)
            results.append(
                {
                    "url": url,
                    "name": source.display_name,
                    "status": "existing" if already_ready else "added",
                }
            )
        except Exception:
            results.append({"url": url, "name": url, "status": "failed"})
    if overflow:
        results.append(
            {
                "url": "",
                "name": f"링크는 한 메시지에서 최대 {settings.RAG_AUTO_URL_LIMIT}개까지 처리합니다.",
                "status": "limited",
            }
        )
    return results


def _flash_link_results(request, results):
    added = sum(item["status"] == "added" for item in results)
    existing = sum(item["status"] == "existing" for item in results)
    failed = sum(item["status"] == "failed" for item in results)
    if added:
        messages.success(request, f"프롬프트의 링크 {added}개를 내 지식 자료에 추가했습니다.")
    if existing:
        messages.info(request, f"이미 등록된 링크 {existing}개를 다시 사용했습니다.")
    if failed:
        messages.warning(request, f"링크 {failed}개를 수집하지 못했지만 채팅은 계속했습니다.")
    if any(item["status"] == "limited" for item in results):
        messages.warning(request, f"링크는 한 메시지에서 최대 {settings.RAG_AUTO_URL_LIMIT}개까지 처리합니다.")


def _update_auto_title(conversation):
    conversation.refresh_from_db(fields=["title", "title_is_custom"])
    first_user = conversation.messages.filter(role="user").first()
    old_auto_title = first_user.content[:40] if first_user else ""
    if conversation.title_is_custom or conversation.title not in {
        "새 대화",
        "이전 대화",
        old_auto_title,
    }:
        return conversation.title
    recent = list(conversation.messages.order_by("-created_at", "-id")[:6])
    recent.reverse()
    try:
        title = generate_title(
            [{"role": item.role, "content": item.content} for item in recent]
        )
    except RuntimeError:
        title = old_auto_title or "새 대화"
    conversation.title = title
    conversation.save(update_fields=["title", "updated_at"])
    return title


def _streaming_response(
    user, conversation, request_messages, temperature, sources=None, link_results=None
):
    sources = sources or []
    link_results = link_results or []
    def generate():
        chunks = []
        saved = False
        try:
            if link_results:
                yield json.dumps(
                    {"type": "links", "results": link_results}, ensure_ascii=False
                ) + "\n"
            for chunk in stream_ollama(request_messages, temperature):
                chunks.append(chunk)
                yield json.dumps(
                    {"type": "chunk", "content": chunk}, ensure_ascii=False
                ) + "\n"
            answer = "".join(chunks)
            if answer:
                Message.objects.create(
                    user=user,
                    conversation=conversation,
                    role="assistant",
                    content=answer,
                    sources=sources,
                )
                _audit_message(user.id, conversation.id, "assistant", answer)
                saved = True
            yield json.dumps(
                {"type": "done", "title": conversation.title, "sources": sources}, ensure_ascii=False
            ) + "\n"
        except RuntimeError as error:
            yield json.dumps(
                {"type": "error", "message": str(error)}, ensure_ascii=False
            ) + "\n"
        finally:
            # 브라우저에서 생성을 중지해도 이미 생성된 부분은 보존합니다.
            if chunks and not saved:
                Message.objects.create(
                    user=user,
                    conversation=conversation,
                    role="assistant",
                    content="".join(chunks),
                    sources=sources,
                )
                _audit_message(user.id, conversation.id, "assistant", "".join(chunks))

    response = StreamingHttpResponse(
        generate(), content_type="application/x-ndjson; charset=utf-8"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@login_required
def chat(request, conversation_id=None):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    conversation = _current_conversation(request.user, conversation_id)

    # JavaScript를 사용할 수 없는 브라우저를 위한 일반 전송 방식입니다.
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        prompt_error = _prompt_error(prompt)
        if prompt_error:
            messages.error(request, prompt_error)
        else:
            _save_prompt(request.user, conversation, prompt)
            link_results = _auto_ingest_prompt_urls(request.user, prompt)
            _flash_link_results(request, link_results)
            try:
                request_messages, sources = _rag_messages(
                    request.user, conversation, preference, prompt
                )
                answer = ask_ollama(request_messages, preference.temperature)
                Message.objects.create(
                    user=request.user,
                    conversation=conversation,
                    role="assistant",
                    content=answer,
                    sources=sources,
                )
                _audit_message(request.user.id, conversation.id, "assistant", answer)
                _update_auto_title(conversation)
            except (RuntimeError, KeyError, ValueError) as error:
                messages.error(request, str(error))
        return redirect("conversation", conversation_id=conversation.id)

    return render(
        request,
        "chat/chat.html",
        {
            "chat_messages": conversation.messages.all(),
            "conversation": conversation,
            "conversations": request.user.conversations.annotate(
                message_count=Count("messages")
            ).filter(message_count__gt=0),
            "preference": preference,
        },
    )


@login_required
def stream_chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)
    prompt = request.POST.get("prompt", "").strip()
    prompt_error = _prompt_error(prompt)
    if prompt_error:
        return JsonResponse({"error": prompt_error}, status=400)

    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    _save_prompt(request.user, conversation, prompt)
    link_results = _auto_ingest_prompt_urls(request.user, prompt)
    request_messages, sources = _rag_messages(
        request.user, conversation, preference, prompt
    )
    return _streaming_response(
        request.user,
        conversation,
        request_messages,
        preference.temperature,
        sources,
        link_results,
    )


@login_required
def regenerate_chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)

    last_message = conversation.messages.order_by("-created_at", "-id").first()
    if not last_message or last_message.role != "assistant":
        return JsonResponse({"error": "다시 생성할 답변이 없습니다."}, status=400)

    last_message.delete()
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    last_user = conversation.messages.filter(role="user").order_by("-created_at", "-id").first()
    if not last_user:
        return JsonResponse({"error": "다시 생성할 질문이 없습니다."}, status=400)
    request_messages, sources = _rag_messages(
        request.user, conversation, preference, last_user.content
    )
    return _streaming_response(
        request.user,
        conversation,
        request_messages,
        preference.temperature,
        sources,
    )


@login_required
def generate_chat_title(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)
    return JsonResponse({"title": _update_auto_title(conversation)})


@login_required
def new_chat(request):
    if request.method != "POST":
        return redirect("chat")
    request.user.conversations.filter(messages__isnull=True).delete()
    conversation = Conversation.objects.create(user=request.user)
    return redirect("conversation", conversation_id=conversation.id)


@login_required
def rename_chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)
    title = request.POST.get("title", "").strip()[:80]
    if title:
        conversation.title = title
        conversation.title_is_custom = True
        conversation.save(update_fields=["title", "title_is_custom", "updated_at"])
        messages.success(request, "대화 이름을 수정했습니다.")
    else:
        messages.error(request, "대화 이름을 입력하세요.")
    return redirect("conversation", conversation_id=conversation.id)


@login_required
def delete_chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)
    try:
        from .rag_memory import RAGMemory

        RAGMemory(request.user.id, conversation.id).clear()
    except Exception:
        pass
    conversation.delete()
    messages.success(request, "대화를 삭제했습니다.")
    next_conversation = request.user.conversations.first()
    if next_conversation:
        return redirect("conversation", conversation_id=next_conversation.id)
    return redirect("chat")


@login_required
def settings_view(request):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = PreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, "개인 설정을 저장했습니다.")
            return redirect("settings")
    else:
        form = PreferenceForm(instance=preference)
    return render(request, "chat/settings.html", {"form": form})


@login_required
def knowledge_view(request):
    if request.method == "POST":
        form = KnowledgeIngestForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                from .rag_ingest import ingest_uploaded_file, ingest_url
            except ImportError:
                messages.error(request, "RAG 패키지가 설치되지 않았습니다. requirements.txt를 설치하세요.")
                return redirect("knowledge")
            completed = 0
            for url in form.cleaned_data["urls"]:
                try:
                    ingest_url(request.user, url)
                    completed += 1
                except Exception as error:
                    messages.error(request, f"{url}: {error}")
            for upload in form.cleaned_data["files"]:
                try:
                    ingest_uploaded_file(request.user, upload)
                    completed += 1
                except Exception as error:
                    messages.error(request, f"{upload.name}: {error}")
            if completed:
                messages.success(request, f"지식 자료 {completed}개를 등록했습니다.")
            return redirect("knowledge")
    else:
        form = KnowledgeIngestForm()
    return render(
        request,
        "chat/knowledge.html",
        {"form": form, "knowledge_sources": KnowledgeSource.objects.filter(user=request.user)},
    )


@login_required
def delete_knowledge_source_view(request, source_id):
    source = get_object_or_404(KnowledgeSource, id=source_id, user=request.user)
    if request.method != "POST":
        return redirect("knowledge")
    try:
        from .rag_ingest import delete_knowledge_source

        display_name = source.display_name
        delete_knowledge_source(source)
        messages.success(request, f"{display_name} 자료를 삭제했습니다.")
    except Exception as error:
        messages.error(request, f"자료를 삭제하지 못했습니다: {error}")
    return redirect("knowledge")


@login_required
def clear_rag_memory(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == "POST":
        try:
            from .rag_memory import RAGMemory

            RAGMemory(request.user.id, conversation.id).clear()
            messages.success(request, "이 대화의 Redis 메모리를 삭제했습니다.")
        except Exception as error:
            messages.error(request, f"Redis 메모리를 삭제하지 못했습니다: {error}")
    return redirect("conversation", conversation_id=conversation.id)


@login_required
def update_temperature(request):
    if request.method != "POST":
        return redirect("chat")
    try:
        temperature = round(float(request.POST.get("temperature", "")), 1)
    except (TypeError, ValueError):
        return JsonResponse({"error": "올바른 창의성 값을 선택하세요."}, status=400)
    if not 0.0 <= temperature <= 1.5:
        return JsonResponse({"error": "창의성 값은 0.0에서 1.5 사이여야 합니다."}, status=400)

    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    preference.temperature = temperature
    preference.save(update_fields=["temperature"])
    return JsonResponse({"temperature": temperature})
