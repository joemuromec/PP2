# The else statement is executed when the if condition (and any elif conditions) evaluate to False.
a = 200
b = 33
if b > a:
  print("b is greater than a")
elif a == b:
  print("a and b are equal")
else:
  print("a is greater than b")
  
# You can also have an else without the elif:
a = 200
b = 33
if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")

# Checking even or odd numbers:
number = 7
if number % 2 == 0:
  print("The number is even")
else:
  print("The number is odd")
  
# You can combine if, elif, and else to create a comprehensive decision-making structure.
# Temperature classifier:
temperature = 22
if temperature > 30:
  print("It's hot outside!")
elif temperature > 20:
  print("It's warm outside")
elif temperature > 10:
  print("It's cool outside")
else:
  print("It's cold outside!")

#Validating user input:
username = "Emil"
if len(username) > 0:
  print(f"Welcome, {username}!")
else:
  print("Error: Username cannot be empty")