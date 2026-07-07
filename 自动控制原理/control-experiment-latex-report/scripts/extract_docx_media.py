#!/usr/bin/env python3
"""Extract images from a DOCX and convert WMF/EMF to PNG when supported.

The script writes a manifest TSV with original DOCX media names, generated
filenames, dimensions, formats, and actions.
"""

from __future__ import annotations

import argparse
import shutil
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image


def media_sort_key(name: str) -> tuple[int, str]:
    stem = Path(name).stem
    digits = "".join(ch for ch in stem if ch.isdigit())
    return (int(digits) if digits else 0, name)


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for i in range(2, 1000):
        candidate = path.with_name(f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find unique filename for {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract DOCX media for LaTeX reports.")
    parser.add_argument("docx", type=Path, help="Source .docx file")
    parser.add_argument("--out", type=Path, required=True, help="Output image directory")
    parser.add_argument("--prefix", default="docx_media", help="Filename prefix")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    manifest_rows = ["original\toutput\tformat\tdimensions\tbytes\taction"]

    with ZipFile(args.docx) as zf:
        media_names = [
            name
            for name in zf.namelist()
            if name.startswith("word/media/") and not name.endswith("/")
        ]
        for idx, member in enumerate(sorted(media_names, key=media_sort_key), start=1):
            data = zf.read(member)
            ext = Path(member).suffix.lower()
            original_name = Path(member).name
            action = "copied"
            fmt = "unknown"
            dims = ""

            try:
                image = Image.open(BytesIO(data))
                fmt = image.format or "unknown"
                dims = f"{image.size[0]}x{image.size[1]}"
            except Exception:
                image = None

            if ext in {".wmf", ".emf"} and image is not None:
                out_path = unique_path(args.out / f"{args.prefix}_{idx:03d}_{Path(member).stem}.png")
                image.convert("RGB").save(out_path, "PNG")
                action = f"converted {ext[1:].upper()} to PNG"
            else:
                safe_ext = ext if ext else ".bin"
                out_path = unique_path(args.out / f"{args.prefix}_{idx:03d}_{Path(member).stem}{safe_ext}")
                out_path.write_bytes(data)

            manifest_rows.append(
                f"{original_name}\t{out_path.name}\t{fmt}\t{dims}\t{len(data)}\t{action}"
            )

    manifest = args.out / "media_manifest.tsv"
    manifest.write_text("\n".join(manifest_rows) + "\n", encoding="utf-8")
    print(f"Extracted {len(manifest_rows) - 1} media files to {args.out}")
    print(f"Manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
