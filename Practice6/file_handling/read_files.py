with open("sample_data.txt", 'r') as f:
    print("Content of file:")
    print(f.read())

with open("sample_data.txt", "a") as f:
    f.write("Now the file has more content!")

with open("sample_data.txt") as f:
    print("Updated content:")
    print(f.read())