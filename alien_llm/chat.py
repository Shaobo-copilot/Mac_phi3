import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    # ====================== 配置 ======================
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model_path = os.path.abspath("models/phi3")   # 改成你的实际路径

    print("正在加载 Phi-3 模型，请稍候... 这可能需要一点时间。")
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        local_files_only=True,
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
        trust_remote_code=True
    )
    
    model.to(device)
    model.eval()

    print(f"✅ 模型加载完成！设备：{device}")
    print("输入 'exit' 或 '退出' 结束对话。\n")

    # 可选的 System Prompt（你可以修改内容）
    system_prompt = "You are a helpful, honest, and friendly AI assistant."

    # 对话历史（用于多轮对话）
    conversation = [
        {"role": "system", "content": system_prompt}
    ]

    while True:
        try:
            user_input = input("你：").strip()
            
            if user_input.lower() in ["exit", "quit", "退出", "bye"]:
                print("👋 结束对话，再见！")
                break
                
            if not user_input:
                continue

            # 添加用户消息到历史
            conversation.append({"role": "user", "content": user_input})

            # 使用 Phi-3 官方推荐的 chat template
            prompt = tokenizer.apply_chat_template(
                conversation,
                tokenize=False,
                add_generation_prompt=True
            )

            # Tokenize 并移动到设备
            inputs = tokenizer(prompt, return_tensors="pt").to(device)

            print("🤖 AI 正在思考...")

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,      # 控制生成长度
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )

            # 只解码新生成的部分（去掉输入的 prompt）
            generated_ids = outputs[0][inputs.input_ids.shape[1]:]
            response = tokenizer.decode(generated_ids, skip_special_tokens=True)

            # 清理响应
            response = response.strip()

            print(f"AI: {response}\n")

            # 把 AI 的回复加入历史，保持上下文
            conversation.append({"role": "assistant", "content": response})

            # 可选：限制历史长度，防止显存爆炸（保留最近10轮对话）
            if len(conversation) > 21:   # system + 10轮 user + 10轮 assistant
                conversation = [conversation[0]] + conversation[-20:]

        except KeyboardInterrupt:
            print("\n👋 对话被中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            continue


if __name__ == "__main__":
    main()