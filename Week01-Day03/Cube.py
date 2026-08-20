import random

class RealCubeSolver3D:
    # 큐브의 6개 면을 숫자로 관리한다.
    # self.cube[0]은 윗면, self.cube[1]은 아랫면처럼 접근할 수 있다.
    # 숫자를 직접 쓰는 것보다 self.U, self.D처럼 이름을 붙이면 코드가 훨씬 읽기 쉽다.
    U, D, F, B, L, R = 0, 1, 2, 3, 4, 5

    # 출력할 때 각 면의 이름을 보여주기 위한 목록이다.
    # COLORS와 같은 순서를 유지해야 한다.
    FACE_NAME = ["UP (W)", "DOWN (Y)", "FRONT (G)", "BACK (B)", "LEFT (O)", "RIGHT (R)"]

    # 각 면의 완성 상태 색상이다.
    # W: 흰색, Y: 노란색, G: 초록색, B: 파란색, O: 주황색, R: 빨간색
    COLORS = ["W", "Y", "G", "B", "O", "R"]

    def __init__(self):
        # 객체를 만들자마자 큐브를 완성 상태로 초기화한다.
        self.reset()

        # target_cube는 정답 큐브 상태다.
        # 예: target_cube[0]은 W가 3x3으로 채워진 윗면이다.
        # 이후 is_solved()에서 현재 큐브와 target_cube를 비교한다.
        self.target_cube = [[[color] * 3 for _ in range(3)] for color in self.COLORS]

    def reset(self):
        # cube는 3차원 리스트로 저장한다.
        # 구조: self.cube[면 번호][행 번호][열 번호]
        # 예: self.cube[self.F][0][2]는 앞면의 0번째 행, 2번째 열 칸이다.
        self.cube = [[[color] * 3 for _ in range(3)] for color in self.COLORS]
        
        # scramble()로 무작위 섞기를 할 때 사용한 회전 공식을 저장한다.
        # 마지막 결과 출력에서 "처음 섞은 공식"을 보여주기 위해 필요하다.
        self.secret_scramble = [] # 처음 섞은 공식 박제용 변수

    def _rotate_face_surface(self, face, cw=True):
        # 한 면 자체의 3x3 스티커를 회전시키는 함수다.
        # 주의: 이 함수는 해당 면의 표면만 돌린다.
        # 주변 면의 줄/열 이동은 rotate()에서 따로 처리한다.
        if cw:
            # 시계 방향 90도 회전
            # 1. self.cube[face][::-1]로 행 순서를 뒤집는다.
            # 2. zip(*)으로 행과 열을 바꾼다.
            # 결과적으로 3x3 배열이 시계 방향으로 회전한다.
            self.cube[face] = [list(row) for row in zip(*self.cube[face][::-1])]
        else:
            # 반시계 방향 90도 회전
            # zip(*)으로 행과 열을 바꾼 뒤, 필요한 방향으로 다시 뒤집는다.
            self.cube[face] = [list(row) for row in zip(*self.cube[face])][::-1]
            self.cube[face] = [row[::-1] for row in self.cube[face]]

    def rotate(self, move):
        # move는 "U", "D'", "F2" 같은 회전 명령이다.
        # U  : 윗면을 시계 방향으로 90도 회전
        # U' : 윗면을 반시계 방향으로 90도 회전
        # U2 : 윗면을 180도 회전
        if move.endswith("2"):
            # 180도 회전은 같은 방향 90도 회전을 두 번 하면 된다.
            base = move[0]
            self.rotate(base)
            self.rotate(base)
            return

        # 작은따옴표가 붙어 있으면 반시계 방향, 없으면 시계 방향으로 본다.
        cw = not move.endswith("'")

        # 회전할 면의 문자만 꺼낸다.
        # 예: "R'"에서 base는 "R"이다.
        base = move[0]

        # 문자로 들어온 면 이름을 실제 리스트 인덱스로 바꾼다.
        f_idx = {"U":0, "D":1, "F":2, "B":3, "L":4, "R":5}[base]

        # 먼저 선택한 면의 표면 3x3을 회전시킨다.
        self._rotate_face_surface(f_idx, cw)

        # 아래부터는 회전한 면 주변의 행/열을 서로 이동시키는 부분이다.
        # 루빅스 큐브에서 한 면을 돌리면 그 면만 도는 것이 아니라,
        # 인접한 4개 면의 가장자리 줄도 함께 이동한다.
        if base == "U":
            # U 회전은 윗면을 돌리는 것이므로,
            # 앞/오른쪽/뒤/왼쪽 면의 맨 윗줄이 서로 교환된다.
            if cw:
                tmp = self.cube[self.F][0][:]
                self.cube[self.F][0] = self.cube[self.R][0][:]
                self.cube[self.R][0] = self.cube[self.B][0][:]
                self.cube[self.B][0] = self.cube[self.L][0][:]
                self.cube[self.L][0] = tmp
            else:
                tmp = self.cube[self.F][0][:]
                self.cube[self.F][0] = self.cube[self.L][0][:]
                self.cube[self.L][0] = self.cube[self.B][0][:]
                self.cube[self.B][0] = self.cube[self.R][0][:]
                self.cube[self.R][0] = tmp
        elif base == "D":
            # D 회전은 아랫면을 돌리는 것이므로,
            # 앞/왼쪽/뒤/오른쪽 면의 맨 아랫줄이 서로 교환된다.
            if cw:
                tmp = self.cube[self.F][2][:]
                self.cube[self.F][2] = self.cube[self.L][2][:]
                self.cube[self.L][2] = self.cube[self.B][2][:]
                self.cube[self.B][2] = self.cube[self.R][2][:]
                self.cube[self.R][2] = tmp
            else:
                tmp = self.cube[self.F][2][:]
                self.cube[self.F][2] = self.cube[self.R][2][:]
                self.cube[self.R][2] = self.cube[self.B][2][:]
                self.cube[self.B][2] = self.cube[self.L][2][:]
                self.cube[self.L][2] = tmp
        elif base == "R":
            # R 회전은 오른쪽 면을 돌리는 것이므로,
            # 윗면 오른쪽 열, 뒤면 왼쪽 열, 아랫면 오른쪽 열,
            # 앞면 오른쪽 열이 서로 이동한다.
            # 뒤면은 바라보는 방향이 반대라서 2-i로 순서를 뒤집는 곳이 있다.
            u_col = [self.cube[self.U][i][2] for i in range(3)]
            b_col = [self.cube[self.B][i][0] for i in range(3)]
            d_col = [self.cube[self.D][i][2] for i in range(3)]
            f_col = [self.cube[self.F][i][2] for i in range(3)]
            if cw:
                for i in range(3): self.cube[self.U][i][2] = f_col[i]
                for i in range(3): self.cube[self.B][i][0] = u_col[2-i]
                for i in range(3): self.cube[self.D][i][2] = b_col[2-i]
                for i in range(3): self.cube[self.F][i][2] = d_col[i]
            else:
                for i in range(3): self.cube[self.U][i][2] = b_col[2-i]
                for i in range(3): self.cube[self.B][i][0] = d_col[2-i]
                for i in range(3): self.cube[self.D][i][2] = f_col[i]
                for i in range(3): self.cube[self.F][i][2] = u_col[i]
        elif base == "L":
            # L 회전은 왼쪽 면을 돌리는 것이므로,
            # 윗면 왼쪽 열, 뒤면 오른쪽 열, 아랫면 왼쪽 열,
            # 앞면 왼쪽 열이 서로 이동한다.
            u_col = [self.cube[self.U][i][0] for i in range(3)]
            b_col = [self.cube[self.B][i][2] for i in range(3)]
            d_col = [self.cube[self.D][i][0] for i in range(3)]
            f_col = [self.cube[self.F][i][0] for i in range(3)]
            if cw:
                for i in range(3): self.cube[self.U][i][0] = b_col[2-i]
                for i in range(3): self.cube[self.B][i][2] = d_col[2-i]
                for i in range(3): self.cube[self.D][i][0] = f_col[i]
                for i in range(3): self.cube[self.F][i][0] = u_col[i]
            else:
                for i in range(3): self.cube[self.U][i][0] = f_col[i]
                for i in range(3): self.cube[self.B][i][2] = u_col[2-i]
                for i in range(3): self.cube[self.D][i][0] = b_col[2-i]
                for i in range(3): self.cube[self.F][i][0] = d_col[i]
        elif base == "F":
            # F 회전은 앞면을 돌리는 것이므로,
            # 윗면 아랫줄, 오른쪽 면 왼쪽 열, 아랫면 윗줄,
            # 왼쪽 면 오른쪽 열이 서로 이동한다.
            u_row = self.cube[self.U][2][:]
            r_col = [self.cube[self.R][i][0] for i in range(3)]
            d_row = self.cube[self.D][0][:]
            l_col = [self.cube[self.L][i][2] for i in range(3)]
            if cw:
                for i in range(3): self.cube[self.U][2][i] = l_col[2-i]
                for i in range(3): self.cube[self.R][i][0] = u_row[i]
                for i in range(3): self.cube[self.D][0][i] = r_col[2-i]
                for i in range(3): self.cube[self.L][i][2] = d_row[i]
            else:
                for i in range(3): self.cube[self.U][2][i] = r_col[i]
                for i in range(3): self.cube[self.R][i][0] = d_row[2-i]
                for i in range(3): self.cube[self.D][0][i] = l_col[i]
                for i in range(3): self.cube[self.L][i][2] = u_row[2-i]
        elif base == "B":
            # B 회전은 뒷면을 돌리는 것이므로,
            # 윗면 윗줄, 왼쪽 면 왼쪽 열, 아랫면 아랫줄,
            # 오른쪽 면 오른쪽 열이 서로 이동한다.
            u_row = self.cube[self.U][0][:]
            l_col = [self.cube[self.L][i][0] for i in range(3)]
            d_row = self.cube[self.D][2][:]
            r_col = [self.cube[self.R][i][2] for i in range(3)]
            if cw:
                for i in range(3): self.cube[self.U][0][i] = r_col[i]
                for i in range(3): self.cube[self.L][i][0] = u_row[2-i]
                for i in range(3): self.cube[self.D][2][i] = l_col[i]
                for i in range(3): self.cube[self.R][i][2] = d_row[2-i]
            else:
                for i in range(3): self.cube[self.U][0][i] = l_col[2-i]
                for i in range(3): self.cube[self.L][i][0] = d_row[i]
                for i in range(3): self.cube[self.D][2][i] = r_col[2-i]
                for i in range(3): self.cube[self.R][i][2] = u_row[i]

    def scramble(self, count=3):
        # 큐브를 무작위로 섞는 함수다.
        # count가 3이면 랜덤 회전을 3번 수행한다.
        moves = ["U", "D", "F", "B", "L", "R", "U'", "D'", "F'", "B'", "L'", "R'"]

        # 나중에 어떤 회전으로 섞었는지 확인할 수 있도록 저장한다.
        self.secret_scramble = [random.choice(moves) for _ in range(count)]

        # 저장된 회전들을 실제 큐브에 차례대로 적용한다.
        for m in self.secret_scramble:
            self.rotate(m)

    def is_solved(self):
        # 현재 큐브 상태가 target_cube와 완전히 같으면 완성된 상태다.
        return self.cube == self.target_cube

    def heuristic(self):
        # 휴리스틱 함수는 "정답까지 얼마나 멀어 보이는지"를 대략 계산한다.
        # 여기서는 각 칸이 목표 색상과 다르면 misplaced를 1 증가시킨다.
        # 단순한 휴리스틱이라 정확한 최소 회전 수는 아니지만,
        # IDA*가 아무 정보 없이 탐색하는 것보다는 가지치기에 도움이 된다.
        misplaced = 0
        for f in range(6):
            for r in range(3):
                for c in range(3):
                    if self.cube[f][r][c] != self.target_cube[f][r][c]:
                        misplaced += 1

        # 한 번의 회전으로 여러 스티커가 움직일 수 있으므로 8로 나누어
        # 너무 큰 추정값이 나오지 않게 완화한다.
        return misplaced / 8.0

    def solve_ida_star(self):
        # IDA*는 Iterative Deepening A*의 줄임말이다.
        # 메모리를 많이 쓰는 우선순위 큐 대신 깊이 제한 DFS를 반복한다.
        #
        # g: 지금까지 실제로 움직인 횟수
        # h: 휴리스틱으로 예상한 남은 비용
        # f: g + h, 현재 경로의 예상 총 비용
        # bound: 이번 반복에서 허용할 최대 f값

        # IDA* 탐색 시작 전 초기 제한값 설정
        bound = self.heuristic()

        # 현재까지의 이동 경로 저장
        path = []

        # 가능한 회전 목록
        possible_moves = ["U", "D", "F", "B", "L", "R", "U'", "D'", "F'", "B'", "L'", "R'"]

        # 탐색한 상태 수 초기화
        self.nodes_visited = 0

        def search(g, bound):
            # 내부 재귀 함수다.
            # 현재 큐브 상태에서 가능한 다음 움직임들을 깊이 우선으로 탐색한다.
            self.nodes_visited += 1

            h = self.heuristic()
            f = g + h

            # 제한값을 넘으면 가지치기
            if f > bound:
                return f

            # 큐브가 완성되었으면 성공
            if self.is_solved():
                return "FOUND"

            min_val = float('inf')

            for move in possible_moves:
                # 바로 직전 움직임을 취소하는 불필요한 움직임 제거
                # 예: 방금 U'를 했는데 바로 U를 하면 원래 상태로 돌아가므로 탐색 낭비다.
                if path and path[-1].endswith("'") and path[-1][0] == move:
                    continue
                if path and move.endswith("'") and move[0] == path[-1]:
                    continue

                # 현재 큐브 상태 백업
                # 재귀 탐색에서 move를 적용한 뒤, 다른 move도 시험해야 하므로
                # 탐색이 끝나면 반드시 이전 큐브 상태로 되돌려야 한다.
                backup = [
                    [
                        [self.cube[f][r][c] for c in range(3)]
                        for r in range(3)
                    ]
                    for f in range(6)
                ]

                # 현재 move를 경로에 추가하고 큐브에 실제 적용한다.
                path.append(move)
                self.rotate(move)

                # 한 수를 더 둔 상태에서 재귀적으로 탐색한다.
                t = search(g + 1, bound)

                # 하위 탐색에서 답을 찾았다면 더 볼 필요 없이 성공을 전달한다.
                if t == "FOUND":
                    return "FOUND"

                # 답은 못 찾았지만 bound를 넘은 값들 중 가장 작은 값을 저장한다.
                # 다음 IDA* 반복에서 bound를 이 값으로 늘린다.
                if t < min_val:
                    min_val = t

                # 백트래킹
                path.pop()
                self.cube = backup

            return min_val

        # IDA* 반복 탐색
        while True:
            # 현재 bound 안에서 답을 찾을 수 있는지 DFS 탐색을 수행한다.
            t = search(0, bound)

            if t == "FOUND":
                return path

            if t == float('inf'):
                # 더 이상 확장할 후보가 없으면 해법을 찾지 못한 것이다.
                return None

            # 이번 bound에서는 못 찾았으므로,
            # 다음 반복에서는 가장 작게 초과했던 f값까지 제한을 늘린다.
            bound = t

    def print_cube(self, title="큐브 상태"):
        # 현재 큐브의 6개 면을 사람이 보기 좋게 출력한다.
        print("\n" + "=" * 40)
        print(f"{title}")
        print("=" * 40)

        for i in range(6):
            # i번째 면의 이름을 먼저 출력한다.
            print(f"\n[{self.FACE_NAME[i]}]")

            # 각 면은 3행 3열이므로 행 단위로 출력한다.
            for row in self.cube[i]:
                print("  " + " ".join(row))

        print("\n" + "=" * 40)

