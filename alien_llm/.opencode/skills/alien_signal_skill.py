"""
Alien Signal Generator 综合技能
"""
import os
import sys
import subprocess

# 添加当前目录到Python路径以解决导入问题
sys.path.insert(0, os.path.dirname(__file__))

from project_setup import *
from data_manager import *
from model_manager import *

class AlienSignalSkill:
    def __init__(self):
        self.data_manager = DataManager()
        self.model_manager = ModelManager()
    
    def setup_project(self):
        """完整设置项目"""
        print("开始设置 Alien Signal Generator 项目...")
        
        # 检查依赖
        missing_deps = check_dependencies()
        if missing_deps:
            print(f"安装缺失的依赖: {missing_deps}")
            install_dependencies()
        else:
            print("所有依赖已安装")
        
        # 检查模型
        model_exists = check_model_files()
        if not model_exists:
            print("检测到模型文件缺失，建议下载 Phi-3 模型")
        else:
            print("模型文件完整")
    
    def validate_project(self):
        """验证项目完整性"""
        print("验证项目完整性...")
        
        # 检查依赖
        missing_deps = check_dependencies()
        if missing_deps:
            print(f"缺失依赖: {missing_deps}")
            return False
        
        # 检查数据
        data_valid = validate_all_data()
        if not data_valid:
            print("数据格式存在问题")
            return False
        
        # 检查模型
        model_valid = self.model_manager.check_model_files()
        if not model_valid:
            print("模型文件不完整")
            return False
        
        print("项目验证通过")
        return True
    
    def run_server(self, host='localhost', port=5000):
        """运行服务器"""
        print(f"启动 Alien Signal Generator 服务器在 {host}:{port}")
        
        # 验证项目
        if not self.validate_project():
            print("项目验证失败，无法启动服务器")
            return
        
        # 切换到scripts目录并启动服务器
        original_dir = os.getcwd()
        try:
            os.chdir('scripts')
            subprocess.run([sys.executable, 'server.py'])
        finally:
            os.chdir(original_dir)
    
    def get_system_info(self):
        """获取系统信息"""
        print("=== Alien Signal Generator 系统信息 ===")
        
        # Python版本
        print(f"Python 版本: {sys.version}")
        
        # 项目验证
        print("\n--- 项目验证 ---")
        project_ok = self.validate_project()
        print(f"项目完整性: {'✓' if project_ok else '✗'}")
        
        # 数据摘要
        print("\n--- 数据摘要 ---")
        get_data_summary()
        
        # 模型信息
        print("\n--- 模型信息 ---")
        model_ok = self.model_manager.check_model_files()
        print(f"模型文件完整性: {'✓' if model_ok else '✗'}")
        
        # GPU支持
        print("\n--- 硬件支持 ---")
        self.model_manager.check_gpu_support()

def deploy():
    """部署项目"""
    skill = AlienSignalSkill()
    skill.setup_project()

def run():
    """运行项目"""
    skill = AlienSignalSkill()
    skill.run_server()

def info():
    """显示系统信息"""
    skill = AlienSignalSkill()
    skill.get_system_info()

def validate():
    """验证项目"""
    skill = AlienSignalSkill()
    return skill.validate_project()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Alien Signal Generator 技能')
    parser.add_argument('action', choices=['deploy', 'run', 'info', 'validate'], 
                       help='要执行的操作')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口')
    
    args = parser.parse_args()
    
    skill = AlienSignalSkill()
    
    if args.action == 'deploy':
        skill.setup_project()
    elif args.action == 'run':
        skill.run_server(port=args.port)
    elif args.action == 'info':
        skill.get_system_info()
    elif args.action == 'validate':
        result = skill.validate_project()
        print(f"验证结果: {'通过' if result else '失败'}")