x = 5
print(x > 3 and x < 10)
# returns True because 5 is greater than 3 AND 5 is less than 10

x = 5
print(x > 3 or x < 4)
# returns True because one of the conditions are true (5 is greater than 3, but 5 is not less than 4)

x = 5
print(not(x > 3 and x < 10))
# returns False because not is used to reverse the result

# Test if a number is greater than 0 and less than 10:
x = 5
print(x > 0 and x < 10) #Returns True

# Test if a number is less than 5 or greater than 10:
x = 5
print(x < 5 or x > 10) #Returns False

# Reverse the result with not:
x = 5
print(not(x > 3 and x < 10)) #Returns False

