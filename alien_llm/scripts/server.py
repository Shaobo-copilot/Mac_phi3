from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import random
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
from datetime import datetime
import threading

app = Flask(__name__, static_folder='static')
CORS(app)

# 全局变量，避免每次请求都加载模型
model = None
tokenizer = None
signals = None
planets = None

def load_data():
    global signals, planets
    
    if signals is None:
        with open(os.path.join(app.root_path, '../signals/nfc_info.json')) as f:
            signals = json.load(f)
    
    if planets is None:
        with open(os.path.join(app.root_path, '../signals/planet_info.json')) as f:
            planets = json.load(f)

def load_model():
    global model, tokenizer
    
    if model is None:
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        model_path = os.path.join(app.root_path, '../models/phi3')
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16
        ).to(device)
        
        return device
    return None

def load_history():
    """从Raw Data/Storage.json加载历史记录"""
    storage_file = os.path.join(app.root_path, '../Raw_Data/Storage.json')
    try:
        with open(storage_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_history(history):
    """保存历史记录到Raw Data/Storage.json"""
    storage_file = os.path.join(app.root_path, '../Raw_Data/Storage.json')
    try:
        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            print(f"✅ 成功保存 {len(history)} 条记录到 {storage_file}")
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False
    

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/signals', methods=['GET'])
def get_signals():
    load_data()
    return jsonify(signals)

@app.route('/api/planets', methods=['GET'])
def get_planets():
    load_data()
    return jsonify(planets)

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取历史记录"""
    history = load_history()
    return jsonify(history)

@app.route('/api/history', methods=['POST'])
def save_history_api():
    """保存历史记录"""
    try:
        data = request.get_json()
        if save_history(data):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to save history'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    global model, tokenizer
    
    data = request.get_json()
    signal_names = data.get('signal_names', [])
    planet_name = data.get('planet_name', '')
    temperature = data.get('temperature', 0.2)
    max_new_tokens = data.get('max_new_tokens', 80)
    
    # 首次调用时加载模型
    if model is None:
        device = load_model()
    else:
        device = model.device
    
    # 查找信号
    chosen_signals = [s for s in signals if s["name"] in signal_names]
    
    # 提取语义标签
    semantic_tags = []
    for s in chosen_signals:
        semantic_tags.extend(s["semantic_tags"])
    
    # 查找星球
    planet = next((p for p in planets if p["name"] == planet_name), None)
    if not planet:
        planet = random.choice(planets)
    
    planet_name_val = planet["name"]
    civilization = planet["civilization_type"]
    perception = planet["perception_style"]
    
    # 构建 Prompt
    prompt = f"""<|user|>
An alien civilization from {planet_name_val} receives signals from Earth.

Detected signal meanings:
{", ".join(semantic_tags)}

Their civilization type:
{civilization}

Their perception style:
{perception}

Explain how this civilization interprets the signals.
Keep the answer within 2 sentences.
"""

    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    output = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True
    )
    
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # 提取 assistant 后的内容
    if "Keep the answer within 2 sentences." in text:
        result_text = text.split("Keep the answer within 2 sentences.")[-1].strip()
    else:
        result_text = text.strip()
    
    # 创建响应数据
    response_data = {
        'result': result_text, #返回的代码，介绍了这个文明如何解读信号
        'full_text': text, # 完整的解码文本
        'planet': planet, #返回的星球信息
        'signals': chosen_signals,
        'timestamp': datetime.now().isoformat()
    }
    
    # 将这次生成添加到历史记录
    history = load_history()
    history_entry = {
        'id': int(datetime.now().timestamp() * 1000),  # 使用毫秒时间戳作为唯一ID
        'time': datetime.now().strftime('%H:%M:%S'),
        'planet': planet_name,
        'signals': ', '.join(signal_names),
        'fullData': response_data
    }
    history.insert(0, history_entry)  # 插入到开头
    save_history(history)
    
    return jsonify(response_data)

if __name__ == '__main__':
    load_data()
    load_model()
    app.run(debug=True, port=5000)
