---
name: control-experiment-latex-report
description: Use when creating or revising automatic-control/control-theory experiment LaTeX reports from DOCX examples, PDF lab guides, and user-provided LaTeX templates, especially when extracting DOCX result/principle images, correcting report content from a guide, compiling with XeLaTeX, and naming deliverables like studentid_name_控制实验八 with Chinese numeral experiment numbers.
---

# Control Experiment LaTeX Report

## Overview

Use this skill to turn control experiment source materials into a polished LaTeX report. Typical inputs are a DOCX reference report or template, a PDF lab manual, user metadata, and a LaTeX skeleton.

Prefer the PDF lab guide as the technical authority and the DOCX as the structure/image source. Do not reuse another student's name, ID, date, or invented measurement values.

## Workflow

1. **Ground the sources**
   - Verify all referenced DOCX/PDF/template paths exist.
   - Inspect DOCX paragraphs and image order with `zipfile`/OOXML or `python-docx`.
   - Extract the relevant PDF experiment pages with `pdftotext`; use `pdfinfo` to confirm page count.
   - If DOCX and PDF conflict on technical details, use the PDF unless the user explicitly says otherwise.

2. **Set naming and metadata**
   - Name final files as `<student_id>_<student_name>_控制实验<中文数字>.tex` and `.pdf`, for example `123456_张三_控制实验八.tex`.
   - Use Chinese numerals for the experiment number by default: 一, 二, 三, 四, 五, 六, 七, 八, 九, 十, 十一, 十二, etc.
   - Fill the report header with the user's metadata, not the DOCX author's metadata.

3. **Extract and organize images**
   - Use `scripts/extract_docx_media.py` to extract DOCX media into a local figures directory.
   - Convert WMF/EMF principle and circuit diagrams to PNG when PIL supports them; preserve JPEG/PNG result screenshots.
   - Inspect extracted images, remove duplicates from the report plan, and rename selected files descriptively, for example `fig8_1_3_second_order_feedback_circuit.png`.
   - Insert principle diagrams, circuit diagrams, and experiment result screenshots directly in LaTeX with stable relative paths.

4. **Write the LaTeX report**
   - Preserve the user's LaTeX template style unless it prevents compilation.
   - Fill these sections at minimum: 实验目的, 实验内容, 实验原理与参数设计, 实验步骤, 实验结果与分析, 实验反思.
   - Re-typeset key formulas in LaTeX instead of screenshotting formulas when practical.
   - Include state equations, controllability checks, desired pole choices, characteristic equations, feedback gains, and experimental device/unit settings.
   - Keep result analysis tied to observed curves: response speed, overshoot, stability, settling behavior, and likely error sources.

5. **Compile and verify**
   - Run `xelatex` at least twice.
   - Check that every `\includegraphics{}` file exists through `\graphicspath` or direct relative paths.
   - Check logs for missing files, undefined references, and fatal errors.
   - Use `pdfinfo` for page count and `pdftotext` for required section names.
   - When possible, render pages with `pdftoppm` and visually inspect a contact sheet for missing images, overflow, large blank gaps, or mismatched captions.

## Quality Rules

- Report completeness matters: do not leave template sections empty.
- Use PDF guide wording for experiment steps, devices, and parameters when available.
- Do not fabricate precise measurements from screenshots; qualitative analysis is acceptable when curves are the only data source.
- Keep figures standard: centered, readable, captioned, and referenced near relevant analysis.
- If old files are locked and cannot be renamed/deleted, generate the correctly named final files and mention the locked leftover.

## Useful Commands

```powershell
python scripts/extract_docx_media.py "source.docx" --out "figures/experiment8"
xelatex -interaction=nonstopmode -halt-on-error -file-line-error "123456_张三_控制实验八.tex"
pdfinfo "123456_张三_控制实验八.pdf"
pdftotext -enc UTF-8 "guide.pdf" -
```
