"""
Alien Signal Generator 模型管理技能
"""
import os
import subprocess
import sys
from pathlib import Path
import torch

class ModelManager:
    def __init__(self):
        # 使用绝对路径以确保在任何工作目录下都能找到模型
        import os
        self.model_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "phi3/")
        # 规范化路径
        self.model_path = os.path.normpath(self.model_path)
    
    def check_gpu_support(self):
        """检查GPU支持情况"""
        gpu_info = {
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda,
            "mps_available": hasattr(torch.backends, "mps") and torch.backends.mps.is_available(),
            "device_count": torch.cuda.device_count()
        }
        
        print("=== GPU 支持信息 ===")
        print(f"CUDA 可用: {gpu_info['cuda_available']}")
        if gpu_info['cuda_available']:
            print(f"CUDA 版本: {gpu_info['cuda_version']}")
            print(f"GPU 数量: {gpu_info['device_count']}")
        print(f"MPS 可用 (Apple Silicon): {gpu_info['mps_available']}")
        
        return gpu_info
    
    def check_model_size(self):
        """检查模型大小"""
        if not os.path.exists(self.model_path):
            print(f"模型路径不存在: {self.model_path}")
            return None
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.model_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        size_mb = total_size / (1024 * 1024)
        print(f"模型总大小: {size_mb:.2f} MB ({total_size} 字节)")
        return total_size
    
    def check_model_files(self):
        """检查模型文件完整性"""
        required_files = [
            "config.json",
            "tokenizer.json", 
            "tokenizer.model",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "model.safetensors.index.json",
            "generation_config.json"
        ]
        
        weight_files = [
            "model-00001-of-00002.safetensors",
            "model-00002-of-00002.safetensors"
        ]
        
        print("=== 检查必需文件 ===")
        all_present = True
        
        for file in required_files:
            file_path = os.path.join(self.model_path, file)
            exists = os.path.exists(file_path)
            print(f"{file}: {'✓' if exists else '✗'}")
            if not exists:
                all_present = False
        
        print("\n=== 检查权重文件 ===")
        for file in weight_files:
            file_path = os.path.join(self.model_path, file)
            exists = os.path.exists(file_path)
            print(f"{file}: {'✓' if exists else '✗'}")
            if not exists:
                all_present = False
        
        return all_present
    
    def download_model_hf(self, model_name="microsoft/Phi-3-mini-4k-instruct"):
        """从Hugging Face下载模型"""
        try:
            from huggingface_hub import snapshot_download
            
            print(f"正在下载模型 {model_name} 到 {self.model_path}")
            snapshot_download(
                repo_id=model_name,
                local_dir=self.model_path,
                local_dir_use_symlinks=False
            )
            print("模型下载完成!")
            return True
        except ImportError:
            print("请先安装 huggingface_hub: pip install huggingface_hub")
            return False
        except Exception as e:
            print(f"下载过程中出现错误: {str(e)}")
            return False
    
    def get_model_info(self):
        """获取模型基本信息"""
        config_path = os.path.join(self.model_path, "config.json")
        if not os.path.exists(config_path):
            print("未找到模型配置文件")
            return None
        
        try:
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            info = {
                "model_type": config.get("model_type", "Unknown"),
                "hidden_size": config.get("hidden_size"),
                "num_attention_heads": config.get("num_attention_heads"),
                "num_hidden_layers": config.get("num_hidden_layers"),
                "vocab_size": config.get("vocab_size"),
                "max_position_embeddings": config.get("max_position_embeddings")
            }
            
            print("=== 模型信息 ===")
            for key, value in info.items():
                print(f"{key}: {value}")
                
            return info
        except Exception as e:
            print(f"读取模型配置时出现错误: {str(e)}")
            return None

def quick_check():
    """快速检查模型状态"""
    mm = ModelManager()
    print("快速检查模型状态...")
    
    files_ok = mm.check_model_files()
    print(f"\n文件完整性: {'良好' if files_ok else '存在问题'}")
    
    size = mm.check_model_size()
    if size:
        print(f"模型大小: {size / (1024*1024):.2f} MB")
    
    gpu_info = mm.check_gpu_support()
    if gpu_info["mps_available"]:
        print("检测到 Apple Silicon，将使用 MPS 加速")
    elif gpu_info["cuda_available"]:
        print("检测到 CUDA，将使用 GPU 加速")
    else:
        print("将使用 CPU 运行模型")
    
    return files_ok

if __name__ == "__main__":
    print("Alien Signal Generator 模型管理工具")
    quick_check()