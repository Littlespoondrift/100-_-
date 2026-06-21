from transformers import AutoProcessor, AutoModelForVision2Seq

model_path = r"Qwen2-VL-2B"

processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForVision2Seq.from_pretrained(model_path, trust_remote_code=True)

print("模型加载成功")


























