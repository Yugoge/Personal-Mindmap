import requests
import os

NOTION_API_KEY = os.getenv("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")
DATABASE_ID = os.getenv("185bdd3556c281afa4b2000c96fa09b3&pvs=4")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

response = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query", headers=headers)
data = response.json()

mermaid_code = "graph TD;\n"

for item in data["results"]:
    name = item["properties"]["Name"]["title"][0]["text"]["content"]
    type = item["properties"]["Type"]["select"]["name"]
    parent = item["properties"]["Parent"]["relation"][0]["id"] if item["properties"]["Parent"]["relation"] else None
    notion_url = item["url"]

    if parent:
        mermaid_code += f'  "{parent}" --> "{name}"\n'
    else:
        mermaid_code += f'  "{name}"\n'

    # 添加 Notion 页面超链接
    mermaid_code += f'  click "{name}" "{notion_url}"\n'

# 将 Mermaid 代码写入 README.md 或其他 Notion 页面
with open("mermaid_diagram.md", "w") as file:
    file.write(f"```mermaid\n{mermaid_code}\n```")

print("Mermaid.js Diagram updated!")
