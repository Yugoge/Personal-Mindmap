import requests
import os
import json

# ✅ 你的 Notion API Key
NOTION_API_KEY = "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"

# ✅ 你的 Notion 数据库 ID
DATABASE_IDS = {
    "Area": "185bdd3556c2817db031cd1968322da2",
    "Target": "185bdd3556c281c0aa62e144d27e84d0",
    "Project": "185bdd3556c281779e79dabe472407a1",
    "Task": "185bdd3556c281499a2cc84e2144fd2c",
    "Dashboard": "185bdd3556c2819ab6d3ec98eb28d44c"
}
CODE_BLOCK_ID = '1a0bdd35-56c2-81cc-ac2e-e050d6c67e50'

# ✅ Notion API Headers
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ✅ 获取 Notion 数据库中的所有条目
def fetch_database_items(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=HEADERS)
    return response.json().get("results", [])

# ✅ 获取所有层级数据
area_data = fetch_database_items(DATABASE_IDS["Area"])
target_data = fetch_database_items(DATABASE_IDS["Target"])
project_data = fetch_database_items(DATABASE_IDS["Project"])
task_data = fetch_database_items(DATABASE_IDS["Task"])

# ✅ 创建一个映射存储层级关系
area_map = {}  # 存储 Area -> Target
target_map = {}  # 存储 Target -> Project
project_map = {}  # 存储 Project -> Task
notion_links = {}  # 存储每个元素的 Notion 链接

# ✅ 解析 Notion 数据库条目
def parse_notion_data(data, parent_map, parent_field):
    for item in data:
        item_id = item["id"].replace("-", "")[-4:]  # 移除 ID 中的破折号
        try:
            name = item["properties"]["Name"]["title"][0]["text"]["content"]
        except:
            name = item["properties"]["Name"]["title"][0]['mention']['date']['start'] + item["properties"]["Name"]["title"][1]["text"]["content"]
        notion_links[item_id] = item["url"]  # 存储 Notion 页面链接

        # 获取 Parent 关联项
        parent_id = None
        if item["properties"].get(parent_field) and item["properties"][parent_field]["relation"]:
            parent_id = item["properties"][parent_field]["relation"][0]["id"].replace("-", "")[-4:]  # 移除 ID 中的破折号

        # 记录层级关系
        if parent_id:
            if parent_id not in parent_map:
                parent_map[parent_id] = []
            parent_map[parent_id].append((item_id, name))

# ✅ 解析各个层级的关系
parse_notion_data(target_data, area_map, "Area")
parse_notion_data(project_data, target_map, "Target")
parse_notion_data(task_data, project_map, "Project")
mapping = {str(area_map): target_map, str(target_map): project_map}

# ✅ 生成 Mermaid.js 代码
mermaid_code = "flowchart LR\n"

# 🔹 递归构建树状结构
def build_mermaid_graph(parent_id, parent_name, child_map, indent=1):
    global mermaid_code
    if parent_id in child_map:
        for child_id, child_name in sorted(child_map[parent_id], key=lambda x: x[1]):
            link = notion_links.get(child_id, "#")  # 获取 Notion 链接
            mermaid_code += f'  {"  " * indent}{parent_id}["{parent_name}"] --> {child_id}["{child_name}"]\n'
            mermaid_code += f'  {"  " * indent}click {child_id} "{link}"\n'
            try:
                build_mermaid_graph(child_id, child_name, mapping[str(child_map)], indent + 1)
            except:
                pass

# 🔹 遍历所有 Areas 并构建树
for area in sorted(area_data, key=lambda x: x["properties"]["Name"]["title"][0]["text"]["content"]):
    area_id = area["id"].replace("-", "")[-4:]  # 移除 ID 中的破折号
    area_name = area["properties"]["Name"]["title"][0]["text"]["content"]
    notion_links[area_id] = area["url"]  # 存储 Area Notion 链接
    mermaid_code += f'  {area_id}["{area_name}"]\n'
    mermaid_code += f'  click {area_id} "{notion_links[area_id]}"\n'
    build_mermaid_graph(area_id, area_name, area_map)

# ✅ 将 Mermaid 代码写入文件
with open("notion_mermaid_diagram.md", "w") as file:
    file.write(f"```mermaid\n{mermaid_code}\n```")

print("✅ Mermaid.js 代码已生成！请查看 notion_mermaid_diagram.md")

# ✅ 读取 Mermaid.js 代码
with open("notion_mermaid_diagram.md", "r") as file:
    mermaid_code = file.read()

# # ✅ 由于 Notion 限制 2000 字符，拆分代码
# def split_text(text, max_length=2000):
#     return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# code_blocks = split_text(mermaid_code, 2000)

# ✅ 发送更新请求（更新已有代码块内容）
payload = {
    "code": {
        "rich_text": [{"type": "text", "text": {"content": mermaid_code}}],
        "language": "mermaid"
    }
}

response = requests.patch(
    f"https://api.notion.com/v1/blocks/{CODE_BLOCK_ID}",
    headers=HEADERS,
    data=json.dumps(payload)
)

if response.status_code == 200:
    print(f"✅ 代码更新成功！")
else:
    print(f"❌ 更新失败:", response.text)