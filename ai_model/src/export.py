"""
CAPVIA AI - Model Export Module
Exports trained RT-DETR v2 models to ONNX and TorchScript formats for high-throughput edge deployment.
"""
from __future__ import annotations
import argparse
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def export_rtdetr_model(
    weights_path: str = "ai_model/weights/best.pt",
    output_path: Optional[str] = None,
    format_type: str = "onnx",
    imgsz: int = 1024,
    opset: int = 16,
    half: bool = False,
    dynamic: bool = True,
) -> str:
    """
    Export PyTorch RT-DETR weights (.pt) to ONNX or other deployment formats.
    """
    weights_file = Path(weights_path)
    if not weights_file.exists():
        raise FileNotFoundError(
            f"Weights file not found at: {weights_path}. Train model in Colab first."
        )

    try:
        from ultralytics import RTDETR
    except ImportError as e:
        raise ImportError(
            "Ultralytics is required for export. Install with: pip install ultralytics"
        ) from e

    logger.info(f"Loading RT-DETR weights from {weights_path}...")
    model = RTDETR(str(weights_file))

    logger.info(f"Exporting to {format_type.upper()} with imgsz={imgsz}, opset={opset}, dynamic={dynamic}...")
    exported_path = model.export(
        format=format_type,
        imgsz=imgsz,
        opset=opset,
        half=half,
        dynamic=dynamic,
    )

    if output_path and exported_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.move(exported_path, str(out_p))
        exported_path = str(out_p)

    logger.info(f"Export complete: {exported_path}")
    return str(exported_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export RT-DETR model to ONNX")
    parser.add_argument("--weights", default="ai_model/weights/best.pt", help="Path to best.pt")
    parser.add_argument("--output", default="ai_model/weights/best.onnx", help="Path for exported file")
    parser.add_argument("--format", default="onnx", choices=["onnx", "torchscript", "engine"])
    parser.add_argument("--imgsz", type=int, default=1024, help="Inference resolution")
    parser.add_argument("--half", action="store_true", help="Enable FP16 half precision")
    args = parser.parse_args()

    export_rtdetr_model(
        weights_path=args.weights,
        output_path=args.output,
        format_type=args.format,
        imgsz=args.imgsz,
        half=args.half,
    )
