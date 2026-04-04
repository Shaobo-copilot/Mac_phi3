"""
Alien Signal Generator 项目设置和启动技能
"""
import os
import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """检查项目依赖是否安装"""
    required_packages = ['flask', 'flask-cors', 'torch', 'transformers']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """安装项目依赖"""
    requirements_file = "scripts/requirements.txt"
    if os.path.exists(requirements_file):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements.requirements_file])
        print("依赖安装完成")
    else:
        print(f"未找到 {requirements_file}")

def check_model_files():
    """检查Phi-3模型文件是否存在"""
    import os
    # 使用绝对路径
    model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models", "phi3/")
    model_dir = os.path.normpath(model_dir)
    
    required_files = [
        "config.json",
        "tokenizer.json", 
        "tokenizer.model",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "model.safetensors.index.json",
        "generation_config.json"
    ]
    
    model_files_exist = True
    for file in required_files:
        if not os.path.exists(os.path.join(model_dir, file)):
            print(f"缺少模型文件: {file}")
            model_files_exist = False
    
    # 检查模型权重文件
    weight_files = [
        "model-00001-of-00002.safetensors",
        "model-00002-of-00002.safetensors"
    ]
    
    for file in weight_files:
        if not os.path.exists(os.path.join(model_dir, file)):
            print(f"缺少模型权重文件: {file}")
            model_files_exist = False
    
    return model_files_exist

def start_server():
    """启动服务器"""
    import subprocess
    import os
    os.chdir("scripts")
    subprocess.Popen([sys.executable, "server.py"])

if __name__ == "__main__":
    print("Alien Signal Generator 项目设置工具")
    print("检查依赖...")
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"缺少依赖包: {missing_deps}")
    else:
        print("所有依赖均已安装")
    
    print("\n检查模型文件...")
    if check_model_files():
        print("所有模型文件齐全")
    else:
        print("缺少部分模型文件，请下载 Phi-3 模型到 models/phi3/ 目录")