from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import random
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
from datetime import datetime

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

@app.route('/api/generate', methods=['POST'])
def generate():
    global model, tokenizer
    
    data = request.get_json()
    signal_names = data.get('signal_names', [])
    planet_name = data.get('planet_name', '')
    temperature = data.get('temperature', 0.7)
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
<|assistant|>
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
    if "<|assistant|>" in text:
        result_text = text.split("<|assistant|>", 1)[1].strip()
    else:
        result_text = text.strip()
    
    return jsonify({
        'result': result_text,
        'planet': planet,
        'signals': chosen_signals,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    load_data()
    load_model()
    app.run(debug=True, port=5000)
