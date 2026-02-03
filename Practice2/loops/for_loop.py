# Print each fruit in a fruit list:
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
  
# Loop through the letters in the word "banana":
for x in "banana":
  print(x)
  
# Using the range() function:
for x in range(6):
  print(x)

#Using the start parameter:
for x in range(2, 6):
  print(x)
  
# Increment the sequence with 3 (default is 1):
for x in range(2, 30, 3):
  print(x)

# Print all numbers from 0 to 5, and print a message when the loop has ended:
for x in range(6):
  print(x)
else:
  print("Finally finished!")

# The "inner loop" will be executed one time for each iteration of the "outer loop":

# Print each adjective for every fruit:
adj = ["red", "big", "tasty"]
fruits = ["apple", "banana", "cherry"]
for x in adj:
  for y in fruits:
    print(x, y)

# for loops cannot be empty, but if you for some reason have a for loop with no content, put in the pass statement to avoid getting an error.
for x in [0, 1, 2]:
  pass