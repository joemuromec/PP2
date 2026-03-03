import re

def Task1(text):
    pattern = r"^ab*$"
    if re.search(pattern, text):
        return "Match is found"
    else:
        return "Doesn't match pattern"
    
def Task2(text):
    pattern = r"^ab{2,3}$"
    if re.search(pattern, text):
        return "Match is found"
    else:
        return "Doesn't match pattern"
    
def Task3(text):
    pattern = r"[a-z]+_[a-z]+"
    results = re.findall(pattern, text)
    if results:
        return f"Found: {results}"
    else:
        return "Didn't found anything"

def Task4(text):
    pattern = r"^[A-Z][a-z]+"
    matches = re.findall(pattern, text)
    return matches

def Task5(text):
    pattern = r"^a.*b$"
    if re.fullmatch(pattern, text):
        return f"{text} matches pattern"
    else:
        return f"{text} does NOT matches pattern\n"

def Task6(text):
    pattern = r"[ ,.]"
    result = re.sub(pattern, ":", text)
    return result

def Task7(text):
    pattern = r"_([a-z])"
    result = re.sub(pattern, lambda match: match.group(1).upper(), text)
    return result

def Task8(text):
    pattern = r"(?=[A-Z])"
    result = re.split(pattern, text)
    return [word for word in result if word]

def Task9(text):
    pattern = r"(\w)([A-Z])"
    result = re.sub(pattern, r"\1 \2", text)
    return result

def Task10(text):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()

print("Task 1")
print(f"ab: {Task1('ab')}")    
print(f"abbb: {Task1('abbb')}\n")
print("Task 2")
print(f"abbb: {Task2("abbb")}")  
print(f"abbbb: {Task2("abbbb")}\n") 
test_str = "snake_case example"
print("Task 3")
print(f"{Task3(test_str)}\n")
print("Task 4")
test_text = "Yesterday Ivan bought an Apple and went to London. It was great!"
print(f"Words that were found: {Task4(test_text)}\n")
print("Task 5")
print(Task5("ab"))
print(Task5(f"amazing_python_job"))
print("Task 6")
test_str = "Python Exercises, Java.C++"
print(f"Before: {test_str}")
print(f"After: {Task6(test_str)}\n")
print("Task 7")
test_str = "python_exercises_solution"
print(f"Snake: {test_str}")
print(f"Camel: {Task7(test_str)}\n")
print("Task 8")
test_str = "PythonExercisesSolution"
print(f"String: {test_str}")
print(f"List: {Task8(test_str)}\n")
print("Task 9")
test_str = "PythonExercisesSolution"
print(f"Before: {test_str}")
print(f"After: {Task9(test_str)}\n")
print("Task 10")
test_str = "PythonExercisesSolution"
print(f"Camel: {test_str}")
print(f"Snake: {Task10(test_str)}")
# Результат: python_exercises_solution
print(f"Test 2: {Task10('MyVariable123WithHTTP')}")
# Результат: my_variable123_with_http