if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 아래 코드가 동작한다.
    # 다른 파일에서 import할 때는 실행되지 않는다.
    solver = RealCubeSolver3D()

    # 큐브 섞기
    solver.scramble(3)

    # 섞인 상태 출력
    solver.print_cube("섞인 직후 큐브 상태")

    # 풀이 시작 안내
    print("\n풀이를 탐색하는 중입니다...")

    # IDA* 알고리즘 실행
    solution = solver.solve_ida_star()

    # 최종 결과 출력
    print("\n" + "=" * 50)
    print("최종 결과")
    print("=" * 50)

    print(f"처음 섞은 공식 : {' '.join(solver.secret_scramble)}")

    if solution is not None:
        # 해법을 찾은 경우, 섞은 공식과 찾아낸 해법을 함께 보여준다.
        print(f"찾아낸 해법 공식 : {' '.join(solution)}")
        print(f"탐색한 상태 수 : {solver.nodes_visited}개")

        # solve_ida_star()가 실제로 큐브를 회전시키면서 찾기 때문에,
        # 성공했다면 현재 큐브는 완성 상태가 되어 있어야 한다.
        solver.print_cube("풀이 완료 후 큐브 상태")

    else:
        # 현재 탐색 조건 안에서 해법을 찾지 못한 경우다.
        print("풀이를 찾지 못했습니다.")
