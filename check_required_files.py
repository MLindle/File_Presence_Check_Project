import requests
import sys

owner = "MLindle"
repo = "File_Presence_Check_Project"
branch = "main"
files_to_check = ["READE.md", ".gtignore"]

for file_path in files_to_check:

    url = f"https://api.github.com/repos/{owner}/File_Presence_Check_Project/contents/{file_path}?ref={branch}"
    response = requests.get(url)

    if response.status_code != 200:
    
        print (file_path, "not found.")
        missing_file_found = True

if missing_file_found == True:

    print ("One or more missing files detected. Exiting.")
    sys.exit(1)

#Adding comment for test