import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from PIL import Image

MODEL_PATH = "./Qwen2-VL-2B"

processor = None
model = None


# =========================
# 模型只加载一次
# =========================
def load_model():
    global processor, model

    if model is None:
        processor = AutoProcessor.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True
        )

        model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16,
            device_map="auto"
        )

        model.eval()


# =========================
# VLM分析核心
# =========================
def analyze(image_path, yolo_result):

    image = Image.open(image_path).convert("RGB")
    image = image.resize((512, 512))  # 平衡：质量 + 速度

    # 🔥 改进prompt（关键：不再过度限制）
    prompt = f"""
你是城市交通分析专家，请根据图像和YOLO检测结果进行分析。

YOLO检测结果：
{yolo_result}

请从以下角度分析：

1. 当前道路场景（如：城市道路/路口/主干道）
2. 车辆组成分析（轿车/货车比例）
3. 交通流量判断（畅通/轻度/中度/拥堵，并说明原因）
4. 是否存在异常情况（如货车过多、局部拥堵）
5. 给出3条交通优化建议
6. 一句话总结当前路况
"""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = processor(
        text=[text],
        images=[image],
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True
        )

    generated_ids = [
        out[len(inp):]
        for inp, out in zip(inputs.input_ids, output)
    ]

    result = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]
    result = result.replace("assistant", "")
    result = result.strip()
    return result