#!/usr/bin/env python3
"""
Alien Signal Generator 命令行接口
"""
import argparse
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from alien_signal_skill import AlienSignalSkill, deploy, run, info, validate
from data_manager import DataManager, validate_all_data, get_data_summary
from model_manager import ModelManager, quick_check

def main():
    parser = argparse.ArgumentParser(description='Alien Signal Generator 技能命令行工具')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 项目命令
    project_parser = subparsers.add_parser('project', help='项目管理命令')
    project_parser.add_argument('action', choices=['setup', 'info', 'validate', 'run'], 
                               help='项目操作: setup(设置), info(信息), validate(验证), run(运行)')
    project_parser.add_argument('--port', type=int, default=5000, help='运行端口 (默认: 5000)')
    
    # 数据命令
    data_parser = subparsers.add_parser('data', help='数据管理命令')
    data_parser.add_argument('action', choices=['info', 'validate'], 
                            help='数据操作: info(信息), validate(验证)')
    
    # 模型命令
    model_parser = subparsers.add_parser('model', help='模型管理命令')
    model_parser.add_argument('action', choices=['info', 'validate', 'quick-check'], 
                             help='模型操作: info(信息), validate(验证), quick-check(快速检查)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    skill = AlienSignalSkill()
    dm = DataManager()
    mm = ModelManager()
    
    try:
        if args.command == 'project':
            if args.action == 'setup':
                print("设置项目...")
                deploy()
            elif args.action == 'info':
                print("获取项目信息...")
                info()
            elif args.action == 'validate':
                print("验证项目...")
                result = validate()
                print(f"验证结果: {'✓ 通过' if result else '✗ 失败'}")
            elif args.action == 'run':
                print(f"运行服务器 (端口 {args.port})...")
                skill.run_server(port=args.port)
                
        elif args.command == 'data':
            if args.action == 'info':
                print("获取数据摘要...")
                get_data_summary()
            elif args.action == 'validate':
                print("验证数据格式...")
                result = validate_all_data()
                print(f"验证结果: {'✓ 通过' if result else '✗ 失败'}")
                
        elif args.command == 'model':
            if args.action == 'info':
                print("获取模型信息...")
                mm.get_model_info()
            elif args.action == 'validate':
                print("验证模型文件...")
                result = mm.check_model_files()
                print(f"验证结果: {'✓ 通过' if result else '✗ 失败'}")
            elif args.action == 'quick-check':
                print("快速检查模型...")
                quick_check()
                
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"错误: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()