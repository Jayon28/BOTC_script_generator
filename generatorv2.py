import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from itertools import combinations
image_overrides = {}
frame_links = None

# --- 核心逻辑函数 ---
def load_json_to_dict(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return {entry["name"]: entry for entry in data if "name" in entry}

#修改图片链接函数
def edit_image_link():
    name = simple_input("修改角色图片链接", "请输入要修改图片链接的角色名称：")
    if not name:
        return
    link = simple_input("图片链接", f"请输入 {name} 的新图片链接：")
    if not link:
        return
    image_overrides[name] = link
    messagebox.showinfo("成功", f"已设置 {name} 的图片链接。将在生成 JSON 时生效。")


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

def overwrite_role_table_from_ids(ids, role_table_path, output_path):
    def normalize_id(s):
        return s.replace("Button", "").replace("-", "").replace("_", "").lower()
    try:
        with open(role_table_path, 'r', encoding='utf-8') as f:
            role_table = json.load(f)
        matched = [entry for entry in role_table if normalize_id(entry.get("id", "")) in ids]
        matched_ids = {normalize_id(entry.get("id", "")) for entry in matched}
        unmatched_ids = ids - matched_ids
        if unmatched_ids:
            messagebox.showwarning("未匹配的ID", f"以下 ID 未匹配到任何角色：\n{', '.join(unmatched_ids)}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(matched, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("错误", f"更新 roletable.json 失败: {e}")
        return False

def generate_json():
    sname = entry_title.get()
    author = entry_author.get()
    logo = entry_logo.get() or "https://www.helloimg.com/i/2024/07/18/669889e8484e6.png"
    user_input = entry_roles.get("1.0", tk.END).strip().split() + ["往生者"]

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

    if var_add_state.get():
        state_entries = []
        for sname, sdesc in extra_states:
            if sname.get() and sdesc.get():
                state_entries.append({"stateName": sname.get(), "stateDescription": sdesc.get()})
        if state_entries:
            meta_info["state"] = state_entries

    filtered_data, not_found, jinx = create_json_with_combinations(user_input, name_dict)
    if jinx:
        filtered_data, not_found, jinx = create_json_with_combinations(user_input + ["灯神"], name_dict)

    if not sname:
        messagebox.showerror("错误", "请输入剧本标题")
        return

    if not_found:
        messagebox.showwarning("未找到角色", f"以下角色未找到：{', '.join(not_found)}")

    # 应用图片链接覆盖
    for entry in filtered_data:
        if 'name' in entry and entry['name'] in image_overrides:
            entry['image'] = image_overrides[entry['name']]

    # 去重角色，按 name 去重
    unique_data = {}
    for entry in filtered_data:
        if 'name' in entry:
            unique_data[entry['name']] = entry
        else:
            unique_data[id(entry)] = entry  # fallback
    filtered_data = list(unique_data.values())

    filtered_data.insert(0, meta_info)
    if filtered_data:
        output_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], initialfile=f"{sname}.json")
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("完成", f"已生成剧本文件：\n{os.path.abspath(output_path)}")
    else:
        messagebox.showwarning("失败", "未生成文件，检查输入")

#刷新角色链接
def refresh_link_editor(roles):
    global frame_links
    if frame_links:
        frame_links.destroy()

    # 容器：外层 frame + canvas + scrollbar
    container = tk.Frame(root)
    container.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(container, height=200)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame_links = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_links, anchor="nw")

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_links.bind("<Configure>", on_configure)

    # 添加角色显示行
    for role in roles:
        row = tk.Frame(frame_links)
        row.pack(fill="x", pady=1)
        tk.Label(row, text=role, width=20, anchor="w").pack(side=tk.LEFT)
        link_label = tk.Label(row, text=image_overrides.get(role, "(使用默认)"), fg="blue", cursor="hand2", anchor="w", wraplength=400, justify="left")
        link_label.pack(side=tk.LEFT, fill="x", expand=True)

        def bind_label(label=link_label, role=role):
            def on_click(event):
                new_link = simple_input("图片链接", f"{role} 的新图片链接：")
                if new_link:
                    image_overrides[role] = new_link
                    label.config(text=new_link)
            label.bind("<Button-1>", on_click)
        bind_label()


def add_state_row():
    row_frame = tk.Frame(frame_states)
    row_frame.pack(pady=2)
    state_name = tk.Entry(row_frame, width=15)
    state_desc = tk.Entry(row_frame, width=40)
    state_name.pack(side=tk.LEFT, padx=5)
    state_desc.pack(side=tk.LEFT)
    extra_states.append((state_name, state_desc))

