from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="exaone3.5:7.8b",
    base_url="http://127.0.0.1:11434",
    temperature=0,
)
answer = llm.invoke(
    "Windows에서 가상환경을 쓰는 이유는?"
)
print(answer.content)
