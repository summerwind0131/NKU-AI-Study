# control-experiment-latex-report

这是一个用于生成“自动控制/控制理论实验报告”的 Codex Skill。它可以根据 DOCX 示例报告、PDF 实验指导书和 LaTeX 模板，辅助生成中文控制实验报告，并完成图片提取、内容整理、XeLaTeX 编译和基础检查。

## 使用方法（示例）

将整个 `control-experiment-latex-report` 文件夹放到 Codex 的 skills 目录：

```text
C:\Users\<用户名>\.codex\skills\
```

重启 Codex 或新开对话后，可以这样使用：
Use $control-experiment-latex-report，根据我的 DOCX 示例、PDF 实验指导书和 LaTeX 模板，生成控制实验八报告。
我的姓名是 xxx，学号是 xxx。

## 依赖

建议提前安装 Python、Pillow、XeLaTeX，以及 Poppler 工具中的 pdfinfo、pdftotext、pdftoppm。

## 说明

请注意原版skill需要上传的内容，如果初次使用可以与ai对话弄清此skill使用方法，以及根据个人需求作出更改
