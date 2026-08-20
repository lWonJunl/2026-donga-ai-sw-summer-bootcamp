def fib_recursive(n):
    if n <= 2:
        return 1
    
    return fib_recursive(n-1) + fib_recursive(n-2)

print(fib_recursive(10))