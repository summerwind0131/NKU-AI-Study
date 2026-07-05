from __future__ import annotations

import csv
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
REMOTE_REPO = WORKSPACE_ROOT / "_remote_nku_ai_study"
ANALYSIS_DIR = WORKSPACE_ROOT / "analysis"
DOCS_DIR = REPO_ROOT / "docs"
COURSES_DIR = DOCS_DIR / "courses"

GITHUB_ROOT = "https://github.com/summerwind0131/NKU-AI-Study"
PROTECTED_SLUGS = {"machine-vision"}
LOCAL_INSERT_AFTER = "机器学习"
LOCAL_EXTRA_COURSE = "机器视觉技术"

SLUGS = {
    "线性代数": "linear-algebra",
    "高级语言程序设计2-1": "advanced-programming-2-1",
    "大物实验报告": "physics-experiments",
    "离散数学": "discrete-math",
    "微分方程与复变函数": "differential-equations-complex-functions",
    "高等数学A上": "calculus-a-1",
    "概率论与数理统计": "probability-statistics",
    "高级语言程序设计2-2": "advanced-programming-2-2",
    "大学物理": "college-physics",
    "电路基础": "circuit-basics",
    "自动化与智能科学概论": "intro-automation-intelligent-science",
    "运筹学": "operations-research",
    "痴人喃喃": "mental-health-notes",
    "学海无涯": "study-skills",
    "马克思主义原理": "marxism-principles",
    "大学语文": "college-chinese",
    "高等数学A下": "calculus-a-2",
    "中国近现代史纲要": "modern-chinese-history",
    "军事理论": "military-theory",
    "思想道德与法治": "ideology-morality-law",
    "数据结构": "data-structures",
    "升学": "further-study",
    "机器学习": "machine-learning",
    "英语口语与写作": "english-speaking-writing",
    "公能实践课（志愿时长、实践活动不懂看这里）": "public-service-practice",
    "机器视觉技术": "machine-vision",
}

LOCAL_EXTRA_ROWS = {
    "机器视觉技术": {
        "course": "机器视觉技术",
        "file_count": "0",
        "size_mb": "0.0",
        "extensions": "pdf; md; cpp; m; py",
        "subdirs": "课件; 往年真题及练习题; 机器视觉实验 sfy; 机器视觉实验by fyr; 2026 机器视觉回忆.md",
        "readme_status": "strong",
        "readme_features": "课程概览; 学习建议; 考核方式; 推荐资源; 资料说明",
        "risk_count": "0",
        "label": "较完整",
    }
}

README_NAMES = {"readme.md", "readme", "readme.markdown", "reamme.md"}
SKIP_INTRO_TITLES = {"目录", "table of contents", "贡献记录", "联系方式", "声明", "附录"}


@dataclass
class CourseRow:
    course: str
    file_count: str
    extensions: str
    subdirs: str
    readme_status: str
    readme_features: str
    risk_count: str
    label: str


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={REMOTE_REPO.as_posix()}", "-c", "core.quotepath=false", *args],
        cwd=REMOTE_REPO,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def readme_issue_map() -> dict[str, list[dict[str, str]]]:
    path = ANALYSIS_DIR / "readme_issues.csv"
    if not path.exists():
        return {}
    issues_by_course: dict[str, list[dict[str, str]]] = {}
    for row in read_csv_rows(path):
        path_value = row.get("path", "")
        course = path_value.split("/", 1)[0]
        if course:
            issues_by_course.setdefault(course, []).append(row)
    return issues_by_course


def normalize_row(row: dict[str, str]) -> CourseRow:
    return CourseRow(
        course=row["course"],
        file_count=row.get("file_count", ""),
        extensions=row.get("extensions", ""),
        subdirs=row.get("subdirs", ""),
        readme_status=row.get("readme_status", ""),
        readme_features=row.get("readme_features", ""),
        risk_count=row.get("risk_count", "0"),
        label=row.get("label", ""),
    )


def page_name(course: str) -> str:
    if course not in SLUGS:
        slug = re.sub(r"[^0-9A-Za-z_-]+", "-", course).strip("-").lower()
        return slug or "course"
    return SLUGS[course]


