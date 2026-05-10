#!/usr/bin/env python3
"""
音乐发现应用GitHub上传脚本
使用GitHub API直接上传到新仓库
"""

import os
import base64
import requests
from pathlib import Path
import json

# 配置
GITHUB_TOKEN = "your_token_here"
USERNAME = "fish1981bimmer"
REPO_NAME = "music-discovery-app"
REPO_FULL_NAME = f"{USERNAME}/{REPO_NAME}"
BASE_URL = f"https://api.github.com/repos/{REPO_FULL_NAME}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def create_repo():
    """创建新的GitHub仓库"""
    print("创建仓库...")
    url = "https://api.github.com/user/repos"
    data = {
        "name": REPO_NAME,
        "description": "一个完全免费的音乐发现应用，集成多个免费音乐API，无需任何认证",
        "private": False,
        "auto_init": False
    }
    
    response = requests.post(url, headers=HEADERS, json=data)
    
    if response.status_code == 201:
        repo_info = response.json()
        print(f"✓ 仓库创建成功: {repo_info['full_name']}")
        print(f"  URL: {repo_info['html_url']}")
        return True
    else:
        print(f"✗ 仓库创建失败: {response.status_code}")
        print(f"  错误: {response.text}")
        return False

def get_file_list():
    """获取项目文件列表"""
    print("扫描项目文件...")
    
    # 要上传的文件列表
    files_to_upload = []
    
    # 获取所有文件
    for root, dirs, files in os.walk("."):
        # 跳过 .git 目录和其他不需要的目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
        
        for file in files:
            file_path = os.path.join(root, file)
            # 跳过二进制文件和大文件
            if file_path.endswith(('.pyc', '.pyo', '.exe', '.dll', '.so', '.dylib')):
                continue
            
            # 转换为相对路径
            rel_path = os.path.relpath(file_path, ".")
            files_to_upload.append((file_path, rel_path))
    
    print(f"找到 {len(files_to_upload)} 个文件")
    return files_to_upload

def upload_file(file_path, repo_path):
    """上传单个文件"""
    try:
        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Base64编码
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        # 检查文件是否存在
        url = f"{BASE_URL}/contents/{repo_path}"
        check_response = requests.get(url, headers=HEADERS)
        
        # 构建请求数据
        data = {
            "message": f"Add {repo_path}",
            "content": encoded_content
        }
        
        # 如果文件已存在，添加sha
        if check_response.status_code == 200:
            file_info = check_response.json()
            data['sha'] = file_info['sha']
        
        # 上传文件
        response = requests.put(url, headers=HEADERS, json=data)
        
        if response.status_code in [200, 201]:
            action = "更新" if check_response.status_code == 200 else "上传"
            print(f"✓ {action}成功: {repo_path}")
            return True
        else:
            print(f"✗ 上传失败: {repo_path} - {response.status_code}")
            print(f"  错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 上传出错: {repo_path} - {str(e)}")
        return False

def batch_upload(files_mapping):
    """批量上传文件"""
    print("\n开始批量上传...")
    
    success_count = 0
    total_count = len(files_mapping)
    
    for i, (file_path, repo_path) in enumerate(files_mapping, 1):
        print(f"\n[{i}/{total_count}] 处理: {repo_path}")
        
        if upload_file(file_path, repo_path):
            success_count += 1
        
        # 避免API调用过于频繁
        if i < total_count:
            import time
            time.sleep(0.5)
    
    print(f"\n上传完成: {success_count}/{total_count} 个文件")
    return success_count

def main():
    """主函数"""
    print("=== 音乐发现应用GitHub上传 ===")
    print(f"用户: {USERNAME}")
    print(f"仓库名: {REPO_NAME}")
    print(f"仓库URL: https://github.com/{REPO_FULL_NAME}")
    print()
    
    # 切换到项目目录
    os.chdir("/Users/a1234/.openclaw/workspace/music-discovery-app")
    
    # 获取文件列表
    files_mapping = get_file_list()
    
    if not files_mapping:
        print("✗ 没有找到要上传的文件")
        return
    
    # 创建仓库
    if not create_repo():
        print("✗ 仓库创建失败，退出")
        return
    
    # 等待一下让仓库创建完成
    import time
    time.sleep(2)
    
    # 批量上传
    success_count = batch_upload(files_mapping)
    
    print("\n=== 上传完成 ===")
    print(f"成功上传 {success_count} 个文件")
    print(f"仓库URL: https://github.com/{REPO_FULL_NAME}")
    print("\n你可以使用以下命令克隆仓库:")
    print(f"git clone https://github.com/{REPO_FULL_NAME}.git")

if __name__ == "__main__":
    main()