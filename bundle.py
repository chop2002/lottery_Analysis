import os

# 定義要排除的資料夾（避免太亂）
exclude = {'.git', '.venv', '__pycache__', '.pytest_cache', 'data'} 

def bundle_project(root_dir):
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if file.endswith('.py'): # 只抓 Python 程式碼
                file_path = os.path.join(root, file)
                print(f"\n{'='*20}")
                print(f"FILE: {file_path}")
                print(f"{'='*20}\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        print(f.read())
                except:
                    print("// 無法讀取檔案內容")

# 執行並產生內容
bundle_project('.')