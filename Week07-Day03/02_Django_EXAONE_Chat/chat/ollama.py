import json
from urllib.error import URLError
from urllib.request import Request, urlopen

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "exaone3.5:7.8b"


def stream_ollama(messages, temperature, num_predict=512):
    payload = json.dumps(
        {
            "model": MODEL,
            "messages": messages,
            "stream": True,
            "keep_alive": "30m",
            "options": {
                "num_ctx": 2048,
                "num_predict": num_predict,
                "temperature": temperature,
            },
        }
    ).encode("utf-8")
    request = Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            for line in response:
                if not line.strip():
                    continue
                data = json.loads(line.decode("utf-8"))
                if data.get("error"):
                    raise RuntimeError(data["error"])
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
                if data.get("done"):
                    break
    except (URLError, TimeoutError, OSError, ValueError) as error:
        raise RuntimeError(
            "Ollama 응답 시간이 너무 길거나 연결할 수 없습니다. 잠시 후 다시 시도하세요."
        ) from error


def ask_ollama(messages, temperature):
    return "".join(stream_ollama(messages, temperature))


def generate_title(messages):
    excerpt = "\n".join(
        f"{item['role']}: {item['content'][:500]}" for item in messages[-4:]
    )
    prompt = (
        "다음 대화의 핵심 주제를 한국어 제목 하나로 요약하세요. "
        "15자 안팎으로 작성하고 따옴표, 마침표, 설명은 쓰지 마세요.\n\n"
        + excerpt
    )
    result = "".join(
        stream_ollama([{"role": "user", "content": prompt}], 0.2, num_predict=24)
    )
    title = result.strip().splitlines()[0].strip(' "\'`#*.-')
    return title[:80] or "새 대화"
