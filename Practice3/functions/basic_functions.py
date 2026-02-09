# This creates a function named my_function that prints "Hello from a function" when called.
def my_function():
  print("Hello from a function")
# To call a function, write its name followed by parentheses:
my_function()
# You can call the same function multiple times:
my_function()
my_function()
my_function()

# Valid function names:
# calculate_sum()
# _private_function()
# myFunction2()

# With functions - reusable code:
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))

# A function that returns a value:
def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)

# Using the return value directly:
def get_greeting():
  return "Hello from a function"

print(get_greeting())

# If you need to create a function placeholder without any code, use the pass statement:
def my_function():
  pass