import requests
import sys
import os, json

owner = "MLindle"
repo = "File_Presence_Check_Project"
branch = "main"
default_files_to_check = ["README.md", ".gitignore"]
custom_files_to_check = []
missing_file_found_default = False
missing_file_found_custom = False
missing_files = []
use_default_files = False
output_files = []

try:
    with open(".required-files.yml", mode="r") as required_files:
        for line in required_files:
                line = " ".join(line.split())
                if not line:
                     continue
                custom_files_to_check.append(line)
           
except FileNotFoundError as e:
    print (e, "Checking for default files.", sep=" ")

    use_default_files = True

    for file_path in default_files_to_check:

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
        response = requests.get(url)

        if response.status_code != 200:
        
            print (file_path, "not found.")
            missing_files.append(file_path)
            missing_file_found_default = True

    if missing_file_found_default == True:

        print ("One or more default files are missing.")

for file_path in custom_files_to_check:

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    response = requests.get(url)

    if response.status_code != 200:
        
        print (file_path, "not found.")
        missing_files.append(file_path)
        missing_file_found_custom = True

if missing_file_found_custom == True:

    print ("One or more custom files are missing.")


output_files = custom_files_to_check if not use_default_files else default_files_to_check

gh_out = os.getenv("GITHUB_OUTPUT")
if gh_out:
    with open (gh_out, "a") as out:
        print(f"required_files_output={json.dumps(output_files)}", file=out)
        print(f"missing_files_output={json.dumps(missing_files)}", file=out)