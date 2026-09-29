"""
CAPVIA AI - RT-DETR v2 Large Training Script
Usage: python ai_model/train_rtdetr.py
Outputs: ai_model/weights/best_rtdetr.pt, ai_model/weights/last.pt, ai_model/weights/best.onnx
"""
from __future__ import annotations
import argparse, json, logging, os, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("capvia.train")

def parse_args():
    p = argparse.ArgumentParser(description="Train RT-DETR v2 for paint defect detection")
    p.add_argument("--data",     default="ai_model/dataset.yaml")
    p.add_argument("--epochs",   type=int,   default=150)
    p.add_argument("--imgsz",    type=int,   default=1024)
    p.add_argument("--batch",    type=int,   default=-1)
    p.add_argument("--lr0",      type=float, default=1e-4)
    p.add_argument("--device",   default="0")
    p.add_argument("--resume",   action="store_true")
    p.add_argument("--patience", type=int,   default=20)
    p.add_argument("--workers",  type=int,   default=8)
    p.add_argument("--name",     default="capvia_rtdetr")
    p.add_argument("--checkpoint", default=None, help="Path to specific checkpoint file to resume from")
    return p.parse_args()

def train(args):
    try:
        from ultralytics import RTDETR
    except ImportError:
        logger.error("Ultralytics not installed. Run: pip install ultralytics>=8.3.0")
        sys.exit(1)
    weights_dir = Path("ai_model/weights")
    weights_dir.mkdir(parents=True, exist_ok=True)
    training_dir = Path("ai_model/training")
    training_dir.mkdir(parents=True, exist_ok=True)
    run_dir = Path(f"runs/rtdetr/{args.name}")

    ckpt_candidate = None
    if args.checkpoint:
        ckpt_candidate = Path(args.checkpoint)
    elif args.resume:
        if (run_dir / "weights" / "last.pt").exists():
            ckpt_candidate = run_dir / "weights" / "last.pt"
        elif (weights_dir / "last.pt").exists():
            ckpt_candidate = weights_dir / "last.pt"

    import torch
    device = args.device
    if device == "0" and not torch.cuda.is_available():
        logger.warning("CUDA GPU not detected. Automatically falling back to device='cpu'.")
        device = "cpu"
    use_amp = True if (device != "cpu" and torch.cuda.is_available()) else False

    batch = args.batch
    workers = args.workers
    if device == "cpu":
        if batch == -1:
            batch = 4
            logger.info("Setting batch=4 for CPU execution (AutoBatch requires GPU).")
        if workers > 2:
            workers = 2
            logger.info("Setting workers=2 for optimal Windows CPU performance.")

    if args.resume and ckpt_candidate and ckpt_candidate.exists():
        logger.info(f"Resuming training from checkpoint: {ckpt_candidate}")
        model = RTDETR(str(ckpt_candidate))
        results = model.train(resume=True, epochs=args.epochs, device=device, plots=False)
    else:
        if args.resume:
            logger.warning("Resume flag set but no last.pt found! Starting fresh.")
        model_weights = "rtdetr-l.pt"
        logger.info(f"Starting fresh with {model_weights}")
        model = RTDETR(model_weights)
        logger.info("=" * 60)
        logger.info("CAPVIA AI - RT-DETR v2 Large Training")
        logger.info(f"Dataset: {args.data} | Epochs: {args.epochs} | ImgSz: {args.imgsz} | LR: {args.lr0}")
        logger.info(f"Device: {device} | AMP: {use_amp} | Early-stop: {args.patience} epochs")
        logger.info("=" * 60)
        results = model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz, batch=batch, optimizer="AdamW", lr0=args.lr0, lrf=0.01, cos_lr=True, weight_decay=1e-4, warmup_epochs=3, device=device, workers=workers, patience=args.patience, save_period=5, amp=use_amp, plots=False, name=args.name, project="runs/rtdetr", exist_ok=True, verbose=True, flipud=0.3, fliplr=0.5, degrees=15.0, translate=0.1, scale=0.5, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, mosaic=0.8, mixup=0.1)
    run_dir = Path(f"runs/rtdetr/{args.name}")
    best_src = run_dir / "weights" / "best.pt"
    last_src = run_dir / "weights" / "last.pt"
    if best_src.exists():
        import shutil
        shutil.copy(best_src, weights_dir / "best_rtdetr.pt")
        shutil.copy(last_src, weights_dir / "last.pt")
        logger.info(f"Best weights saved to {weights_dir / 'best_rtdetr.pt'}")
    metrics = {"best_map50": float(results.results_dict.get("metrics/mAP50(B)", 0.0)), "best_map5095": float(results.results_dict.get("metrics/mAP50-95(B)", 0.0)), "best_precision": float(results.results_dict.get("metrics/precision(B)", 0.0)), "best_recall": float(results.results_dict.get("metrics/recall(B)", 0.0)), "epochs_trained": args.epochs, "model": "rtdetr-l", "imgsz": args.imgsz}
    (training_dir / "training_metrics.json").write_text(json.dumps(metrics, indent=2))
    logger.info(f"mAP50={metrics['best_map50']:.4f} | mAP50-95={metrics['best_map5095']:.4f}")
    try:
        logger.info("Exporting to ONNX...")
        model.export(format="onnx", imgsz=args.imgsz, simplify=True)
        onnx_src = run_dir / "weights" / "best.onnx"
        if onnx_src.exists():
            import shutil
            shutil.copy(onnx_src, weights_dir / "best.onnx")
    except Exception as e:
        logger.warning(f"ONNX export failed (non-critical): {e}")
    logger.info("Training complete!")

if __name__ == "__main__":
    train(parse_args())
