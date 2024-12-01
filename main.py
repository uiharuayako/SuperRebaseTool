import os
import shutil
import tkinter as tk
from tkinter import messagebox
import json
from git import Repo, GitCommandError

# 定义保存的 JSON 文件路径
JSON_FILE_PATH = "config.json"


def load_data():
    """加载用户保存的数据"""
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data():
    """将用户当前的输入保存到 JSON 文件"""
    data = {
        "directory_name": dir_entry.get(),
        "git_url": git_entry.get(),
        "branch1": branch1_entry.get(),
        "branch2": branch2_entry.get(),
        "new_branch": new_branch_entry.get(),
        "commit_message": commit_message_text.get("1.0", tk.END).strip()
    }
    try:
        with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("成功", "数据已成功保存！")
    except Exception as e:
        messagebox.showerror("错误", f"保存数据时发生错误！\n错误信息: {str(e)}")


def clone_repository():
    global repo1, repo2
    directory_name = dir_entry.get()
    git_url = git_entry.get()

    if not directory_name or not git_url:
        messagebox.showerror("错误", "请输入目录名称和 Git 链接！")
        return

    try:
        # 克隆第一个仓库
        repo1 = Repo.clone_from(git_url, directory_name)

        # 克隆第二个仓库
        second_directory = f"{directory_name}_copy"
        repo2 = Repo.clone_from(git_url, second_directory)

        messagebox.showinfo("成功", f"仓库克隆成功！生成了以下两个目录：\n1. {directory_name}\n2. {second_directory}")
    except GitCommandError as e:
        messagebox.showerror("错误", f"克隆仓库失败！\n错误信息: {str(e)}")
    except Exception as e:
        messagebox.showerror("错误", f"发生未知错误！\n错误信息: {str(e)}")


def checkout_branch(repo, branch_name, repo_label):
    if not branch_name:
        messagebox.showerror("错误", f"请输入{repo_label}的分支名称！")
        return
    try:
        repo.git.checkout(branch_name)
        messagebox.showinfo("成功", f"{repo_label}成功切换到分支：{branch_name}")
    except GitCommandError as e:
        messagebox.showerror("错误", f"{repo_label}切换分支失败！\n错误信息: {str(e)}")


def copy_contents():
    if not repo1 or not repo2:
        messagebox.showerror("错误", "请先克隆仓库！")
        return
    try:
        src_dir = repo1.working_tree_dir
        dest_dir = repo2.working_tree_dir

        if not src_dir or not dest_dir:
            raise Exception("无法获取工作目录！")

        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dest_dir, item)
            if os.path.isdir(s) and item == ".git":
                continue
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        messagebox.showinfo("成功", "文件内容已成功复制并覆盖！")
    except Exception as e:
        messagebox.showerror("错误", f"复制内容失败！\n错误信息: {str(e)}")


def create_new_branch():
    branch_name = new_branch_entry.get()
    if not branch_name:
        messagebox.showerror("错误", "请输入新分支名称！")
        return
    try:
        repo2.git.checkout("-b", branch_name)
        messagebox.showinfo("成功", f"已在第二个仓库中创建并切换到新分支：{branch_name}")
    except GitCommandError as e:
        messagebox.showerror("错误", f"新建分支失败！\n错误信息: {str(e)}")


def commit_changes():
    commit_message = commit_message_text.get("1.0", tk.END).strip()
    if not commit_message:
        messagebox.showerror("错误", "请输入提交信息！")
        return
    if not repo2:
        messagebox.showerror("错误", "请先克隆第二个仓库！")
        return

    try:
        # 检查是否有未提交的修改
        if repo2.is_dirty():
            repo2.git.add(A=True)  # 添加所有变更
            repo2.index.commit(commit_message)  # 提交变更
            messagebox.showinfo("成功", "更改已提交！")
            origin = repo2.remotes.origin
            origin.push()

        else:
            messagebox.showinfo("信息", "没有未提交的更改。")
    except GitCommandError as e:
        messagebox.showerror("错误", f"提交失败！\n错误信息: {str(e)}")
    except Exception as e:
        messagebox.showerror("错误", f"提交过程中发生错误！\n错误信息: {str(e)}")


def create_gui():
    global dir_entry, git_entry, branch1_entry, branch2_entry, new_branch_entry, commit_message_text, repo1, repo2
    repo1 = repo2 = None

    # 加载之前保存的数据
    data = load_data()

    # 初始化窗口
    root = tk.Tk()
    root.title("Git 仓库操作工具")

    # 第一行：目录名称
    tk.Label(root, text="目录名称:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    dir_entry = tk.Entry(root, width=40)
    dir_entry.grid(row=0, column=1, padx=10, pady=5)
    dir_entry.insert(0, data.get("directory_name", ""))

    # 第二行：Git 链接
    tk.Label(root, text="Git 链接:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    git_entry = tk.Entry(root, width=40)
    git_entry.grid(row=1, column=1, padx=10, pady=5)
    git_entry.insert(0, data.get("git_url", ""))

    clone_button = tk.Button(root, text="克隆仓库", command=clone_repository)
    clone_button.grid(row=1, column=2, padx=10, pady=5)

    # 第三行：第一个仓库切换分支
    tk.Label(root, text="源仓库分支:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    branch1_entry = tk.Entry(root, width=40)
    branch1_entry.grid(row=2, column=1, padx=10, pady=5)
    branch1_entry.insert(0, data.get("branch1", ""))

    branch1_button = tk.Button(root, text="切换分支",
                               command=lambda: checkout_branch(repo1, branch1_entry.get(), "第一个仓库"))
    branch1_button.grid(row=2, column=2, padx=10, pady=5)

    # 第四行：第二个仓库切换分支
    tk.Label(root, text="目标仓库分支:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    branch2_entry = tk.Entry(root, width=40)
    branch2_entry.grid(row=3, column=1, padx=10, pady=5)
    branch2_entry.insert(0, data.get("branch2", ""))

    branch2_button = tk.Button(root, text="切换分支",
                               command=lambda: checkout_branch(repo2, branch2_entry.get(), "第二个仓库"))
    branch2_button.grid(row=3, column=2, padx=10, pady=5)

    # 第五行：复制内容
    copy_button = tk.Button(root, text="复制源仓库文件到目标仓库", command=copy_contents)
    copy_button.grid(row=4, column=1, padx=10, pady=5)

    # 第六行：新建分支
    tk.Label(root, text="新分支名称:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    new_branch_entry = tk.Entry(root, width=40)
    new_branch_entry.grid(row=5, column=1, padx=10, pady=5)
    new_branch_entry.insert(0, data.get("new_branch", ""))

    new_branch_button = tk.Button(root, text="新建并切换分支", command=create_new_branch)
    new_branch_button.grid(row=5, column=2, padx=10, pady=5)

    # 第七行：提交更改
    tk.Label(root, text="提交信息:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    commit_message_text = tk.Text(root, height=4, width=40)
    commit_message_text.grid(row=6, column=1, padx=10, pady=5)
    commit_message_text.insert("1.0", data.get("commit_message", ""))

    commit_button = tk.Button(root, text="提交更改", command=commit_changes)
    commit_button.grid(row=6, column=2, padx=10, pady=5)

    # 保存按钮
    save_button = tk.Button(root, text="保存当前配置", command=save_data)
    save_button.grid(row=7, column=1, padx=10, pady=5)

    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    create_gui()
