import json
import os
import time
from itertools import combinations

debug = 0
# 开场动画
def opening_animation():
    text = '''
      ██╗ █████╗ ██╗   ██╗ ██████╗ ███╗   ██╗
      ██║██╔══██╗╚██╗ ██╔╝██╔═══██╗████╗  ██║
      ██║███████║ ╚████╔╝ ██║   ██║██╔██╗ ██║
 ██   ██║██╔══██║  ╚██╔╝  ██║   ██║██║╚██╗██║
 ╚█████╔╝██║  ██║   ██║   ╚██████╔╝██║ ╚████║
  ╚════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝
'''
    print(text)
    print("                 —— Jayon 制作 ——")
    #time.sleep(2)

print("使用说明：建议开个记事本，将你想添加的角色、传奇角色、旅行者用空格分开，顺序不限，然后复制一份。")

# 定义读取json文件并生成字典的函数
def load_json_to_dict(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        type(data)
        #print(data)
    return {entry["name"]: entry for entry in data if "name" in entry}

# 加载多个json文件的数据合并成一个字典
json_files = [
    'data.json',
    'custom.json'
]

name_dict = {}
for json_file in json_files:
    if os.path.exists(json_file):
        loaded_data = load_json_to_dict(json_file)
        name_dict.update(loaded_data)
    else:
        print(f"警告：未找到文件 {json_file}")

print("已读取基础数据库和自定义角色数据库。")

# 根据用户输入筛选数据，包含相克
def create_json_with_combinations(selected_names, data_dict):
    filtered_data = []
    not_found = []
    jinx = 0
    for name in selected_names:
        if name in data_dict:
            filtered_data.append(data_dict[name])
        else:
            not_found.append(name)

    for combo in combinations(selected_names, 2):
        combo_name1 = f"{combo[0]}&{combo[1]}"
        combo_name2 = f"{combo[1]}&{combo[0]}"

        if combo_name1 in data_dict:
            filtered_data.append(data_dict[combo_name1])
            jinx = 1
        elif combo_name2 in data_dict:
            filtered_data.append(data_dict[combo_name2])
            jinx = 1

    return filtered_data, not_found, jinx

#定义初始meta info
meta_info = {
    "id": "_meta",
    "name": sname,
    "author": author,
    "logo": logo,
    "townsfolkName": "镇民",
    "outsidersName": "外来者",
    "minionsName": "爪牙",
    "demonsName": "恶魔",
    "townsfolk": "镇民",
    "outsider": "外来者",
    "minion": "爪牙",
    "demon": "恶魔",
    "a jinxedName": "相克",
    "a jinxed": "相克" 
}

#主程序运行
opening_animation() #开场

# 输入剧本标题和作者
sname = input("输入剧本标题：")
author = input("输入作者：")
logo = input("【如果留空默认使用全追logo】粘贴logo图床地址:")
if logo == "":
    logo = "https://www.helloimg.com/i/2024/07/18/669889e8484e6.png"

# 是否添加额外state信息
add_state = input("是否加入额外信息？(例如“疯狂”；默认有“醉酒/中毒”。留空则不添加，输入任意内容则加入)：")
if add_state:
    state_entries = []
    while True:
        state_name = input("输入额外信息名称（留空结束输入）：")
        if not state_name:
            break
        state_description = input("输入额外信息描述：")
        state_entries.append({"stateName": state_name, "stateDescription": state_description})

    if state_entries:
        meta_info["state"] = state_entries

# 输入角色列表,自动添加往生者
user_input = input("【支持传奇角色、旅行者，自动添加往生者】请输入角色名称，多个角色名之间以空格分隔：").split() + ["往生者"]

# 筛选数据并检查不存在的角色
filtered_json_data, not_found_names, jinx = create_json_with_combinations(user_input, name_dict)

# 提示未找到的角色
if not_found_names:
    print(f"以下角色未找到，请检查输入：{', '.join(not_found_names)}")
else:
    print("所有输入角色均找到。")

# 检查是否有相克
if jinx:
    print("找到相克规则，已添加入剧本json。")

# 将meta信息插入到数据开头
filtered_json_data.insert(0, meta_info)

# 生成新json文件
if filtered_json_data and debug != 1:
    output_json_path = f"{sname}.json"
    with open(output_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(filtered_json_data, outfile, ensure_ascii=False, indent=2)

    print(f"剧本json文件已生成：{os.path.abspath(output_json_path)}")
else:
    print("未生成json文件，因为未找到任何匹配的角色或处于调试模式。")

# 按任意键退出
input("按任意键退出程序...")
