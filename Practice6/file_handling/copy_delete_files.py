import shutil
import os

shutil.copy("sample_data.txt", "sample_backup.txt")
print("Backup file was created: sample_backup.txt")

if os.path.exists("sample_data.txt"):
    os.remove("sample_data.txt")
    print("File sample_data.txt was deleted succesfully")
else:
    print("The file does not exist")