import heapq

graph = {
    'A': [('B', 2), ('D', 5)],
    'B': [('C', 9), ('D', 1)],
    'C': [('A', 4), ('B', 1), ('D', 7)],
    'D': [('B', 1)]
}

def dijkstra_path(graph, start):
    dist = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}

    dist[start] = 0
    pq = [(0, start)]

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current_dist > dist[current]:
            continue

        for neighbor, weight in graph[current]:
            new_dist = current_dist + weight

            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))

    return dist, prev


def build_path(prev, target):
    path = []
    node = target

    while node is not None:
        path.append(node)
        node = prev[node]

    return path[::-1]


dist, prev = dijkstra_path(graph, 'A')

target = 'D'
path = build_path(prev, target)

print(f"{target}의 최단 거리: {dist[target]}")
print(f"{target}의 최단 경로: {' -> '.join(path)}")