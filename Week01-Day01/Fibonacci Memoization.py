k = 0

def fib_memo(n, memo=None):
    global k

    if memo is None:
        memo = {}
    
    if n <= 2:
        k += 1
        return 1
    
    if n in memo:
        return memo[n]
    
    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]

print(fib_memo(10))