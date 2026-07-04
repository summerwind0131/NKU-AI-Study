from __future__ import annotations

import argparse
import csv
import json
import warnings
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from tqdm import tqdm

from src.hand_posture_models import create_model, freeze_backbone, unfreeze_all


CLASSES = ["A", "B", "C", "Five", "Point", "V"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a hand-posture classifier.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/hand_posture"))
    parser.add_argument("--model", default="mobilenet_v3_large")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--freeze-epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--fine-lr", type=float, default=8e-5)
    parser.add_argument("--weight-decay", type=float, default=5e-2)
    parser.add_argument("--label-smoothing", type=float, default=0.05)
    parser.add_argument("--class-weight", action="store_true")
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", type=Path, default=Path("runs/mobilenet_cpu"))
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--resume-checkpoint", type=Path, default=None)
    return parser.parse_args()


def seed_everything(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.benchmark = True


def build_transforms(img_size: int) -> tuple[transforms.Compose, transforms.Compose]:
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    train_tf = transforms.Compose(
        [
            transforms.RandomResizedCrop(img_size, scale=(0.72, 1.0), ratio=(0.8, 1.25)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(18),
            transforms.ColorJitter(brightness=0.22, contrast=0.22, saturation=0.16, hue=0.03),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
            transforms.RandomErasing(p=0.18, scale=(0.02, 0.16), ratio=(0.3, 3.3)),
        ]
    )
    eval_tf = transforms.Compose(
        [
            transforms.Resize(int(img_size * 1.14)),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ]
    )
    return train_tf, eval_tf


def assert_class_order(dataset: datasets.ImageFolder) -> None:
    actual = dataset.classes
    if actual != CLASSES:
        raise ValueError(f"Class order mismatch. Expected {CLASSES}, got {actual}")


def class_weights_from_dataset(dataset: datasets.ImageFolder, device: torch.device) -> torch.Tensor:
    targets = np.array(dataset.targets)
    counts = np.bincount(targets, minlength=len(CLASSES))
    weights = counts.sum() / (len(CLASSES) * np.maximum(counts, 1))
    return torch.tensor(weights, dtype=torch.float32, device=device)


def make_optimizer(model: nn.Module, lr: float, weight_decay: float) -> torch.optim.Optimizer:
    params = [p for p in model.parameters() if p.requires_grad]
    return torch.optim.AdamW(params, lr=lr, weight_decay=weight_decay)


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
    scaler: torch.amp.GradScaler | None = None,
    desc: str = "",
) -> tuple[float, float, list[int], list[int]]:
    is_train = optimizer is not None
    model.train(is_train)
    total_loss = 0.0
    total_correct = 0
    total_seen = 0
    all_preds: list[int] = []
    all_targets: list[int] = []

    with torch.set_grad_enabled(is_train):
        for images, targets in tqdm(loader, leave=False, desc=desc):
            images = images.to(device, non_blocking=True)
            targets = targets.to(device, non_blocking=True)
            if is_train:
                optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
                logits = model(images)
                loss = criterion(logits, targets)

            if is_train:
                assert scaler is not None
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()

            preds = logits.argmax(dim=1)
            batch_size = targets.size(0)
            total_loss += loss.item() * batch_size
            total_correct += (preds == targets).sum().item()
            total_seen += batch_size
            all_preds.extend(preds.detach().cpu().tolist())
            all_targets.extend(targets.detach().cpu().tolist())

    return total_loss / total_seen, total_correct / total_seen, all_preds, all_targets


def main() -> None:
    args = parse_args()
    warnings.filterwarnings("ignore", message="Palette images with Transparency expressed in bytes")
    seed_everything(args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_tf, val_tf = build_transforms(args.img_size)
    train_ds = datasets.ImageFolder(args.data_dir / "train", transform=train_tf)
    val_ds = datasets.ImageFolder(args.data_dir / "val", transform=val_tf)
    assert_class_order(train_ds)
    assert_class_order(val_ds)
    print(f"Data directory: {args.data_dir}")
    print(f"Training images: {len(train_ds)}")
    print(f"Validation images: {len(val_ds)}")
    print(f"Classes: {train_ds.classes}")

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.workers,
        pin_memory=device.type == "cuda",
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.workers,
        pin_memory=device.type == "cuda",
    )

    model = create_model(args.model, num_classes=len(CLASSES), pretrained=not args.no_pretrained).to(device)
    if args.resume_checkpoint is not None:
        checkpoint = torch.load(args.resume_checkpoint, map_location=device)
        if checkpoint["model_name"] != args.model:
            raise ValueError(f"Checkpoint model is {checkpoint['model_name']}, but --model is {args.model}.")
        model.load_state_dict(checkpoint["model_state"])
        print(f"Loaded checkpoint from {args.resume_checkpoint}")

    if args.freeze_epochs > 0:
        freeze_backbone(model, args.model)
    criterion_weight = class_weights_from_dataset(train_ds, device) if args.class_weight else None
    criterion = nn.CrossEntropyLoss(weight=criterion_weight, label_smoothing=args.label_smoothing)
    optimizer = make_optimizer(model, args.lr, args.weight_decay)
    scaler = torch.amp.GradScaler(enabled=device.type == "cuda")

    config = vars(args).copy()
    config["data_dir"] = str(config["data_dir"])
    config["out_dir"] = str(config["out_dir"])
    if config["resume_checkpoint"] is not None:
        config["resume_checkpoint"] = str(config["resume_checkpoint"])
    config["device"] = str(device)
    (args.out_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (args.out_dir / "class_to_idx.json").write_text(json.dumps(train_ds.class_to_idx, indent=2), encoding="utf-8")

    best_acc = 0.0
    log_path = args.out_dir / "history.csv"
    with log_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["epoch", "train_loss", "train_acc", "val_loss", "val_acc", "lr"])
        writer.writeheader()

        for epoch in range(1, args.epochs + 1):
            if epoch == args.freeze_epochs + 1:
                unfreeze_all(model)
                optimizer = make_optimizer(model, args.fine_lr, args.weight_decay)

            current_lr = optimizer.param_groups[0]["lr"]
            train_loss, train_acc, _, _ = run_epoch(
                model, train_loader, criterion, device, optimizer, scaler, desc=f"train {epoch:03d}/{args.epochs}"
            )
            val_loss, val_acc, val_preds, val_targets = run_epoch(
                model, val_loader, criterion, device, desc=f"val   {epoch:03d}/{args.epochs}"
            )
            writer.writerow(
                {
                    "epoch": epoch,
                    "train_loss": round(train_loss, 6),
                    "train_acc": round(train_acc, 6),
                    "val_loss": round(val_loss, 6),
                    "val_acc": round(val_acc, 6),
                    "lr": current_lr,
                }
            )
            f.flush()

            print(
                f"epoch {epoch:03d}/{args.epochs} "
                f"train_acc={train_acc:.4f} val_acc={val_acc:.4f} val_loss={val_loss:.4f}"
            )

            checkpoint = {
                "model_name": args.model,
                "model_state": model.state_dict(),
                "classes": CLASSES,
                "img_size": args.img_size,
                "val_acc": val_acc,
                "epoch": epoch,
            }
            torch.save(checkpoint, args.out_dir / "last.pth")
            if val_acc > best_acc:
                best_acc = val_acc
                torch.save(checkpoint, args.out_dir / "best.pth")
                report = classification_report(val_targets, val_preds, target_names=CLASSES, digits=4)
                matrix = confusion_matrix(val_targets, val_preds).tolist()
                (args.out_dir / "classification_report.txt").write_text(report, encoding="utf-8")
                (args.out_dir / "confusion_matrix.json").write_text(
                    json.dumps({"classes": CLASSES, "matrix": matrix}, indent=2),
                    encoding="utf-8",
                )

    print(f"Best validation accuracy: {best_acc:.4f}")
    print(f"Best checkpoint: {args.out_dir / 'best.pth'}")


if __name__ == "__main__":
    main()