def import_json():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list) and all('id' in item and len(item) == 1 for item in data):
            messagebox.showinfo("提示", "载入了国染委json！正在更新角色表...")
            ids = {''.join(c for c in item['id'] if c.isalnum()).lower() for item in data}
            if overwrite_role_table_from_ids(ids, 'roleTable.json', file_path):
                messagebox.showinfo("完成", "已根据角色ID更新该文件内容并重新载入角色数据库。")
                global name_dict
                name_dict = {}
                for file in ['data.json', 'custom.json']:
                    if os.path.exists(file):
                        name_dict.update(load_json_to_dict(file))
            return

        roles = [entry['name'] for entry in data if entry.get('id') != '_meta']
        entry_roles.delete("1.0", tk.END)
        entry_roles.insert(tk.END, ' '.join(roles))
        if '_meta' in [entry.get('id') for entry in data]:
            meta = next(entry for entry in data if entry.get('id') == '_meta')
            entry_title.delete(0, tk.END)
            entry_title.insert(0, meta.get('name', ''))
            entry_author.delete(0, tk.END)
            entry_author.insert(0, meta.get('author', ''))
            entry_logo.delete(0, tk.END)
            entry_logo.insert(0, meta.get('logo', ''))
            if meta.get('state'):
                for state in meta['state']:
                    add_state_row()
                    extra_states[-1][0].insert(0, state.get("stateName", ""))
                    extra_states[-1][1].insert(0, state.get("stateDescription", ""))
                var_add_state.set(True)


         # 检查是否有新角色需要写入 custom.json
        custom_path = 'custom.json'
        all_known = set()
        for file in ['data.json', custom_path]:
            if os.path.exists(file):
                with open(file, 'r', encoding='utf-8') as f:
                    all_known.update(entry['name'] for entry in json.load(f) if 'name' in entry)

        new_roles = [entry for entry in data if entry.get('name') and entry.get('id') != '_meta' and entry['name'] not in all_known]
        if new_roles:
            if os.path.exists(custom_path):
                with open(custom_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            else:
                existing = []
            existing.extend(new_roles)
            with open(custom_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("新增角色", f"已添加 {len(new_roles)} 个新角色到 custom.json")
        
        refresh_link_editor(roles)
        messagebox.showinfo("导入成功", "剧本内容已导入")
    except Exception as e:
        messagebox.showerror("导入失败", f"无法导入 JSON 文件：{e}")

def add_role():
    name = simple_input("添加角色", "请输入要添加的角色名称：")
    if name:
        current = entry_roles.get("1.0", tk.END).strip().split()
        if name not in current:
            current.append(name)
            entry_roles.delete("1.0", tk.END)
            entry_roles.insert(tk.END, ' '.join(current))

def remove_role():
    name = simple_input("删除角色", "请输入要删除的角色名称：")
    if name:
        current = entry_roles.get("1.0", tk.END).strip().split()
        if name in current:
            current.remove(name)
            entry_roles.delete("1.0", tk.END)
            entry_roles.insert(tk.END, ' '.join(current))

def simple_input(title, prompt):
    popup = tk.Toplevel()
    popup.title(title)
    tk.Label(popup, text=prompt).pack(padx=10, pady=5)
    entry = tk.Entry(popup)
    entry.pack(padx=10, pady=5)
    entry.focus()
    result = []
    def on_submit():
        result.append(entry.get())
        popup.destroy()
    tk.Button(popup, text="确定", command=on_submit).pack(pady=5)
    popup.grab_set()
    popup.wait_window()
    return result[0] if result else None

# --- 加载数据 ---
name_dict = {}
for file in ['data.json', 'custom.json']:
    if os.path.exists(file):
        name_dict.update(load_json_to_dict(file))

# --- GUI 设置 ---
root = tk.Tk()
root.title("剧本生成器 by Jayon from [SUI染钟楼] V3.0")
root.geometry("650x500")
extra_states = []

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

entry_title = tk.Entry(frame, width=40)
entry_author = tk.Entry(frame, width=40)
entry_logo = tk.Entry(frame, width=50)
entry_title.grid(row=0, column=1, padx=5, pady=5)
entry_author.grid(row=1, column=1, padx=5, pady=5)
entry_logo.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame, text="剧本标题").grid(row=0, column=0, sticky='e')
tk.Label(frame, text="作者").grid(row=1, column=0, sticky='e')
tk.Label(frame, text="logo地址 (可选)").grid(row=2, column=0, sticky='e')

var_add_state = tk.BooleanVar()
tk.Checkbutton(frame, text="添加额外状态", variable=var_add_state).grid(row=3, columnspan=2, sticky='w', pady=5)

frame_states = tk.LabelFrame(root, text="额外状态信息", padx=10, pady=10)
frame_states.pack(fill="x", padx=10, pady=5)

btn_add_state = tk.Button(root, text="添加一条状态", command=add_state_row)
btn_add_state.pack(pady=5)

tk.Label(root, text="请输入角色名称（空格分隔）").pack()
entry_roles = scrolledtext.ScrolledText(root, width=60, height=5)
entry_roles.pack(pady=5)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)
tk.Button(frame_buttons, text="导入已有JSON", command=import_json).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="添加角色", command=add_role).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="删除角色", command=remove_role).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="修改图片链接", command=edit_image_link).pack(side=tk.LEFT, padx=5) #修改图片链接

tk.Button(root, text="生成JSON文件", command=generate_json, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5).pack(pady=10)

# 添加 logo 图片显示
try:
    from urllib.request import urlopen
    from PIL import Image, ImageTk
    import io

    image_url = "https://i.postimg.cc/VNc6Dkx4/image.png"
    image_bytes = urlopen(image_url).read()
    image_data = Image.open(io.BytesIO(image_bytes))
    image_data = image_data.resize((100, 100))
    logo_img = ImageTk.PhotoImage(image_data)

    logo_label = tk.Label(root, image=logo_img)
    logo_label.image = logo_img
    logo_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
except Exception as e:
    print("无法加载Logo图片：", e)
    
#root.geometry("800x800")  # 临时放大窗口确保可见
root.mainloop()
