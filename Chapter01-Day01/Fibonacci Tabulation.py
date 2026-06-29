def fib_table(n):
    if n <= 2:
        return 1
    
    dp = [0] * (n+1)
    dp[1] = 1
    dp[2] = 1

    for i in range(3, n+1):
        dp[i] = dp[i-1] + dp[i-2]

    return dp[n]

print(fib_table(10))
# 사용할 화폐 단위 (원)
money = [10, 50, 100, 500, 1000, 5000, 10000, 50000]

# 목표 금액 입력
target = int(input("만들 금액(원): "))

# 0이하의 값이 입력된 경우
if target < 0:
    print("금액은 0원 이상 입력해야 합니다.")

else:
    # DP 배열 생성
    dp = [0] * (target + 1)

    # 0원을 만드는 방법은 아무것도 사용하지 않는 1가지
    dp[0] = 1

    # DP 계산
    for m in money:
        for i in range(m, target + 1):
            dp[i] += dp[i - m]

    # 결과 출력
    if dp[target] == 0:
        print(f"{target}원을 만들 수 없습니다.")
    else:
        print(f"{target}원을 만드는 경우의 수는 {dp[target]}가지입니다.")