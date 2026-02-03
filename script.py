from os import system
with open("scheme.txt", "r") as file:
    lines = []
    for i in range(0, 15):
        line = file.readline().rstrip('\n')
        if i == 0 or i == 4 or i == 9:
            lines.append(line)
            system(f"mkdir Practice2\{line}")
            continue
        system(f"echo. > Practice2\{lines[i//5 if i > 4 else i//4]}\{line}")
        
        