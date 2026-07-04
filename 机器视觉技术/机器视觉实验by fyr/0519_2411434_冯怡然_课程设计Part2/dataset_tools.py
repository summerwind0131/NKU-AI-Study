from __future__ import annotations

import argparse
import io
import json
import random
import shutil
import tarfile
import urllib.request
import hashlib
from pathlib import Path
from zipfile import ZipFile

from PIL import Image


CLASSES = ["A", "B", "C", "Five", "Point", "V"]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff", ".ppm", ".pgm", ".pnm"}
MARCEL_TEST_URL = "https://www.idiap.ch/resource/gestures/data/shp_marcel_test.tar.gz"
MARCEL_TRAIN_URL = "https://www.idiap.ch/resource/gestures/data/shp_marcel_train.tar.gz"


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def remove_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def class_from_path(path: Path, root: Path | None = None) -> str | None:
    try:
        rel = path.relative_to(root) if root is not None else path
    except ValueError:
        rel = path

    parts = [p for p in rel.parts if p]
    lowered = [p.lower() for p in parts]
    for cls in CLASSES:
        if cls.lower() in lowered:
            return cls

    stem = path.stem.lower()
    for cls in sorted(CLASSES, key=len, reverse=True):
        if stem.startswith(cls.lower()):
            return cls
    return None


def verify_image_bytes(raw: bytes) -> bool:
    try:
        with Image.open(io.BytesIO(raw)) as image:
            image.verify()
        return True
    except Exception:
        return False


def verify_image_file(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def image_hash(path: Path) -> str | None:
    try:
        with Image.open(path) as image:
            image = image.convert("RGB")
            return hashlib.sha256(image.tobytes() + str(image.size).encode()).hexdigest()
    except Exception:
        return None


def course_hashes(course_dir: Path) -> set[str]:
    hashes: set[str] = set()
    for split in ["train", "val"]:
        split_dir = course_dir / split
        if not split_dir.exists():
            continue
        for image_path in sorted(p for p in split_dir.rglob("*") if is_image(p)):
            digest = image_hash(image_path)
            if digest is not None:
                hashes.add(digest)
    return hashes


def prepare_course_zip(zip_path: Path, out_dir: Path, val_ratio: float, seed: int, overwrite: bool) -> None:
    if out_dir.exists():
        if not overwrite:
            print(f"{out_dir} already exists. Nothing to do. Add --overwrite to rebuild it.")
            return
        remove_dir(out_dir)

    for split in ["train", "val"]:
        for cls in CLASSES:
            (out_dir / split / cls).mkdir(parents=True, exist_ok=True)

    random.seed(seed)
    summary = {"seed": seed, "val_ratio": val_ratio, "classes": CLASSES, "counts": {}}
    with ZipFile(zip_path) as zf:
        image_names = [name for name in zf.namelist() if Path(name).suffix.lower() in IMAGE_EXTENSIONS]
        for cls in CLASSES:
            members = [name for name in image_names if f"/{cls}/" in name.replace("\\", "/")]
            members.sort()
            random.shuffle(members)
            val_count = max(1, round(len(members) * val_ratio))
            counts = {"train": 0, "val": 0, "skipped": 0}

            for index, member in enumerate(members):
                split = "val" if index < val_count else "train"
                raw = zf.read(member)
                if not verify_image_bytes(raw):
                    counts["skipped"] += 1
                    continue
                target = out_dir / split / cls / Path(member).name
                target.write_bytes(raw)
                counts[split] += 1
            summary["counts"][cls] = counts

    reports_dir = out_dir.parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "dataset_split.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def prepare_marcel(
    source: Path,
    out_dir: Path,
    overwrite: bool,
    download: bool,
    use_train_archive: bool,
    background: str,
) -> None:
    if download:
        source.parent.mkdir(parents=True, exist_ok=True)
        url = MARCEL_TRAIN_URL if use_train_archive else MARCEL_TEST_URL
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, source)
        print(f"Saved to {source}")

    if out_dir.exists():
        if not overwrite:
            print(f"{out_dir} already exists. Nothing to do. Add --overwrite to rebuild it.")
            return
        remove_dir(out_dir)

    for cls in CLASSES:
        (out_dir / cls).mkdir(parents=True, exist_ok=True)

    counts = {cls: 0 for cls in CLASSES}
    if source.is_dir():
        image_iter = sorted(p for p in source.rglob("*") if is_image(p) and matches_background(p, source, background))
        for image_path in image_iter:
            cls = class_from_path(image_path, source)
            if cls is None:
                continue
            save_converted_image(image_path, out_dir / cls, cls, counts)
    else:
        if not source.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        with tarfile.open(source, "r:gz") as tf:
            for member in tf.getmembers():
                if not member.isfile() or Path(member.name).suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                if not matches_background(Path(member.name), None, background):
                    continue
                cls = class_from_path(Path(member.name))
                if cls is None:
                    continue
                extracted = tf.extractfile(member)
                if extracted is None:
                    continue
                try:
                    with Image.open(extracted) as img:
                        img = img.convert("RGB")
                        counts[cls] += 1
                        img.save(out_dir / cls / f"{cls}_external_{counts[cls]:04d}.png")
                except Exception as exc:
                    print(f"Skipped {member.name}: {exc}")

    print("Prepared Marcel-style external test set:")
    for cls in CLASSES:
        print(f"{cls}: {counts[cls]}")
    print(f"Output: {out_dir}")


def matches_background(path: Path, root: Path | None, background: str) -> bool:
    if background == "all":
        return True
    try:
        rel = path.relative_to(root) if root is not None else path
    except ValueError:
        rel = path
    parts = [p.lower() for p in rel.parts]
    return background.lower() in parts


