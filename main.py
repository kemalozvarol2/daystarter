from simplegmail import Gmail
from simplegmail.query import construct_query
import json, requests, os

# You can generate the API key for free, and we are using a free model,
# (deepseek-chat:free) in this script, so you won't be charged anything even if you have
# balance on openrouter website.

# You can switch to another model by changing the "model" value on line 39.

DEEPSEEK_API_KEY = "openrouter.ai api key here"

# 1. Create a project from Google developer (now cloud) console
# 2. Add gmail API access to your project
# 3. Add your email as test user to the project
# 4. Download API credentials and put it in the same directory as this file
#    and name it "credentials.json"
#
# If this was too complicated, see this video : youtu.be/NQ6s4JFhGcc


credentials_file = "./credentials.json"

gmail = Gmail(client_secret_file=credentials_file)


def askAI(question):
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer " + DEEPSEEK_API_KEY,
        "Content-Type": "application/json",
    },
    data=json.dumps({

        # You can also use "deepseek/deepseek-r1:free"
        # I'm using this because this one's faster.

        "model": "deepseek/deepseek-chat:free",
        "messages": [
        {
            "role": "user",
            "content": question
        }
        ],        
    })
    )

    resp = response.json()
    content = resp["choices"][0]["message"]["content"]

    return content



query_params = {
    "newer_than": (1, "day"),
    "unread": True
}

messages = gmail.get_unread_inbox(query=construct_query(query_params))

todaysEmails = []

for message in messages:
    todaysEmails.append({
        "Subject": message.subject,
        "From": message.sender,
        "Date": message.date
    })


# Below is the prompt for Deepseek AI, 
# feel free to change it to fit your needs

# But make sure it returns a list of p tags 
# so the index.html renders properly.

prompt = "Can you take a look at my emails below and summarize them for me? Mention each of the 'important ones' in a short paragraph. And don't even mention spam, promotional stuff and newsletters. Don't use markdown, use html tags like 'p', 'strong' and 'br' when necessary.\n"
prompt += json.dumps(todaysEmails)

response = askAI(prompt)

with open('partials/head.html') as head:
    site_head = head.read()
    
with open('partials/foot.html') as foot:
    site_foot = foot.read()

with open("index.html", "w") as file:
    file.write(site_head + response + site_foot)

# This part is optional, you can remove the line below if you
# don't want to view the page immediately after it's created.
# Or you can change "firefox" with chrome or whatever browser you want to use.
# Just remember to leave a space after it.

os.system("firefox " + os.getcwd() + "/index.html")
