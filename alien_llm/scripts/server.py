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

    # 从请求中获取输入数据
    data = request.get_json()
    signal_names = data.get('signal_names', [])  # 用户选择的信号名称列表
    planet_name = data.get('planet_name', '')  # 用户选择的星球名称
    temperature = data.get('temperature', 0.2)  # 生成文本的随机性参数
    max_new_tokens = data.get('max_new_tokens', 80)  # 生成文本的最大长度

    # 如果模型尚未加载，则加载模型
    if model is None:
        device = load_model()  # 加载模型并确定设备（如 CPU 或 GPU）
    else:
        device = model.device  # 获取已加载模型的设备信息

    # 根据用户提供的信号名称查找对应的信号数据
    chosen_signals = [s for s in signals if s["name"] in signal_names]

    # 提取信号的语义标签
    semantic_tags = []
    for s in chosen_signals:
        semantic_tags.extend(s["semantic_tags"])

    # 根据用户提供的星球名称查找对应的星球数据
    planet = next((p for p in planets if p["name"] == planet_name), None)
    if not planet:
        planet = random.choice(planets)  # 如果未找到星球，则随机选择一个星球

    # 提取星球的相关信息
    planet_name_val = planet["name"]
    civilization = planet["civilization_type"]  # 文明类型
    perception = planet["perception_style"]  # 感知风格

    # 构建输入模型的 Prompt
    prompt = f"""# 构建更为严谨的 Prompt
        <|system|>
        You are an expert in speculative biology and science fiction. Your task is to explain how an alien civilization interprets Earth's signals based on their unique perception. Keep your answer strictly within 2 sentences. Do not include prefixes like "Solution:" or "Interpretation:".<|end|>
        <|user|>
        An alien civilization from K2-18b (Oceanic civilization, Fluid pattern recognition) receives these signals: terrestrial_life, bipedal_organism, abstract_art.
        Explain their interpretation.<|end|>
        <|assistant|>
        The K2-18b civilization perceives the signals as rhythmic pulsations in their liquid environment, interpreting 'bipedal organisms' as strange, vertical current-disturbances. They view 'abstract art' not as static images, but as complex, swirling energy vortexes that mirror their own fluid-based linguistic structures.<|end|>
        <|user|>
        An alien civilization from {planet_name_val} ({civilization}, {perception}) receives these signals: {", ".join(semantic_tags)}.
        Explain their interpretation.<|end|>
        <|assistant|>"""

    # 使用 tokenizer 对 Prompt 进行编码
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}  # 将输入数据移动到模型设备

    # 调用模型生成文本
    output = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,  # 最大生成长度
        temperature=temperature,  # 控制生成的随机性
        top_p=0.9,  # nucleus sampling 的概率阈值
        do_sample=True  # 启用采样生成
    )

    # 解码生成的文本
    text = tokenizer.decode(output[0], skip_special_tokens=True)

    # 提取生成结果的主要内容
    if "Explain their interpretation." in text:
        result_text = text.split("Explain their interpretation.")[-1].strip()
    else:
        result_text = text.strip()

    # 构建响应数据
    response_data = {
        'result': result_text,  # 返回的代码，介绍了这个文明如何解读信号
        'full_text': text,  # 完整的解码文本
        'planet': planet,  # 返回的星球信息
        'signals': chosen_signals,  # 返回的信号信息
        'timestamp': datetime.now().isoformat()  # 时间戳
    }

    # 将生成的结果保存到历史记录
    history = load_history()
    history_entry = {
        'id': int(datetime.now().timestamp() * 1000),  # 使用毫秒时间戳作为唯一ID
        'time': datetime.now().strftime('%H:%M:%S'),  # 当前时间
        'planet': planet_name,  # 星球名称
        'signals': ', '.join(signal_names),  # 信号名称列表
        'fullData': response_data  # 完整的响应数据
    }
    history.insert(0, history_entry)  # 将新记录插入到历史记录的开头
    save_history(history)  # 保存历史记录

    return jsonify(response_data)  # 返回响应数据

if __name__ == '__main__':
    load_data()
    load_model()
    app.run(debug=True, port=5000)