def ordered_course_names(rows: list[CourseRow]) -> list[str]:
    rows_by_course = {row.course: row for row in rows}
    try:
        candidates = [line.strip() for line in run_git(["ls-tree", "--name-only", "HEAD"]).splitlines()]
    except subprocess.CalledProcessError:
        candidates = [row.course for row in rows]

    ordered: list[str] = []
    for name in candidates:
        if name in rows_by_course and name not in ordered:
            ordered.append(name)
    for row in rows:
        if row.course not in ordered:
            ordered.append(row.course)

    if LOCAL_EXTRA_COURSE in ordered:
        ordered.remove(LOCAL_EXTRA_COURSE)
    if LOCAL_INSERT_AFTER in ordered:
        ordered.insert(ordered.index(LOCAL_INSERT_AFTER) + 1, LOCAL_EXTRA_COURSE)
    else:
        ordered.append(LOCAL_EXTRA_COURSE)
    return ordered


def top_level_children(course: str) -> tuple[list[str], list[str]]:
    try:
        output = run_git(["ls-tree", "HEAD", "--", f"{course}/"])
    except subprocess.CalledProcessError:
        return [], []
    dirs: list[str] = []
    files: list[str] = []
    prefix = f"{course}/"
    for line in output.splitlines():
        if not line or "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        name = path[len(prefix):] if path.startswith(prefix) else path
        parts = meta.split()
        kind = parts[1] if len(parts) > 1 else ""
        if kind == "tree":
            dirs.append(name)
        elif kind == "blob":
            files.append(name)
    return dirs, files


def all_paths_for_course(course: str) -> list[str]:
    try:
        output = run_git(["ls-tree", "-r", "--name-only", "HEAD", "--", course])
    except subprocess.CalledProcessError:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def choose_readme(course: str, paths: list[str]) -> str | None:
    direct: list[str] = []
    nested: list[str] = []
    prefix = f"{course}/"
    for path in paths:
        rel = path[len(prefix):] if path.startswith(prefix) else path
        lower_name = Path(rel).name.lower()
        if lower_name in README_NAMES:
            if "/" not in rel:
                direct.append(path)
            else:
                nested.append(path)
    if direct:
        return sorted(direct, key=lambda p: p.lower())[0]
    if nested:
        return sorted(nested, key=lambda p: (p.count("/"), p.lower()))[0]
    return None


def read_git_text(path: str) -> str:
    try:
        return run_git(["show", f"HEAD:{path}"])
    except subprocess.CalledProcessError:
        return ""


def parse_features(features: str) -> list[str]:
    return [part.strip() for part in features.split(";") if part.strip()]


def parse_semicolon_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def status_cn(status: str) -> str:
    return {
        "strong": "较完整 README",
        "usable": "可用 README",
        "minimal": "简短 README",
        "stub": "占位 README",
        "empty": "空 README",
        "missing": "缺少 README",
    }.get(status or "", status or "未知")


def github_url(path: str, kind: str) -> str:
    encoded = quote(path.replace("\\", "/"), safe="/-_.~")
    return f"{GITHUB_ROOT}/{kind}/main/{encoded}"


def md_escape_label(value: str) -> str:
    return value.replace("[", "\\[").replace("]", "\\]")


def markdown_link(label: str, path: str, kind: str) -> str:
    return f"[{md_escape_label(label)}]({github_url(path, kind)})"


def strip_markdown(line: str) -> str:
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)
    line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"`([^`]+)`", r"\1", line)
    line = line.replace("**", "").replace("__", "").replace("*", "")
    line = re.sub(r"<[^>]+>", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def should_skip_readme_line(line: str) -> bool:
    if not line:
        return True
    stripped = line.strip()
    return (
        stripped in {"---", "***", "___"}
        or stripped.startswith("|---")
        or stripped.startswith("| ---")
        or stripped.startswith("<p")
        or stripped.startswith("</p")
        or stripped.startswith("<img")
        or stripped.startswith("![")
        or "shields.io" in stripped
    )


def trim_text(value: str, max_chars: int = 180) -> str:
    value = strip_markdown(value)
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def readme_intro_sections(readme_text: str, course: str, status: str) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = "README 要点"
    current_items: list[str] = []

    def flush() -> None:
        nonlocal current_items, current_title
        cleaned = [trim_text(item) for item in current_items if trim_text(item)]
        if cleaned and current_title.lower() not in SKIP_INTRO_TITLES:
            sections.append((current_title, cleaned[:3]))
        current_items = []

    for raw in readme_text.splitlines():
        line = raw.strip()
        if should_skip_readme_line(line):
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            title = strip_markdown(heading_match.group(2)).strip()
            if title and title != course:
                flush()
                current_title = title
            continue
        if line.startswith("|"):
            continue
        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+[.)]\s+", "", line)
        if line:
            current_items.append(line)
    flush()

    total_chars = sum(len(item) for _, items in sections for item in items)
    if status in {"empty", "missing"} and total_chars < 30:
        return []
    if status == "stub" and total_chars < 50:
        return []
    return sections[:4]


