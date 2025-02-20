import requests
import json

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

# ✅ 获取 Notion 数据库中的所有条目（处理分页）
def fetch_database_items(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    all_items = []
    has_more = True
    next_cursor = None
    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()
        all_items.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")
    return all_items

# ✅ 获取所有层级数据
area_data = fetch_database_items(DATABASE_IDS["Area"])
target_data = fetch_database_items(DATABASE_IDS["Target"])
project_data = fetch_database_items(DATABASE_IDS["Project"])
task_data = fetch_database_items(DATABASE_IDS["Task"])

# ✅ 创建映射存储层级关系
area_map = {}  # Area -> Target
target_map = {}  # Target -> Project
project_map = {}  # Project -> Task
notion_links = {}  # 存储每个元素的 Notion 链接

# ✅ 解析 Notion 数据库条目
def parse_notion_data(data, parent_map, parent_field):
    for item in data:
        item_id = item["id"]
        # 提取名称
        name_prop = item["properties"]["Name"]["title"]
        if name_prop and len(name_prop) > 0:
            if "text" in name_prop[0]:
                name = name_prop[0]["text"]["content"]
            elif "mention" in name_prop[0]:
                name = name_prop[0]["mention"]["date"]["start"]
            else:
                name = "Unnamed"
        else:
            name = "Unnamed"
        notion_links[item_id] = item["url"]

        # 获取 Parent 关联项
        parent_id = None
        parent_relation = item["properties"].get(parent_field, {}).get("relation", [])
        if parent_relation:
            parent_id = parent_relation[0]["id"]

        # 记录层级关系
        if parent_id:
            if parent_id not in parent_map:
                parent_map[parent_id] = []
            parent_map[parent_id].append((item_id, name))

# ✅ 解析各个层级的关系
parse_notion_data(target_data, area_map, "Area")
parse_notion_data(project_data, target_map, "Target")
parse_notion_data(task_data, project_map, "Project")

# ✅ 生成 Mermaid.js 代码
mermaid_code = "graph TD;\n"
nodes_defined = set()  # 跟踪已定义的节点

# 🔹 递归构建树状结构
def build_mermaid_graph(parent_id, parent_name, current_map, indent=1):
    global mermaid_code, nodes_defined
    if parent_id not in current_map:
        return
    
    # 对子项按名称排序
    children = sorted(current_map[parent_id], key=lambda x: x[1])
    
    for child_id, child_name in children:
        # 定义子节点（如果未定义过）
        if child_id not in nodes_defined:
            mermaid_code += f'  {"  " * indent}{child_id}["{child_name}"]\n'
            mermaid_code += f'  {"  " * indent}click {child_id} "{notion_links[child_id]}"\n'
            nodes_defined.add(child_id)
        
        # 添加连接
        mermaid_code += f'  {"  " * indent}{parent_id} --> {child_id}\n'
        
        # 确定下一层的映射
        if current_map == area_map:
            next_map = target_map
        elif current_map == target_map:
            next_map = project_map
        elif current_map == project_map:
            next_map = task_map
        else:
            next_map = None
        
        # 递归处理下一层
        if next_map is not None:
            build_mermaid_graph(child_id, child_name, next_map, indent + 1)

# 🔹 遍历所有 Areas 并构建树
for area in sorted(area_data, key=lambda x: x["properties"]["Name"]["title"][0].get("text", {}).get("content", "")):
    area_id = area["id"]
    area_name = area["properties"]["Name"]["title"][0].get("text", {}).get("content", "Unnamed Area")
    # 定义Area节点
    if area_id not in nodes_defined:
        mermaid_code += f'  {area_id}["{area_name}"]\n'
        mermaid_code += f'  click {area_id} "{notion_links[area_id]}"\n'
        nodes_defined.add(area_id)
    # 构建子树
    build_mermaid_graph(area_id, area_name, area_map)

# ✅ 将 Mermaid 代码写入文件
with open("notion_mermaid_diagram.md", "w", encoding="utf-8") as file:
    file.write(f"```mermaid\n{mermaid_code}\n```")

print("✅ Mermaid.js 代码已生成！请查看 notion_mermaid_diagram.md")