from modelscope import snapshot_download

snapshot_download(
    "Qwen/Qwen2-VL-2B-Instruct",
    local_dir="./Qwen2-VL-2B"
)