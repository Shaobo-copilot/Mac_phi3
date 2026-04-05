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
    max_new_tokens = data.get('max_new_tokens', 40)
    
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
    prompt = f"""
An alien civilization from {planet_name_val} receives signals from Earth.

Please analyze each signal category separately and respond in this exact JSON format:
{{
  "signal_analysis": {{
    "semantic_interpretation": "How they interpret the semantic tags: {', '.join(semantic_tags)}",
    "civilization_context": "How their civilization type '{civilization}' affects interpretation", 
    "perception_influence": "How their perception style '{perception}' shapes understanding",
    "final_conclusion": "请综合以上三点（语义解读、文明背景、感知影响），对{planet_name_val}文明如何整体理解这些地球信号给出一个深刻的、有洞察力的最终结论。"
  }}
}}

Keep each section concise (1-2 sentences). Ensure complete sentences with proper punctuation.
Please respond in Chinese only.
"""
    
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    output = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens + 20,  # 增加缓冲空间
        temperature=temperature,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        early_stopping=True
    )
    
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # 提取 assistant 后的内容
    if "<|assistant|>" in text:
        result_text = text.split("<|assistant|>", 1)[1].strip()
    else:
        result_text = text.strip()
    
    # 确保句子完整性
    import re
    sentence_endings = ['.', '!', '?']
    last_valid_end = -1
    for ending in sentence_endings:
        pos = result_text.rfind(ending)
        if pos > last_valid_end:
            last_valid_end = pos

    if last_valid_end != -1:
        result_text = result_text[:last_valid_end + 1]
    
    # 尝试解析为JSON格式（如果模型返回了JSON）
    import json
    try:
        # 尝试提取JSON部分
        json_start = result_text.find('{')
        json_end = result_text.rfind('}')
        if json_start != -1 and json_end != -1:
            json_str = result_text[json_start:json_end+1]
            parsed_result = json.loads(json_str)
            # 如果解析成功并且包含所需字段，则使用解析后的结果
            if 'signal_analysis' in parsed_result:
                signal_analysis = parsed_result['signal_analysis']
                result_text = signal_analysis.get('final_conclusion', result_text)
    except:
        # 如果解析失败，则使用原始文本（保持向后兼容）
        pass
    
    # 返回结构化分析结果
    return jsonify({
        'planet_analysis': f"关于{planet_name_val}的分析：{planet['name']}是一个{planet['civilization_type']}文明的观测点，其{planet['perception_style']}感知方式会影响对信号的理解。",
        'civilization_analysis': f"文明类型分析：{civilization}类型的文明会基于其社会结构和科技发展水平来解释接收到的信号。",
        'perception_analysis': f"感知风格分析：{perception}的感知风格意味着他们更关注信号的整体模式而非细节。",
        'signal_analysis': result_text,
        'planet': planet,
        'signals': chosen_signals,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    load_data()
    load_model()
    app.run(debug=True, port=5000)
