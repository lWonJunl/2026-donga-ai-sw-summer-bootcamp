class Graph:
    def __init__(self):
        self.graph = {}

    # 간선 추가
    def add_edge(self, start, end):
        # 시작 정점이 없으면 정점을 생성
        if start not in self.graph:
            self.graph[start] = []

        # 끝 정점이 없으면 정점을 생성
        if end not in self.graph:
            self.graph[end] = []

        # 간선 추가 (양방향)
        self.graph[start].append(end)
        self.graph[end].append(start)

    # 깊이 우선 탐색 (DFS)
    def dfs(self, start, visited=None, result=None, depth=0):
        # visited 생성 및 초기화
        if visited is None:
            visited = set()

        # result 생성 및 초기화
        if result is None:
            result = []
            print("DFS 탐색 시작")
            print()

        # DFS 탐색 과정 저장
        visited.add(start)
        result.append(start)

        # 깊이(depth)에 따라 들여쓰기(indent) 설정
        indent = "  " * depth

        # 탐색 과정 출력
        print(f"{indent}현재 방문한 정점: {start}")
        print(f"{indent}현재까지 탐색 결과: {result}")

        for neighbor in self.graph[start]:
            if neighbor not in visited:
                print(f"{indent}→ {neighbor}로 이동")
                self.dfs(neighbor, visited, result, depth + 1)
            else:
                print(f"{indent}→ {neighbor}는 이미 방문함")

        if depth == 0:
            print()
            print("DFS 최종 탐색 순서:", result)

        return result

# 그래프 생성
g = Graph()

# 간선 추가
g.add_edge(1, 2)
g.add_edge(1, 3)
g.add_edge(2, 4)
g.add_edge(2, 5)
g.add_edge(3, 6)
g.add_edge(3, 7)

# DFS 탐색 시작
g.dfs(1)