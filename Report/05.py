def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)


def rotate_array(arr, k, right=True):
    n = len(arr)
    k = k % n
    if k == 0:
        return arr

    shift = gcd(n, k)

    for i in range(shift):
        temp = arr[i]
        j = i

        while True:
            d = (j - k + n) % n
            if d == i:
                break
            arr[j] = arr[d]
            j = d
        arr[j] = temp

    return arr
