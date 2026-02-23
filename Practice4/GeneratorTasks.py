# Task 1
def Task1():
    def generator(N):
        for i in range(1, N+1):
            yield i * i
    N = int(input())
    for i in generator(N):
        print(i)

# Task 2
def Task2():
    def even_numbers(N):
        for i in range(0, N + 1, 2):
            yield i
    N = int(input())
    print(",".join(map(str, even_numbers(N))))

# Task 3
def Task3():
    def generator(N):
        for i in range(0, N+1):
                if i % 3 == 0 and i % 4 == 0:
                    yield i
    N = int(input())
    for i in generator(N):
        print(i, end= " ")

# Task 4
def Task4():
    def generator(a, b):
        for i in range(a, b+1):
            yield i * i
    a, b = [int(i) for i in input().split()]
    for i in generator(a, b):
        print(i)

# Task 5
def Task5():
    def generator(n):
        for i in range(n, -1, -1):
            yield i
    n = int(input())
    for i in generator(n):
        print(i)