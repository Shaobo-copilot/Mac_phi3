# Alien Signal Generator 技能包

这个技能包为 Alien Signal Generator 项目提供了一系列自动化工具和管理功能。

## 技能列表

### 1. 项目设置技能 (`project_setup.py`)

用于检查和安装项目依赖：

```python
from skills.project_setup import check_dependencies, install_dependencies, check_model_files
```

- `check_dependencies()` - 检查Python依赖是否安装
- `install_dependencies()` - 安装所需的Python包
- `check_model_files()` - 检查Phi-3模型文件是否完整

### 2. 数据管理技能 (`data_manager.py`)

用于管理信号和星球数据：

```python
from skills.data_manager import DataManager, validate_all_data, get_data_summary
```

- `DataManager` - 数据管理类，提供CRUD操作
- `validate_all_data()` - 验证所有数据格式
- `get_data_summary()` - 获取数据摘要信息
- 数据验证、添加、修改等功能

### 3. 模型管理技能 (`model_manager.py`)

用于管理Phi-3模型：

```python
from skills.model_manager import ModelManager, quick_check
```

- `ModelManager` - 模型管理类
- `quick_check()` - 快速检查模型状态
- GPU支持检测
- 模型文件完整性检查
- 从Hugging Face下载模型

### 4. 综合技能 (`alien_signal_skill.py`)

提供高层次的项目管理功能：

```python
from skills.alien_signal_skill import AlienSignalSkill, deploy, run, info, validate
```

- `AlienSignalSkill` - 主要技能类
- `deploy()` - 部署项目
- `run()` - 运行服务器
- `info()` - 显示系统信息
- `validate()` - 验证项目完整性

## 使用方法

### 1. 部署项目

```bash
cd .opencode/skills
python alien_signal_skill.py deploy
```

### 2. 运行服务器

```bash
cd .opencode/skills
python alien_signal_skill.py run
# 或指定端口
python alien_signal_skill.py run --port 8080
```

### 3. 查看系统信息

```bash
cd .opencode/skills
python alien_signal_skill.py info
```

### 4. 验证项目

```bash
cd .opencode/skills
python alien_signal_skill.py validate
```

### 5. 在代码中使用技能

```python
from skills import AlienSignalSkill, DataManager, ModelManager

# 创建技能实例
skill = AlienSignalSkill()

# 验证项目
if skill.validate_project():
    print("项目验证通过")
    # 运行服务器
    skill.run_server()

# 管理数据
dm = DataManager()
summary = dm.get_signals_summary()
print(f"信号总数: {summary['total_signals']}")

# 管理模型
mm = ModelManager()
gpu_info = mm.check_gpu_support()
```

## 依赖要求

- Python 3.8+
- torch
- transformers
- flask
- flask-cors
- huggingface-hub (可选，用于下载模型)