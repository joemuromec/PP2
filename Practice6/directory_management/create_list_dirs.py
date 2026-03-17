from pathlib import Path

nested_path = Path("project/data/logs")
nested_path.mkdir(parents=True, exist_ok=True)

print(f"Nested directories were created: {nested_path}")

root = Path("project")
print(f"Content of directory {root}")
for item in root.iterdir():
    type_item = "Directory" if item.is_dir() else "File"
    print(f"{type_item}: {item.name}")

data_folder = Path("project/data")
py_files = list(data_folder.glob("*.py"))
print(f"Number of python files: {len(py_files)}")
for file in py_files:
    print(f"- {file.name}")