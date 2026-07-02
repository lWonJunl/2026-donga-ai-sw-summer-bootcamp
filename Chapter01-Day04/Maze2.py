import cv2
import numpy as np
from collections import deque

# ==========================================================
# 1. 이미지 읽기
# ==========================================================

img = cv2.imread("maze.jpg")

if img is None:
    print("이미지를 읽을 수 없습니다.")
    exit()

# ==========================================================
# 2. 흑백 변환
# ==========================================================

gray = cv2.cvtColor(
    img,
    cv2.COLOR_BGR2GRAY
)

# ==========================================================
# 3. 여백 제거
# ==========================================================

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 검은색만 추출
_, binary = cv2.threshold(
    gray,
    200,
    255,
    cv2.THRESH_BINARY_INV
)

# 검은색 픽셀 좌표
points = cv2.findNonZero(binary)

# 가장 작은 사각형
x, y, w, h = cv2.boundingRect(points)

# 너무 딱 맞게 자르면 입구가 잘릴 수 있으므로 여백 5픽셀 추가
margin = 0

x = max(0, x - margin)
y = max(0, y - margin)

w = min(img.shape[1] - x, w + margin * 2)
h = min(img.shape[0] - y, h + margin * 2)

# 미로만 잘라내기
maze = img[y:y+h, x:x+w]

# ==========================================================
# 8. 길(Path) 마스크 생성
# ==========================================================

gray_maze = cv2.cvtColor(
    maze,
    cv2.COLOR_BGR2GRAY
)

# 흰색 = 길(255)
# 검은색 = 벽(0)
_, path_mask = cv2.threshold(
    gray_maze,
    100,
    255,
    cv2.THRESH_BINARY
)

# 노이즈 제거
kernel = np.ones((3,3), np.uint8)

path_mask = cv2.morphologyEx(
    path_mask,
    cv2.MORPH_OPEN,
    kernel
)

# 크기 저장
height, width = path_mask.shape

# ==========================================================
# 9. 입구 찾기
# ==========================================================

entrances = []

# 위쪽
for x in range(width):

    if path_mask[0, x] == 255:

        entrances.append((x, 0))

# 아래쪽
for x in range(width):

    if path_mask[height-1, x] == 255:

        entrances.append((x, height-1))

# 왼쪽
for y in range(height):

    if path_mask[y, 0] == 255:

        entrances.append((0, y))

# 오른쪽
for y in range(height):

    if path_mask[y, width-1] == 255:

        entrances.append((width-1, y))

print("검출된 픽셀 :", len(entrances))

# ==========================================================
# 10. 입구 위치 표시
# ==========================================================

test = maze.copy()

for x, y in entrances:

    cv2.circle(
        test,
        (x, y),
        2,
        (0, 0, 255),
        -1
    )

# ==========================================================
# 11. 연결된 입구를 하나로 묶기
# ==========================================================

def merge_points(points):

    if len(points) == 0:
        return []

    merged = []

    visited = [False] * len(points)

    for i in range(len(points)):

        if visited[i]:
            continue

        group = [points[i]]
        visited[i] = True

        changed = True

        while changed:

            changed = False

            for j in range(len(points)):

                if visited[j]:
                    continue

                for gx, gy in group:

                    px, py = points[j]

                    # 서로 붙어있는 픽셀이면 같은 그룹
                    if abs(gx - px) <= 1 and abs(gy - py) <= 1:

                        group.append(points[j])
                        visited[j] = True
                        changed = True
                        break

        xs = [p[0] for p in group]
        ys = [p[1] for p in group]

        merged.append(
            (
                int(np.mean(xs)),
                int(np.mean(ys))
            )
        )

    return merged


entrances = merge_points(entrances)

print()

print("입구 개수 :", len(entrances))

print(entrances)

# ==========================================================
# 12. 시작점 / 도착점
# ==========================================================

if len(entrances) != 2:

    print("입구를 정확히 찾지 못했습니다.")

    exit()

start = entrances[0]
goal = entrances[1]

print()

print("시작 :", start)
print("도착 :", goal)

# ==========================================================
# 13. BFS
# ==========================================================

def bfs(mask, start, goal):

    queue = deque([start])

    visited = np.zeros(mask.shape, dtype=np.uint8)

    visited[start[1], start[0]] = 1

    parent = {}

    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]

    while queue:

        x, y = queue.popleft()

        if (x, y) == goal:

            path = []

            current = goal

            while current != start:

                path.append(current)

                current = parent[current]

            path.append(start)

            path.reverse()

            return path

        for i in range(4):

            nx = x + dx[i]
            ny = y + dy[i]

            if nx < 0 or ny < 0:
                continue

            if nx >= mask.shape[1] or ny >= mask.shape[0]:
                continue

            if visited[ny, nx]:
                continue

            # 흰색이면 이동 가능
            if mask[ny, nx] == 255:

                visited[ny, nx] = 1

                parent[(nx, ny)] = (x, y)

                queue.append((nx, ny))

    return []

# ==========================================================
# 14. BFS 실행
# ==========================================================

path = bfs(path_mask, start, goal)

if len(path) == 0:

    print("경로를 찾지 못했습니다.")

    exit()

print()

print("최단 이동 횟수 :", len(path) - 1)

# ==========================================================
# 15. 결과 이미지
# ==========================================================

result = maze.copy()

for x, y in path:

    cv2.circle(
        result,
        (x, y),
        1,
        (0, 0, 255),
        -1
    )

# 시작점
cv2.circle(
    result,
    start,
    5,
    (0, 255, 0),
    -1
)

# 도착점
cv2.circle(
    result,
    goal,
    5,
    (255, 0, 0),
    -1
)

cv2.imwrite("result.png", result)

cv2.imshow("BFS Result", result)

cv2.waitKey(0)

cv2.destroyAllWindows()