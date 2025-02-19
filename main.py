import requests
import os

# ✅ 你的 Notion API Key
NOTION_API_KEY = "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"

# ✅ 你的 Notion 数据库 ID
DATABASE_IDS = {
    "Area": "185bdd3556c2817db031cd1968322da2",
    "Target": "185bdd3556c281c0aa62e144d27e84d0",
    "Project": "185bdd3556c281779e79dabe472407a1",
    "Task": "185bdd3556c281499a2cc84e2144fd2c"
}

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
    print("🔹 API 返回状态码:", response.status_code)
    print("🔹 API 返回数据:", response.json())
    return response.json().get("results", [])

# ✅ 获取所有层级数据
area_data = fetch_database_items(DATABASE_IDS["Area"])
target_data = fetch_database_items(DATABASE_IDS["Target"])
project_data = fetch_database_items(DATABASE_IDS["Project"])
task_data = fetch_database_items(DATABASE_IDS["Task"])
print(area_data, target_data, project_data, task_data)

# ✅ 创建一个映射存储层级关系
area_map = {}  # 存储 Area -> Target
target_map = {}  # 存储 Target -> Project
project_map = {}  # 存储 Project -> Task
notion_links = {}  # 存储每个元素的 Notion 链接

# ✅ 解析 Notion 数据库条目
def parse_notion_data(data, parent_map, parent_field):
    for item in data:
        item_id = item["id"]
        name = item["properties"]["Name"]["title"][0]["text"]["content"]
        notion_links[item_id] = item["url"]  # 存储 Notion 页面链接

        # 获取 Parent 关联项
        parent_id = None
        if item["properties"].get(parent_field) and item["properties"][parent_field]["relation"]:
            parent_id = item["properties"][parent_field]["relation"][0]["id"]

        # 记录层级关系
        if parent_id:
            if parent_id not in parent_map:
                parent_map[parent_id] = []
            parent_map[parent_id].append((item_id, name))

# ✅ 解析各个层级的关系
parse_notion_data(target_data, area_map, "Related Area")
parse_notion_data(project_data, target_map, "Related Target")
parse_notion_data(task_data, project_map, "Related Project")

# ✅ 生成 Mermaid.js 代码
mermaid_code = "graph TD;\n"

# 🔹 递归构建树状结构
def build_mermaid_graph(parent_id, child_map, indent=1):
    if parent_id in child_map:
        for child_id, child_name in child_map[parent_id]:
            link = notion_links.get(child_id, "#")  # 获取 Notion 链接
            mermaid_code += f'  {"  " * indent}"{parent_id}" --> "{child_id}"\n'
            mermaid_code += f'  {"  " * indent}click "{child_id}" "{link}"\n'
            build_mermaid_graph(child_id, child_map, indent + 1)

# 🔹 遍历所有 Areas 并构建树
for area in area_data:
    area_id = area["id"]
    area_name = area["properties"]["Name"]["title"][0]["text"]["content"]
    notion_links[area_id] = area["url"]  # 存储 Area Notion 链接
    mermaid_code += f'  "{area_id}"["{area_name}"]\n'
    mermaid_code += f'  click "{area_id}" "{notion_links[area_id]}"\n'
    build_mermaid_graph(area_id, area_map)

# ✅ 将 Mermaid 代码写入文件
print(mermaid_code)
with open("notion_mermaid_diagram.md", "w") as file:
    file.write(f"```mermaid\n{mermaid_code}\n```")

print("✅ Mermaid.js 代码已生成！请查看 notion_mermaid_diagram.md")