def has_learning_material(row: CourseRow) -> bool:
    blob = " ".join([row.subdirs, row.extensions, row.course])
    return any(word in blob for word in ["作业", "答案", "报告", "真题", "论文", "实验"])


def usage_advice(row: CourseRow, dirs: list[str], files: list[str]) -> list[str]:
    advice: list[str] = []
    status = row.readme_status
    label = row.label
    dirs_blob = " ".join(dirs + files + parse_semicolon_list(row.subdirs))
    if status == "strong":
        advice.append("先读课程 README 中的课程介绍和学习建议，再按资料目录进入课件、练习题、往年题或作业资料。")
        advice.append("README 已经包含较多课程说明，适合把它当作本栏目入口。")
    elif status in {"usable", "minimal"}:
        advice.append("先看已有 README 获取基本方向，再结合本页资料链接判断具体用途。")
        advice.append("如果继续完善 Wiki，建议优先补充课程简介、考核方式和推荐阅读顺序。")
    else:
        advice.append("当前入口说明偏弱，建议先从资料目录和文件名判断内容类型。")
        advice.append("本页只依据真实 README 和目录结构整理，不补写没有来源的学习经验。")
    if any(word in dirs_blob for word in ["课件", "PPT", "PPT（from lzx）"]):
        advice.append("复习时先用课件确认本年度讲授范围，再看题目或报告类资料。")
    if any(word in dirs_blob for word in ["往年", "真题", "回忆"]):
        advice.append("往年题和回忆题适合熟悉题型，不建议当作唯一复习范围。")
    if has_learning_material(row):
        advice.append("涉及作业、答案、报告或论文的资料只适合学习参考，不能直接照抄提交。")
    if "入口薄弱" in label or status in {"missing", "empty", "stub"}:
        advice.append("本页以客观索引为主，后续应优先补充可靠的一手课程经验。")
    return advice


def todo_items(row: CourseRow) -> list[str]:
    todos: list[str] = []
    if row.readme_status in {"missing", "empty", "stub", "minimal"}:
        todos.append("补充课程简介、适用年份和任课老师差异。")
        todos.append("补充推荐阅读顺序和考核方式。")
    if row.readme_status in {"missing", "empty"}:
        todos.append("为原目录补一份可用 README。")
    if not parse_features(row.readme_features):
        todos.append("补充资料说明，标明哪些文件适合复习、哪些只适合作参考。")
    if "待补充" in row.label or "入口薄弱" in row.label:
        todos.append("优先补齐 Wiki 页面中的学习建议和资料边界。")
    if not todos:
        todos.append("后续可补充适用年份、老师差异和更细的复习路线。")
    return todos


def md_list(items: list[str], empty: str = "暂无可列项目。") -> str:
    if not items:
        return f"- {empty}\n"
    return "".join(f"- {item}\n" for item in items)


def resource_entries(course: str, names: list[str], kind: str, max_items: int = 10) -> list[str]:
    entries: list[str] = []
    for name in names[:max_items]:
        path = f"{course}/{name}"
        display_path = f"{path}/" if kind == "tree" else path
        entries.append(f"{markdown_link(name, path, kind)}：`{display_path}`")
    return entries


