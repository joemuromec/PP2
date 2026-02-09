# Functions can return values using the return statement:
def my_function(x, y):
  return x + y

result = my_function(5, 3)
print(result)

# A function that returns a list:
def my_function():
  return ["apple", "banana", "cherry"]

fruits = my_function()
print(fruits[0])
print(fruits[1])
print(fruits[2])

# A function that returns a tuple:
def my_function():
  return (10, 20)

x, y = my_function()
print("x:", x)
print("y:", y)

# To specify positional-only arguments, add , / after the arguments:
def my_function(name, /):
  print("Hello", name)

my_function("Emil")

# To specify that a function can have only keyword arguments, add *, before the arguments:
def my_function(*, name):
  print("Hello", name)

my_function(name = "Emil")

# You can combine both argument types in the same function.
# Arguments before / are positional-only, and arguments after * are keyword-only:
def my_function(a, b, /, *, c, d):
  return a + b + c + d

result = my_function(5, 10, c = 15, d = 20)
print(result)