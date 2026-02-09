# To create a class, use the keyword class:
class MyClass:
  x = 5

# Now we can use the class named MyClass to create objects:

# Create an object named p1, and print the value of x:
p1 = MyClass()
print(p1.x)

# You can delete objects by using the del keyword:
del p1 # Delete the p1 object:

# You can create multiple objects from the same class:

# Create three objects from the MyClass class:
p1 = MyClass()
p2 = MyClass()
p3 = MyClass()

print(p1.x)
print(p2.x)
print(p3.x)

# class definitions cannot be empty, but if you for some reason have a class definition with no content, 
# put in the pass statement to avoid getting an error.
class Person:
  pass