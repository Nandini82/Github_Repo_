from flask import Flask, render_template, request
from github import Github
import os
import pandas as pd
import shutil

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
#/home/Nandini82/mysite/
@app.route('/', methods=['POST'])
def process():
    username = request.form['username']
    accesstoken="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"
    # Call your function here passing the username
    a, b = git(accesstoken, username)
    return render_template('index.html', result=a, link=b)

def git(accesstoken, username):
    g = Github(accesstoken)
    repos = fetch_user_repositories(username, accesstoken)
    directory ="./"  # Replace with the desired directory path
    ext = (".py", ".java", ".cpp", ".ipynb", ".md", ".json", ".js", ".html", ".css", ".htm", ".jar")
    columns = ["Name", "star", "forks", "repo_link"] + list(ext)
    df = pd.DataFrame(columns=columns)

    for repo_name in repos:
        try:
            repo = g.get_repo(f"{username}/{repo_name}")
            repo_path = os.path.join(directory, repo_name)
            repo_url = f"https://github.com/{username}/{repo_name}"
            
            if os.path.exists(repo_path):
               shutil.rmtree(repo_path)
               
            os.mkdir(repo_path)
            languages = {ext: 0 for ext in ext}

            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith(ext):
                        try:
                            language = file.split(".")[-1]
                            with open(file_path, "r", encoding="utf-8") as f:
                                lines = f.readlines()
                                loc = sum(1 for line in lines if line.strip())
                                languages[language] += loc
                        except Exception as e:
                            print(f"Error processing file: {file_path}")
                            print(f"Error message: {str(e)}")

            new_languages = {
                "Name": repo_name,
                "star": repo.stargazers_count,
                "forks": repo.forks_count,
                "repo_link": repo_url,
                **languages
            }
            
            shutil.rmtree(repo_path)
            df_dict = pd.DataFrame([new_languages], columns=columns)
            df = pd.concat([df, df_dict], ignore_index=True)

        except Exception as e:
            print(f"Error fetching repository {username}/{repo_name}: {str(e)}")
            continue

    sort_columns = list(ext) #+ ["forks", "star"]
    df_sorted = df.sort_values(by=sort_columns) 
    return df_sorted.iloc[-1]['Name'], df_sorted.iloc[-1]['repo_link']


def fetch_user_repositories(username, accesstoken):
    try:
        g = Github(accesstoken)
        user = g.get_user(username)
        repositories = user.get_repos()
        return [repo.name for repo in repositories]
    except Exception as e:
        print("Error fetching repositories:", e)
        return []

if __name__ == '__main__':
    app.run()
