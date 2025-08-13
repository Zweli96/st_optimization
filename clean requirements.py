with open("requirements.txt", "r") as file:
    lines = file.readlines()

with open("new_requirements.txt", "w") as file:
    for line in lines:
        file.write(line.split("==")[0] + "\n")