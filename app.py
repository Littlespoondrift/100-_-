from flask import Flask, render_template, request
import os
import time
from datetime import datetime

from yolo_detector import detect
from vlm_qwen import analyze, load_model

app = Flask(__name__)

UPLOAD_FOLDER = "static/upload"
RESULT_FOLDER = "static/result"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# 加载Qwen模型（只加载一次）
load_model()


@app.route("/", methods=["GET", "POST"])
def index():

    result_text = None
    result_img = None
    stats = None

    vehicle_total = None
    traffic_index = None
    level = None
    cost_time = None
    current_time = None

    if request.method == "POST":

        start_time = time.time()

        file = request.files["image"]

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        result_img_path = os.path.join(RESULT_FOLDER, file.filename)

        # =====================
        # YOLO检测
        # =====================
        stats = detect(path, result_img_path)

        # =====================
        # 中文映射
        # =====================
        name_map = {
            "car": "小汽车",
            "truck": "货车",
            "bus": "公交车",
            "motorcycle": "摩托车",
            "bicycle": "自行车",
            "person": "行人",
            "traffic light": "红绿灯"
        }

        stats_cn = {}
        for k, v in stats.items():
            stats_cn[name_map.get(k, k)] = v

        # =====================
        # Qwen分析
        # =====================
        result_text = analyze(path, stats_cn)

        result_img = result_img_path.replace("\\", "/")

        stats = stats_cn

        # =====================
        # 交通指数
        # =====================
        vehicle_total = 0
        for k, v in stats.items():
            if k in ["小汽车", "货车", "公交车", "摩托车", "自行车"]:
                vehicle_total += v

        traffic_index = min(vehicle_total * 3, 100)

        if vehicle_total < 10:
            level = "畅通"
        elif vehicle_total < 20:
            level = "轻度拥堵"
        elif vehicle_total < 35:
            level = "中度拥堵"
        else:
            level = "严重拥堵"

        cost_time = round(time.time() - start_time, 2)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stats_json = stats

    return render_template(
        "index.html",
        result_text=result_text,
        result_img=result_img,
        stats=stats,
        stats_json=stats_json,
        vehicle_total=vehicle_total,
        traffic_index=traffic_index,
        level=level,
        cost_time=cost_time,
        current_time=current_time
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)