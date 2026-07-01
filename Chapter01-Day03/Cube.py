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
        print("\n==================================================")
        print("⚙️ [연산 과정 시작] IDA* 알고리즘 트리 탐색 실시간 추적")
        print("==================================================")
        
        bound = self.heuristic()
        path = []
        possible_moves = ["U", "D", "F", "B", "L", "R", "U'", "D'", "F'", "B'", "L'", "R'"]
        self.nodes_visited = 0

        def search(g, bound):
            self.nodes_visited += 1
            h = self.heuristic()
            f = g + h
            
            current_formula = " -> ".join(path) if path else "시작 상태"
            print(f"🔍 [노드 #{self.nodes_visited:04d}] 깊이(g): {g} | 예상치(h): {h:.2f} | 총비용(f): {f:.2f} (제한선: {bound:.2f})")
            print(f"   ┗ 🛠️ 테스트 중인 무브 공식: [ {current_formula} ]")

            if f > bound: 
                print(f"   ┗ ❌ [가지치기] 예상 비용이 제한선을 초과하여 이 탐색줄기는 종료합니다.\n")
                return f
            if self.is_solved(): 
                print(f"\n🎯 [탐색 대성공!] {self.nodes_visited}번째 상태 검사에서 해법을 발견했습니다.")
                return "FOUND"
            
            min_val = float('inf')
            for move in possible_moves:
                if path and path[-1].endswith("'") and path[-1][0] == move: continue
                if path and move.endswith("'") and move[0] == path[-1]: continue

                backup = [[[self.cube[f][r][c] for c in range(3)] for r in range(3)] for f in range(6)]
                
                path.append(move)
                self.rotate(move)
                
                t = search(g + 1, bound)
                if t == "FOUND": return "FOUND"
                if t < min_val: min_val = t
                
                path.pop()
                self.cube = backup
                
            return min_val

        while True:
            print(f"\n📈 [한계 깊이 확장] 허용 비용 한계치를 {bound:.2f}회 회전으로 설정 후 전면 재탐색")
            t = search(0, bound)
            if t == "FOUND": return path
            if t == float('inf'): return None
            bound = t

    def print_cube(self):
        print("-" * 30)
        for i in range(6):
            print(f"====================\n{self.FACE_NAME[i]}")
            for row in self.cube[i]:
                print(" ".join(row))
        print("-" * 30)


if __name__ == "__main__":
    solver = RealCubeSolver3D()
    
    solver.scramble(3) # 연산이 너무 길어지지 않게 우선 3번 믹스
    print("\n[🔍 섞인 직후 최초 큐브 상태]")
    solver.print_cube()
    
    # 순수 현재 상태만 보고 길 찾기 연산 가동 (로그 폭발 영역)
    solution = solver.solve_ida_star()
    
    # 최종 결과 리포트 출력 (이 부분은 위로 밀려나지 않고 맨 아래 박제됩니다)
    print("\n" + "="*50)
    print("📊 [최종 결과 분석 보고서]")
    print("="*50)
    print(f"🎲 1. 처음에 섞은 공식 (밀림 방지 박제) : {' '.join(solver.secret_scramble)}")
    if solution is not None:
        print(f"🎉 2. AI가 찾아낸 독자 해법 공식    : {' '.join(solution)}")
        print(f"🧮 3. 목적지 도달까지 총 연산 상태 수 : {solver.nodes_visited}개")
        print("\n[✨ 솔버 작동 완료 후 최종 큐브 상태]")
        solver.print_cube()
    else:
        print("❌ 풀이를 찾지 못했습니다.")