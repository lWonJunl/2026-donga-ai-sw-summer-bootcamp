# 변수 선언 및 돈의 종류 설정
money = [10, 50, 100, 500, 1000, 5000, 10000, 50000]

def money_cases(n):

    # n이 음수일 때 예외처리
    if n < 0:
        return "금액은 0원 이상 입력해야 합니다."
    
    else:
        # dp (지역)변수 선언 및 리스트 크기 결정
        dp = [0] * (n+1)

        # n == 0 일때 경우의 수 기본값 설정
        dp[0] = 1

        # Tabulation방식으로 돈을 만들 수 있는 경우의 수 계산
        for m in money:
            for i in range(m, n+1):
                dp[i] += dp[i-m]
    
        return dp[n]

print(money_cases(int(input("만들 금액(원): "))))