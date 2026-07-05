import random

class RealCubeSolver3D:
    U, D, F, B, L, R = 0, 1, 2, 3, 4, 5
    FACE_NAME = ["UP (W)", "DOWN (Y)", "FRONT (G)", "BACK (B)", "LEFT (O)", "RIGHT (R)"]
    COLORS = ["W", "Y", "G", "B", "O", "R"]

    def __init__(self):
        self.reset()
        self.target_cube = [[[color] * 3 for _ in range(3)] for color in self.COLORS]

    def reset(self):
        self.cube = [[[color] * 3 for _ in range(3)] for color in self.COLORS]
        self.secret_scramble = [] # 처음 섞은 공식 박제용 변수

    def _rotate_face_surface(self, face, cw=True):
        if cw:
            self.cube[face] = [list(row) for row in zip(*self.cube[face][::-1])]
        else:
            self.cube[face] = [list(row) for row in zip(*self.cube[face])][::-1]
            self.cube[face] = [row[::-1] for row in self.cube[face]]

    def rotate(self, move):
        if move.endswith("2"):
            base = move[0]
            self.rotate(base)
            self.rotate(base)
            return

        cw = not move.endswith("'")
        base = move[0]
        f_idx = {"U":0, "D":1, "F":2, "B":3, "L":4, "R":5}[base]

        self._rotate_face_surface(f_idx, cw)

        if base == "U":
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
        moves = ["U", "D", "F", "B", "L", "R", "U'", "D'", "F'", "B'", "L'", "R'"]
        self.secret_scramble = [random.choice(moves) for _ in range(count)]
        print(f"🎲 처음 섞은 공식 (백업용): {' '.join(self.secret_scramble)}")
        for m in self.secret_scramble:
            self.rotate(m)

    def is_solved(self):
        return self.cube == self.target_cube

    def heuristic(self):
        misplaced = 0
        for f in range(6):
            for r in range(3):
                for c in range(3):
                    if self.cube[f][r][c] != self.target_cube[f][r][c]:
                        misplaced += 1
        return misplaced / 8.0

    def solve_ida_star(self):
        # IDA* 탐색 시작 전 초기 제한값 설정
        bound = self.heuristic()

        # 현재까지의 이동 경로 저장
        path = []

        # 가능한 회전 목록
        possible_moves = ["U", "D", "F", "B", "L", "R", "U'", "D'", "F'", "B'", "L'", "R'"]

        # 탐색한 상태 수 초기화
        self.nodes_visited = 0

        def search(g, bound):
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
                if path and path[-1].endswith("'") and path[-1][0] == move:
                    continue
                if path and move.endswith("'") and move[0] == path[-1]:
                    continue

                # 현재 큐브 상태 백업
                backup = [
                    [
                        [self.cube[f][r][c] for c in range(3)]
                        for r in range(3)
                    ]
                    for f in range(6)
                ]

                path.append(move)
                self.rotate(move)

                t = search(g + 1, bound)

                if t == "FOUND":
                    return "FOUND"

                if t < min_val:
                    min_val = t

                # 백트래킹
                path.pop()
                self.cube = backup

            return min_val

        # IDA* 반복 탐색
        while True:
            t = search(0, bound)

            if t == "FOUND":
                return path

            if t == float('inf'):
                return None

            bound = t

    def print_cube(self, title="큐브 상태"):
        print("\n" + "=" * 40)
        print(f"{title}")
        print("=" * 40)

        for i in range(6):
            print(f"\n[{self.FACE_NAME[i]}]")
            for row in self.cube[i]:
                print("  " + " ".join(row))

        print("\n" + "=" * 40)

if __name__ == "__main__":
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
        print(f"찾아낸 해법 공식 : {' '.join(solution)}")
        print(f"탐색한 상태 수 : {solver.nodes_visited}개")

        solver.print_cube("풀이 완료 후 큐브 상태")

    else:
        print("풀이를 찾지 못했습니다.")