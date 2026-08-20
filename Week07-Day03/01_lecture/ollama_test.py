from ollama import Client

client = Client(host="http://127.0.0.1:11434")
response = client.chat(
    model="exaone3.5:7.8b",
    messages=[{
        "role": "user",
        "content": "가상환경의 장점을 한 문장으로 설명해줘",
    }],
)
print(response.message.content)
