names = ["Bob", "John", "Joe"]
scores = [85, 92, 78]
print("Student list:")
for index, name in enumerate(names, start=1):
    print(f"{index}. {name}")

print("\nScores")
for name, score in zip(names, scores):
    print(f"{name} got {score} points")

data = "100"

if isinstance(data, str):
    print(f"'{data}' is a string. Converting...")

number = int(data)
price = float(number)

print(f"Integer: {number}, Float: {price}")

mixed_list = [1, "apple", 3.14, True]
types = [type(item).__name__ for item in mixed_list]
print(f"Types in list: {types}")