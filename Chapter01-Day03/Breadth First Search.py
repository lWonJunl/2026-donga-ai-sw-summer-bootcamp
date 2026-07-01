from collections import deque

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

    # 너비 우선 탐색 (BFS)
    def bfs(self, start):
        # 방문한 정점을 저장하는 집합(Set)
        visited = set()

        # 탐색할 정점을 저장하는 큐(Queue)
        queue = deque()

        # BFS 탐색 순서를 저장하는 리스트
        result = []

        # 시작 정점을 큐에 삽입
        queue.append(start)

        # 시작 정점을 방문 처리
        visited.add(start)

        # BFS 탐색 시작 출력
        print("BFS 탐색 시작")
        print("초기 큐:", list(queue))
        print()

        # 탐색 단계를 출력하기 위한 변수
        step = 1

        # 큐가 빌 때까지 반복
        while queue:

            # 큐의 맨 앞 정점을 꺼냄(FIFO)
            current = queue.popleft()

            # 현재 정점을 탐색 결과에 저장
            result.append(current)

            # 현재 탐색 상황 출력
            print(f"[{step}단계]")
            print("현재 방문한 정점:", current)
            print("현재까지 탐색 결과:", result)

            # 현재 정점과 연결된 모든 정점을 확인
            for neighbor in self.graph[current]:

                # 아직 방문하지 않은 정점이라면
                if neighbor not in visited:

                    # 방문 처리
                    visited.add(neighbor)

                    # 큐에 추가
                    queue.append(neighbor)

                    print(f"  → {neighbor} 발견, 큐에 추가")

            # 현재 큐 상태 출력
            print("현재 큐 상태:", list(queue))
            print()

            # 단계 증가
            step += 1

        # BFS 최종 탐색 결과 출력
        print("BFS 최종 탐색 순서:", result)

        # 탐색 결과 반환
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

# BFS 탐색 시작
g.bfs(1)