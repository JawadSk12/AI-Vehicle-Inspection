"""
CAPVIA AI - Local Dataset Preparation Script for Google Colab
Packages ai_model/dataset/ into ai_model.zip ready for seamless upload to Google Colab.

Usage:
    python colab/prepare_dataset.py
    python colab/prepare_dataset.py --source ai_model/dataset --output ai_model.zip
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import zipfile


def prepare_dataset_zip(
    source_dir: str = "ai_model/dataset",
    output_zip: str = "ai_model.zip",
) -> str:
    src_path = Path(source_dir)
    if not src_path.exists():
        raise FileNotFoundError(f"Source dataset directory not found at: {src_path.resolve()}")

    data_yaml = src_path / "data.yaml"
    if not data_yaml.exists():
        raise FileNotFoundError(f"data.yaml not found inside: {src_path.resolve()}")

    print(f"\n=======================================================")
    print(f" CAPVIA AI - Preparing Dataset for Google Colab")
    print(f" Source: {src_path.resolve()}")
    print(f" Target: {Path(output_zip).resolve()}")
    print(f"=======================================================\n")

    # Count items
    splits = ["train", "valid", "test"]
    stats = {}
    for s in splits:
        img_dir = src_path / s / "images"
        if img_dir.exists():
            imgs = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpeg"))
            stats[s] = len(imgs)
        else:
            stats[s] = 0

    print(f"Dataset Summary:")
    for s, cnt in stats.items():
        print(f"  - {s.capitalize()}: {cnt} images")
    print(f"  - Total: {sum(stats.values())} images\n")

    # Create ZIP
    out_path = Path(output_zip)
    print(f"Compressing dataset into {out_path.name}...")

    total_files = 0
    for root, _, files in os.walk(src_path):
        total_files += len(files)

    processed = 0
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, _, files in os.walk(src_path):
            for file in files:
                full_path = Path(root) / file
                # Write with prefix 'dataset/' so Colab detects 'dataset/data.yaml'
                rel_path = full_path.relative_to(src_path)
                arcname = Path("dataset") / rel_path
                zf.write(full_path, arcname=str(arcname).replace("\\", "/"))
                processed += 1
                if processed % 200 == 0 or processed == total_files:
                    pct = (processed / max(total_files, 1)) * 100
                    print(f"  Progress: {processed}/{total_files} files ({pct:.1f}%)")

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\nSUCCESS: Created {output_zip} ({size_mb:.2f} MB)")
    print(f"Next Steps:")
    print(f"  1. Open Google Colab (colab/train_colab.ipynb)")
    print(f"  2. Upload {out_path.name} when prompted")
    print(f"  3. Run the notebook to train RT-DETR v2-L\n")
    return str(out_path.resolve())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Package CAPVIA dataset for Google Colab")
    parser.add_argument("--source", default="ai_model/dataset", help="Path to dataset root")
    parser.add_argument("--output", default="ai_model.zip", help="Path to output zip archive")
    args = parser.parse_args()

    prepare_dataset_zip(args.source, args.output)
