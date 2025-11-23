import os
from huggingface_hub import snapshot_download

def main():
    repo_id = os.getenv("HF_MODEL_REPO", "sifakaveza/layoutlm3_receipt_model")
    revision = os.getenv("HF_MODEL_REVISION", "main")
    subfolder = os.getenv("HF_MODEL_SUBFOLDER", "checkpoint-1000")

    target_dir = os.getenv(
        "MODEL_PATH",
        "/app/models/layoutlmv3_receipt_model/checkpoint-1000"
    )

    os.makedirs(target_dir, exist_ok=True)

    snapshot_download(
        repo_id=repo_id,
        revision=revision,
        allow_patterns=f"{subfolder}/*",
        local_dir=os.path.dirname(target_dir),
        local_dir_use_symlinks=False,
    )

    print(f" Model downloaded into: {target_dir}")

if __name__ == "__main__":
    main()
