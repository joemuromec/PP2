# A function with one argument:
def my_function(fname):
  print(fname + " Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")

def my_function(name): # name is a parameter
  print("Hello", name)

my_function("Emil") # "Emil" is an argument

# This function expects 2 arguments, and gets 2 arguments::
def my_function(fname, lname):
  print(fname + " " + lname)

my_function("Emil", "Refsnes")

# If you try to call the function with the wrong number of arguments, you will get an error

# You can assign default values to parameters:
def my_function(name = "friend"):
  print("Hello", name)

my_function("Emil")
my_function("Tobias")
my_function()
my_function("Linus")

# Default value for country parameter:
def my_function(country = "Norway"):
  print("I am from", country)

my_function("Sweden")
my_function("India")
my_function()
my_function("Brazil")

# You can send arguments with the key = value syntax:
def my_function(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)

my_function(animal = "dog", name = "Buddy")

# This way, with keyword arguments, the order of the arguments does not matter:
my_function(name = "Buddy", animal = "dog")

# When you call a function with arguments without using keywords, they are called positional arguments:
def my_function(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)

my_function("dog", "Buddy")

# The order matters with positional arguments. Switching the order changes the result:
my_function("Buddy", "dog")

# You can mix positional and keyword arguments in a function call. 
# However, positional arguments must come before keyword arguments:
def my_function(animal, name, age):
  print("I have a", age, "year old", animal, "named", name)

my_function("dog", name = "Buddy", age = 5)

# Sending a list as an argument:
def my_function(fruits):
  for fruit in fruits:
    print(fruit)

my_fruits = ["apple", "banana", "cherry"]
my_function(my_fruits)

# Sending a dictionary as an argument:
def my_function(person):
  print("Name:", person["name"])
  print("Age:", person["age"])

my_person = {"name": "Emil", "age": 25}
my_function(my_person)