def save_converted_image(image_path: Path, target_dir: Path, cls: str, counts: dict[str, int]) -> None:
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            counts[cls] += 1
            img.save(target_dir / f"{cls}_external_{counts[cls]:04d}.png")
    except Exception as exc:
        print(f"Skipped {image_path}: {exc}")


def dedupe_imagefolder(source_dir: Path, course_dir: Path, out_dir: Path, overwrite: bool) -> None:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source folder not found: {source_dir}")
    if not course_dir.exists():
        raise FileNotFoundError(f"Course dataset not found: {course_dir}")
    if out_dir.exists():
        if not overwrite:
            print(f"{out_dir} already exists. Nothing to do. Add --overwrite to rebuild it.")
            return
        remove_dir(out_dir)

    known_hashes = course_hashes(course_dir)
    counts = {cls: {"total": 0, "removed": 0, "kept": 0} for cls in CLASSES}
    for cls in CLASSES:
        (out_dir / cls).mkdir(parents=True, exist_ok=True)

    for image_path in sorted(p for p in source_dir.rglob("*") if is_image(p)):
        cls = class_from_path(image_path, source_dir)
        if cls is None:
            continue
        counts[cls]["total"] += 1
        digest = image_hash(image_path)
        if digest is None or digest in known_hashes:
            counts[cls]["removed"] += 1
            continue
        counts[cls]["kept"] += 1
        target = out_dir / cls / image_path.name
        suffix = 1
        while target.exists():
            target = out_dir / cls / f"{image_path.stem}_{suffix}{image_path.suffix}"
            suffix += 1
        shutil.copy2(image_path, target)

    summary = {"source": str(source_dir), "course": str(course_dir), "out": str(out_dir), "counts": counts}
    (out_dir / "dedupe_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def add_extra_images(base_dir: Path, extra_dir: Path, out_dir: Path, split: str, overwrite: bool) -> None:
    if not base_dir.exists():
        raise FileNotFoundError(f"Base dataset not found: {base_dir}")
    if not extra_dir.exists():
        raise FileNotFoundError(f"Extra image folder not found: {extra_dir}")
    if out_dir.exists():
        if not overwrite:
            raise FileExistsError(f"{out_dir} already exists. Add --overwrite to rebuild it.")
        remove_dir(out_dir)

    shutil.copytree(base_dir, out_dir)
    counts = {cls: 0 for cls in CLASSES}
    skipped: list[str] = []
    for image_path in sorted(p for p in extra_dir.rglob("*") if is_image(p)):
        cls = class_from_path(image_path, extra_dir)
        if cls is None or not verify_image_file(image_path):
            skipped.append(str(image_path))
            continue
        target_dir = out_dir / split / cls
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"extra_{image_path.stem}{image_path.suffix.lower()}"
        suffix = 1
        while target.exists():
            target = target_dir / f"extra_{image_path.stem}_{suffix}{image_path.suffix.lower()}"
            suffix += 1
        shutil.copy2(image_path, target)
        counts[cls] += 1

    summary = {
        "base": str(base_dir),
        "extra": str(extra_dir),
        "out": str(out_dir),
        "split": split,
        "added": counts,
        "skipped": skipped,
    }
    (out_dir / "extra_images_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dataset utilities for the hand posture project.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    course = subparsers.add_parser("course", help="Prepare train/val ImageFolder data from the course ZIP.")
    course.add_argument("--zip", type=Path, default=Path(r"C:\Users\AliceJFeng\Downloads\Hand_Posture_Hard_Stu.zip"))
    course.add_argument("--out", type=Path, default=Path("data/hand_posture"))
    course.add_argument("--val-ratio", type=float, default=0.2)
    course.add_argument("--seed", type=int, default=42)
    course.add_argument("--overwrite", action="store_true")

    marcel = subparsers.add_parser("marcel", help="Prepare the Marcel-style external test set.")
    marcel.add_argument("--source", type=Path, default=Path("external_downloads/Marcel-Test"))
    marcel.add_argument("--out", type=Path, default=Path("external_tests/marcel_official_test"))
    marcel.add_argument("--download", action="store_true")
    marcel.add_argument("--use-train-archive", action="store_true")
    marcel.add_argument("--background", choices=["all", "complex", "uniform"], default="all")
    marcel.add_argument("--overwrite", action="store_true")

    extra = subparsers.add_parser("add-extra", help="Add extra labeled images into a copy of the training dataset.")
    extra.add_argument("--base", type=Path, default=Path("data/hand_posture"))
    extra.add_argument("--extra", type=Path, default=Path("TestImages"))
    extra.add_argument("--out", type=Path, default=Path("data/hand_posture_plus"))
    extra.add_argument("--split", choices=["train", "val"], default="train")
    extra.add_argument("--overwrite", action="store_true")

    dedupe = subparsers.add_parser("dedupe", help="Remove images that already appear in the course train/val data.")
    dedupe.add_argument("--source", type=Path, required=True)
    dedupe.add_argument("--course", type=Path, default=Path("data/hand_posture"))
    dedupe.add_argument("--out", type=Path, required=True)
    dedupe.add_argument("--overwrite", action="store_true")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "course":
        prepare_course_zip(args.zip, args.out, args.val_ratio, args.seed, args.overwrite)
    elif args.command == "marcel":
        prepare_marcel(args.source, args.out, args.overwrite, args.download, args.use_train_archive, args.background)
    elif args.command == "add-extra":
        add_extra_images(args.base, args.extra, args.out, args.split, args.overwrite)
    elif args.command == "dedupe":
        dedupe_imagefolder(args.source, args.course, args.out, args.overwrite)


if __name__ == "__main__":
    main()