def generate_intro_section(course: str, row: CourseRow, readme_path: str | None, readme_text: str) -> str:
    lines = ["## 课程介绍\n\n"]
    if readme_path:
        lines.append(f"> 主要参考：`{readme_path}`\n\n")
    else:
        lines.append("> 当前未找到课程根 README，本节只说明资料状态，不补写没有来源的课程经验。\n\n")

    sections = readme_intro_sections(readme_text, course, row.readme_status) if readme_text else []
    if not sections:
        lines.append(
            f"当前 README 状态为 `{status_cn(row.readme_status)}`，可提取的课程介绍有限。本页暂以真实目录和资料链接为主，后续适合补充课程简介、学习路线、考核方式和适用年份。\n"
        )
        return "".join(lines)

    for title, items in sections:
        lines.append(f"### {title}\n\n")
        for item in items:
            lines.append(f"- {item}\n")
        lines.append("\n")
    return "".join(lines).rstrip() + "\n"


def generate_resource_section(row: CourseRow, dirs: list[str], files: list[str]) -> str:
    course = row.course
    notable_files = [f for f in files if Path(f).name.lower() not in README_NAMES][:8]
    extensions = parse_semicolon_list(row.extensions)
    features = parse_features(row.readme_features)

    lines = ["\n## 仓库资料与链接\n\n"]
    lines.append(f"- 原始目录：{markdown_link(course + '/', course, 'tree')}（`{course}/`）\n")
    lines.append(f"- 资料完整度：`{row.label or '未知'}`\n")
    lines.append(f"- README 状态：`{status_cn(row.readme_status)}`\n")
    lines.append(f"- 文件数量：`{row.file_count or '未知'}`\n")
    if extensions:
        lines.append(f"- 主要类型：{'; '.join(f'`{item}`' for item in extensions)}\n")
    if features:
        lines.append(f"- 已识别内容要素：{'; '.join(f'`{item}`' for item in features)}\n")

    lines.append("\n### 顶层目录\n\n")
    lines.append(md_list(resource_entries(course, dirs, "tree"), "当前没有顶层子目录。"))
    if len(dirs) > 10:
        lines.append(f"\n> 另有 {len(dirs) - 10} 个顶层目录未在此处展开。\n")

    lines.append("\n### 代表文件\n\n")
    lines.append(md_list(resource_entries(course, notable_files, "blob", 8), "当前没有可直接列出的顶层代表文件。"))
    return "".join(lines)


def generate_issue_section(issues: list[dict[str, str]]) -> str:
    lines = ["\n## README 维护提示\n\n"]
    if not issues:
        lines.append("- 暂未在 `analysis/readme_issues.csv` 中发现空、占位或过短 README。\n")
        return "".join(lines)
    issue_notes = [
        f"`{issue.get('path', '')}`：{status_cn(issue.get('status', ''))}，{issue.get('chars', '0')} 字符"
        for issue in issues[:8]
    ]
    lines.append(md_list(issue_notes))
    if len(issues) > 8:
        lines.append(f"\n> 另有 {len(issues) - 8} 条 README 维护提示未在此处展开。\n")
    return "".join(lines)


def generate_course_page(row: CourseRow, issues: list[dict[str, str]] | None = None) -> str:
    issues = issues or []
    course = row.course
    paths = all_paths_for_course(course)
    readme_path = choose_readme(course, paths)
    readme_text = read_git_text(readme_path) if readme_path else ""
    dirs, files = top_level_children(course)
    advice = usage_advice(row, dirs, files)
    todos = todo_items(row)
    if issues:
        todos.append("处理 `analysis/readme_issues.csv` 中记录的空、占位或过短 README。")

    lines: list[str] = [f"# {course}\n\n"]
    lines.append(generate_intro_section(course, row, readme_path, readme_text))
    lines.append(generate_resource_section(row, dirs, files))
    lines.append(generate_issue_section(issues))
    lines.append("\n## 使用建议\n\n")
    lines.append(md_list(advice))
    lines.append("\n## 待补充\n\n")
    lines.append(md_list(todos))
    lines.append("\n## 资料边界\n\n")
    lines.append(
        "本页只做资料导航和客观说明。PDF、DOCX、PPTX、图片、压缩包等原始资料不在 Wiki 中搬运；涉及作业、答案、实验报告、论文或个人材料的内容仅供学习参考，不得照抄、倒卖或违规使用。不同年份老师要求可能变化，请以当年课程要求为准。\n"
    )
    return "".join(lines)


def page_link(course: str) -> str:
    return f"[进入页面]({page_name(course)}.md)"


