import os
import sys

def add_line_to_file_idempotently(line, filename):
    with open(filename, "r", encoding="utf-8") as fl:
        contents = fl.read()
    contents_cleaned = contents.replace("\r\n","\n").strip()
    line_ending = "\r\n" if "\r\n" in contents else "\n"
    lines = list(map(lambda x: x.strip(), contents_cleaned.split("\n")))
    if line.strip() in lines:
        return
    if contents.endswith(line_ending):
        contents += f"{line}{line_ending}"
    else:
        contents += f"{line_ending}{line}{line_ending}"
    with open(filename,"w",encoding="utf-8") as fl:
        fl.write(contents)

home_directory = os.path.expanduser("~")

profiles = [".bash_profile",".bash_login",".bashrc",".zshenv",".zprofile",".zshrc",".zlogin"]

# It is okay if the PATH is modified more than once if more than one profile get the new line
# On both windows and unix systems duplicates in PATH are not really a problem
# This way, subtle differences in when profiles are sourced won't matter

if len(sys.argv) != 2:
    print("USAGE:\npython3 add-to-path.py <DIRECTORY ABSOLUTE PATH>")
    exit()

path_to_add = sys.argv[1]

command = f"export PATH=\"$PATH:{path_to_add}\""

for profile in profiles:
    fullpath = os.path.join(home_directory,profile)
    if os.path.isfile(fullpath):
        add_line_to_file_idempotently(command,fullpath)