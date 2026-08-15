a, b = map(int, input().split())

if a == 0 or b == 0:
    print("불가능")
else:
    print(a + b)
    print(a - b)
    print(a * b)
    print(a // b)
