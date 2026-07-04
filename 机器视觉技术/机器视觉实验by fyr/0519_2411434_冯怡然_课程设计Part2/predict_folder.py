from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch
from PIL import Image
from PIL import ImageOps
from sklearn.metrics import classification_report, confusion_matrix
from torchvision import transforms

from src.hand_posture_models import create_model


CLASSES = ["A", "B", "C", "Five", "Point", "V"]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff", ".ppm", ".pgm", ".pnm"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict images and calculate accuracy when labels are available.")
    parser.add_argument("input_path", nargs="?", type=Path, default=None, help="Image file or folder to predict.")
    parser.add_argument("--checkpoint", type=Path, default=Path("runs/mobilenet_cpu_resume/best.pth"))
    parser.add_argument("--image-dir", type=Path, default=None, help="Same as input_path; kept for old commands.")
    parser.add_argument("--out", type=Path, default=Path("predictions.csv"))
    parser.add_argument("--eval-out", type=Path, default=Path("eval_summary.json"))
    parser.add_argument("--resize-mode", choices=["crop", "squash", "pad"], default="crop")
    parser.add_argument("--tta", action="store_true", help="Average original and horizontal-flipped predictions.")
    parser.add_argument("--quiet", action="store_true", help="Do not print every image; only print the summary.")
    return parser.parse_args()


def build_transform(img_size: int, resize_mode: str) -> transforms.Compose:
    common = [
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
    if resize_mode == "crop":
        resize_steps = [transforms.Resize(int(img_size * 1.14)), transforms.CenterCrop(img_size)]
    elif resize_mode == "squash":
        resize_steps = [transforms.Resize((img_size, img_size))]
    elif resize_mode == "pad":
        resize_steps = [
            transforms.Lambda(lambda img: ImageOps.pad(img, (img_size, img_size), color=(255, 255, 255))),
        ]
    else:
        raise ValueError(f"Unknown resize mode: {resize_mode}")
    return transforms.Compose(resize_steps + common)


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def collect_images(input_path: Path) -> list[Path]:
    if input_path.is_file():
        if not is_image(input_path):
            raise FileNotFoundError(f"This file is not a supported image: {input_path}")
        return [input_path]
    if not input_path.exists():
        raise FileNotFoundError(f"Path does not exist: {input_path}")

    images = [p for p in input_path.rglob("*") if is_image(p)]
    images.sort()
    if not images:
        exts = ", ".join(sorted(IMAGE_EXTENSIONS))
        raise FileNotFoundError(f"No supported images found in {input_path}. Supported extensions: {exts}")
    return images


def label_from_path(path: Path, root: Path, classes: list[str]) -> str | None:
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path

    if len(rel.parts) >= 2 and rel.parts[0] in classes:
        return rel.parts[0]

    name = path.stem.lower()
    for cls in sorted(classes, key=len, reverse=True):
        if name.startswith(cls.lower()):
            return cls
    return None


def predict_one(model: torch.nn.Module, image: Image.Image, tf: transforms.Compose, device: torch.device, tta: bool) -> torch.Tensor:
    tensors = [tf(image)]
    if tta:
        tensors.append(tf(image.transpose(Image.FLIP_LEFT_RIGHT)))
    batch = torch.stack(tensors).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(batch), dim=1)
    return probs.mean(dim=0)


def main() -> None:
    args = parse_args()
    input_path = args.image_dir or args.input_path or Path("data/hand_posture/val")
    input_path = input_path.expanduser()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.checkpoint, map_location=device)
    classes = checkpoint.get("classes", CLASSES)
    model = create_model(checkpoint["model_name"], num_classes=len(classes), pretrained=False)
    model.load_state_dict(checkpoint["model_state"])
    model.to(device).eval()
    tf = build_transform(checkpoint.get("img_size", 224), args.resize_mode)

    image_paths = collect_images(input_path)
    root = input_path if input_path.is_dir() else input_path.parent

    rows: list[list[str]] = []
    y_true: list[int] = []
    y_pred: list[int] = []
    has_any_label = False

    for path in image_paths:
        display_name = str(path.relative_to(root))
        true_label = label_from_path(path, root, classes)
        with Image.open(path) as img:
            img = img.convert("RGB")
            probs = predict_one(model, img, tf, device, args.tta)
        pred_idx = int(probs.argmax().item())
        pred = classes[pred_idx]
        conf = float(probs[pred_idx].item())

        correct = ""
        if true_label in classes:
            has_any_label = True
            true_idx = classes.index(true_label)
            y_true.append(true_idx)
            y_pred.append(pred_idx)
            correct = "1" if true_idx == pred_idx else "0"

        true_text = true_label or ""
        if not args.quiet:
            print(f"{display_name}\ttrue={true_text or '-'}\tpred={pred}\tconf={conf:.4f}\t{correct}")
        rows.append([display_name, true_text, pred, correct, f"{conf:.6f}"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "true_label", "prediction", "correct", "confidence"])
        writer.writerows(rows)

    if has_any_label:
        correct_count = sum(int(a == b) for a, b in zip(y_true, y_pred))
        accuracy = correct_count / len(y_true)
        labels = list(range(len(classes)))
        report = classification_report(y_true, y_pred, labels=labels, target_names=classes, digits=4, zero_division=0)
        matrix = confusion_matrix(y_true, y_pred, labels=list(range(len(classes)))).tolist()
        print()
        print(f"accuracy={accuracy:.6f} ({correct_count}/{len(y_true)})")
        print(report)
        summary = {"accuracy": accuracy, "correct": correct_count, "total": len(y_true), "classes": classes, "confusion_matrix": matrix}
        args.eval_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        (args.out.with_suffix(".report.txt")).write_text(report, encoding="utf-8")
    else:
        print()
        print("No labels found, so accuracy was not calculated.")
        print("Accuracy can be calculated when images are in A/B/C/Five/Point/V folders, or filenames start with the class name.")

    print(f"Saved predictions to {args.out}")


if __name__ == "__main__":
    main()