def generate_index(rows_by_course: dict[str, CourseRow], order: list[str]) -> str:
    lines = [
        "# 课程索引\n\n",
        "!!! warning \"测试版提示\"\n",
        "    当前 Wiki 仍处于测试整理阶段，页面结构、课程说明和资料链接会继续调整。\n\n",
        "这个页面汇总完整远程镜像中的顶层课程和栏目。Wiki 页面只做资料导航，不搬运原始 PDF、DOCX、PPTX、图片或代码。\n\n",
        "## 全部课程 / 栏目\n\n",
        "| 课程 / 栏目 | 页面 | 资料完整度 | README 状态 | 文件数 | 主要类型 |\n",
        "| --- | --- | --- | --- | ---: | --- |\n",
    ]
    for course in order:
        row = rows_by_course.get(course)
        if not row:
            continue
        ext = row.extensions or "-"
        lines.append(
            f"| `{course}` | {page_link(course)} | {row.label or '未知'} | {status_cn(row.readme_status)} | {row.file_count or '-'} | {ext} |\n"
        )
    lines.extend([
        "\n## 推荐先看\n\n",
        "- 入口较完整的课程可以先看：`线性代数`、`离散数学`、`微分方程与复变函数`、`概率论与数理统计`、`高级语言程序设计2-1`。\n",
        "- 入口薄弱但资料较多的栏目可以优先补：`大学物理`、`痴人喃喃`、`学海无涯`、`数据结构`。\n",
        "- 专业课目前已经人工整理：`机器视觉技术`；`机器学习` 仍是轻量入口页。\n",
        "\n## 维护说明\n\n",
        "课程页由 `scripts/build-course-pages.py` 根据 `analysis/course_index.csv`、`analysis/readme_issues.csv` 和 `_remote_nku_ai_study` 生成。`machine-vision.md` 为人工精修页，脚本不会覆盖。\n",
    ])
    return "".join(lines)


def generate_home() -> str:
    return r"""# NKU-AI-Study Wiki（测试版）

!!! warning "测试版提示"
    当前 Wiki 仍处于测试整理阶段，内容和导航会继续调整；请以课程 README、仓库原始资料和当年老师要求为准。

这是一份面向南开大学人工智能学院同学的学习资料导航。它不是课程资料的替代品，而是把仓库里的课程经验、复习资料、实验报告、代码链接和避坑提醒整理成更容易阅读的 Wiki。

## 这份 Wiki 想解决什么

- 让新同学快速知道每门课有哪些资料、应该先看什么。
- 把零散 README、课件、往年题和实验代码组织成稳定入口。
- 记录真实学习体验：哪些内容值得重点复习，哪些资料只适合作参考。
- 保留资料边界：不承诺高分，不鼓励照抄，不替代当年老师要求。

## 资料总览

- [课程索引](courses/index.md)：直接进入全部课程和栏目主页，查看完整度、README 状态和资料类型。
- [机器视觉技术](courses/machine-vision.md)：当前人工精修程度最高的专业课页面。
- [课程页模板](page-templates/course-template.md)：后续手动补课程页时可以沿用的结构。

## 推荐先看

- 想找资料入口：先看 [课程索引](courses/index.md)，再直接进入具体课程/栏目主页。
- 想看完整示例：先看 [机器视觉技术](courses/machine-vision.md)。
- 想了解使用边界：先看 [使用指南](usage.md)。

## 待补充重点

入口薄弱但资料不少的栏目包括 `大学物理`、`数据结构`、`学海无涯`、`痴人喃喃`。这些页面目前以 README 和目录结构为基础，后续适合继续补充学习路线、适用年份和资料说明。

## 本地预览

推荐使用启动脚本：

```powershell
.\scripts\serve-wiki.ps1
```

换端口：

```powershell
.\scripts\serve-wiki.ps1 -Port 8001
```

如果本机 PowerShell 执行策略拦截脚本，可以使用：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\serve-wiki.ps1
```

也可以手动运行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m mkdocs serve -a 127.0.0.1:8000
```

构建检查：

```powershell
.\.venv\Scripts\python.exe -m mkdocs build --strict
```
"""


