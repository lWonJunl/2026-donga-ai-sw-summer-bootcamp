k = 0 # 연산 횟수 추가를 위한 변수

def coin_change(n, coins):
    count = 0
    for coin in coins:
        global k

        # (Greedy Algorithm 적용)
        count += (n//coin)
        n %= coin

        # 연산 횟수 추가
        k += 2

        # 연산 로그 기록
        print("Count : " + str(n) + " // " + str(coin)+ " = " + str(count) + "   Coin : " + str(n) + " %= " + str(coin) + " = " + str(coin))
        print("<" + str(k) + ">" + " --------------------------------------------")

    return count

coins = [500, 400, 100]
n = 1260
print(coin_change(800, coins))