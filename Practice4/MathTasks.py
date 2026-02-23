import math

# Task 1
def Task1():
    input_degree = int(input())
    res = math.radians(input_degree)
    print(f"Input degree: {input_degree}")
    print(f"Output radian: {res}")

# Task 2
def Task2():
    height = 5
    base1 = 5
    base2 = 6
    area = ((base1 + base2) / 2) * height
    print(f"Height: {height}")
    print(f"Base, first value: {base1}")
    print(f"Base, second value: {base2}")
    print(f"Expected Output: {area}")

# Task 3
def Task3():
    n = int(input("Input number of sides: "))
    s = float(input("Input the length of a side: "))
    area = (n * s**2) / (4 * math.tan(math.pi / n))
    print(f"The area of the polygon is {int(area)}")
    
# Task 4
def Task4():
    l = int(input("Input length of base: "))
    h = int(input("Input length of height: "))
    area = float(l*h)
    print(f"Length of base: {l}")
    print(f"Height of parallelogram: {h}")
    print(f"Area of parallelogram: {area}")

    