def yaml_q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def generate_mkdocs(order: list[str]) -> str:
    lines = [
        "site_name: NKU-AI-Study Wiki（测试版）\n",
        "site_author: summerwind0131\n",
        "site_description: 南开大学人工智能学院学习资料、课程经验与生存指南\n",
        "site_url: https://summerwind0131.github.io/NKU-AI-Study/\n\n",
        "repo_name: summerwind0131/NKU-AI-Study\n",
        "repo_url: https://github.com/summerwind0131/NKU-AI-Study\n\n",
        "theme:\n",
        "  name: material\n",
        "  custom_dir: overrides\n",
        "  language: zh\n",
        "  features:\n",
        "    - navigation.instant\n",
        "    - navigation.tracking\n",
        "    - navigation.top\n",
        "    - search.highlight\n",
        "    - search.share\n",
        "    - search.suggest\n",
        "    - content.code.copy\n",
        "    - content.code.annotate\n",
        "  palette:\n",
        "    - media: \"(prefers-color-scheme: light)\"\n",
        "      scheme: default\n",
        "      primary: light blue\n",
        "      accent: deep purple\n",
        "      toggle:\n",
        "        icon: material/weather-sunny\n",
        "        name: 切换到深色模式\n",
        "    - media: \"(prefers-color-scheme: dark)\"\n",
        "      scheme: slate\n",
        "      primary: cyan\n",
        "      accent: deep purple\n",
        "      toggle:\n",
        "        icon: material/weather-night\n",
        "        name: 切换到浅色模式\n",
        "  font:\n",
        "    text: Roboto Slab\n",
        "    code: Roboto Mono\n",
        "  icon:\n",
        "    repo: fontawesome/brands/github\n\n",
        "markdown_extensions:\n",
        "  - admonition\n",
        "  - attr_list\n",
        "  - footnotes\n",
        "  - md_in_html\n",
        "  - toc:\n",
        "      permalink: true\n",
        "  - pymdownx.details\n",
        "  - pymdownx.highlight:\n",
        "      anchor_linenums: true\n",
        "  - pymdownx.inlinehilite\n",
        "  - pymdownx.superfences\n\n",
        "plugins:\n",
        "  - search:\n",
        "      lang:\n",
        "        - zh\n",
        "        - en\n\n",
        "nav:\n",
        "  - 首页: index.md\n",
        "  - 使用指南: usage.md\n",
        "  - 课程索引:\n",
        "      - 总览: courses/index.md\n",
    ]
    for course in order:
        lines.append(f"      - {yaml_q(course)}: courses/{page_name(course)}.md\n")
    lines.extend([
        "  - 模板:\n",
        "      - 课程页模板: page-templates/course-template.md\n",
    ])
    return "".join(lines)


def main() -> None:
    if not REMOTE_REPO.exists():
        raise SystemExit(f"Remote mirror not found: {REMOTE_REPO}")
    if not (ANALYSIS_DIR / "course_index.csv").exists():
        raise SystemExit("analysis/course_index.csv not found")

    rows = [normalize_row(row) for row in read_csv_rows(ANALYSIS_DIR / "course_index.csv")]
    rows_by_course = {row.course: row for row in rows}
    rows_by_course[LOCAL_EXTRA_COURSE] = normalize_row(LOCAL_EXTRA_ROWS[LOCAL_EXTRA_COURSE])
    order = ordered_course_names(rows)
    issues_by_course = readme_issue_map()
    COURSES_DIR.mkdir(parents=True, exist_ok=True)

    for row in rows:
        slug = page_name(row.course)
        if slug in PROTECTED_SLUGS:
            continue
        (COURSES_DIR / f"{slug}.md").write_text(
            generate_course_page(row, issues_by_course.get(row.course, [])),
            encoding="utf-8",
            newline="\n",
        )

    (COURSES_DIR / "index.md").write_text(generate_index(rows_by_course, order), encoding="utf-8", newline="\n")
    (DOCS_DIR / "index.md").write_text(generate_home(), encoding="utf-8", newline="\n")
    (REPO_ROOT / "mkdocs.yml").write_text(generate_mkdocs(order), encoding="utf-8", newline="\n")

    generated = len(rows) - len([row for row in rows if page_name(row.course) in PROTECTED_SLUGS])
    print(f"Generated {generated} course pages plus flat course index and mkdocs nav.")
    print("Protected pages:", ", ".join(sorted(PROTECTED_SLUGS)))


if __name__ == "__main__":
    main()