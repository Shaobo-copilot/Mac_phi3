from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import random
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
from datetime import datetime
import re

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
        
        print(f"✓ 模型已加载，使用设备: {device}")
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

def parse_analysis(text):
    """
    解析模型输出的分段文本
    期望格式:
    【语义解释】
    ...内容...
    
    【文明背景】
    ...内容...
    
    【感知影响】
    ...内容...
    
    【综合结论】
    ...内容...
    """
    
    sections = {
        'semantic_interpretation': '',
        'civilization_context': '',
        'perception_influence': '',
        'final_conclusion': ''
    }
    
    # 定义分隔符和对应的键
    markers = [
        ('【语义解释】', 'semantic_interpretation'),
        ('【文明背景】', 'civilization_context'),
        ('【感知影响】', 'perception_influence'),
        ('【综合结论】', 'final_conclusion'),
    ]
    
    current_section = None
    current_content = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # 检查是否遇到新的分隔符
        found_marker = False
        for marker, key in markers:
            if marker in line:
                # 保存前一个section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # 开始新的section
                current_section = key
                current_content = []
                found_marker = True
                break
        
        # 如果不是分隔符，就添加到当前section
        if not found_marker and current_section:
            current_content.append(line)
    
    # 保存最后一个section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

def ensure_complete_sentences(text):
    """确保文本以完整的句子结尾"""
    text = text.strip()
    
    # 如果已经以标点符号结尾，直接返回
    if text and text[-1] in '.!?。！？':
        return text
    
    # 找最后一个标点符号
    sentence_endings = ['.', '!', '?', '。', '！', '？']
    last_valid_pos = -1
    
    for ending in sentence_endings:
        pos = text.rfind(ending)
        if pos > last_valid_pos:
            last_valid_pos = pos
    
    if last_valid_pos != -1:
        return text[:last_valid_pos + 1]
    
    return text

@app.route('/api/generate', methods=['POST'])
def generate():
    global model, tokenizer
    
    data = request.get_json()
    signal_names = data.get('signal_names', [])
    planet_name = data.get('planet_name', '')
    temperature = data.get('temperature', 0.7)
    max_new_tokens = data.get('max_new_tokens', 120)  # 增加到120以获得更充分的输出
    
    # 首次调用时加载模型
    if model is None:
        device = load_model()
    else:
        device = model.device
    
    # 加载数据
    load_data()
    
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
    signal_names_str = ', '.join([s["name"] for s in chosen_signals])
    semantic_tags_str = ', '.join(semantic_tags)
    
    # ============ 核心改变：简洁清晰的 Prompt ============
    prompt = f"""You are analyzing alien signal reception.

Planet: {planet_name_val}
Civilization type: {civilization}
Perception style: {perception}
Received signals: {signal_names_str}
Signal meanings: {semantic_tags_str}

Please provide analysis in Chinese with this structure:

【语义解释】
Explain what these signal meanings indicate to this civilization:

【文明背景】
How does their civilization type affect interpretation:

【感知影响】
How does their perception style shape understanding:

【综合结论】
Final integrated analysis based on all above:
"""
    
    print(f"\n📝 Prompt length: {len(prompt)} chars")
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt")
    input_length = len(inputs['input_ids'][0])
    print(f"📊 Input tokens: {input_length}, Max new tokens: {max_new_tokens}")
    
    # 移到设备
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # ============ 生成 ============
    output = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        early_stopping=True,
        top_p=0.95,  # 添加核采样以改进质量
        top_k=50     # 限制候选词表
    )
    
    # 解码
    full_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"🎯 Full output length: {len(full_text)} chars")
    
    # 提取模型生成的部分（去掉prompt）
    if prompt in full_text:
        result_text = full_text.split(prompt, 1)[1].strip()
    else:
        # 如果找不到完整prompt，尝试找到最后的【
        last_marker_pos = max(
            full_text.rfind('【语义解释】'),
            full_text.rfind('【文明背景】'),
            full_text.rfind('【感知影响】'),
            full_text.rfind('【综合结论】')
        )
        if last_marker_pos > 0:
            result_text = full_text[last_marker_pos:]
        else:
            result_text = full_text
    
    print(f"📌 Extracted result length: {len(result_text)} chars")
    print(f"📌 First 200 chars: {result_text[:200]}")
    
    # 确保句子完整性
    result_text = ensure_complete_sentences(result_text)
    
    # ============ 拆解文本为不同的部分 ============
    sections = parse_analysis(result_text)
    
    # 返回结构化数据
    response = {
        'raw_text': result_text,  # 原始生成的文本
        'sections': {
            'semantic_interpretation': {
                'title': '语义解释',
                'content': sections['semantic_interpretation']
            },
            'civilization_context': {
                'title': '文明背景',
                'content': sections['civilization_context']
            },
            'perception_influence': {
                'title': '感知影响',
                'content': sections['perception_influence']
            },
            'final_conclusion': {
                'title': '综合结论',
                'content': sections['final_conclusion']
            }
        },
        'metadata': {
            'planet': planet,
            'signals': chosen_signals,
            'civilization_type': civilization,
            'perception_style': perception,
            'timestamp': datetime.now().isoformat()
        }
    }
    
    print(f"✓ 返回结构化数据，包含 {len([s for s in sections.values() if s])} 个非空section")
    
    return jsonify(response)

if __name__ == '__main__':
    load_data()
    load_model()
    app.run(debug=True, port=5000)