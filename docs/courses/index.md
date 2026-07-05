# 课程索引

!!! warning "测试版提示"
    当前 Wiki 仍处于测试整理阶段，页面结构、课程说明和资料链接会继续调整。

这个页面汇总完整远程镜像中的顶层课程和栏目。Wiki 页面只做资料导航，不搬运原始 PDF、DOCX、PPTX、图片或代码。

## 全部课程 / 栏目

| 课程 / 栏目 | 页面 | 资料完整度 | README 状态 | 文件数 | 主要类型 |
| --- | --- | --- | --- | ---: | --- |
| `中国近现代史纲要` | [进入页面](modern-chinese-history.md) | 可用 | 空 README | 6 | pdf:2; md:2; docx:2 |
| `公能实践课（志愿时长、实践活动不懂看这里）` | [进入页面](public-service-practice.md) | 可用 | 可用 README | 1 | md:1 |
| `军事理论` | [进入页面](military-theory.md) | 较完整 | 较完整 README | 6 | docx:4; md:2 |
| `升学` | [进入页面](further-study.md) | 资料型归档 | 占位 README | 3 | md:2; pdf:1 |
| `大学物理` | [进入页面](college-physics.md) | 资料多但入口薄弱 | 缺少 README | 28 | pdf:24; md:3; zip:1 |
| `大学语文` | [进入页面](college-chinese.md) | 较完整 | 可用 README | 9 | pdf:4; md:3; docx:2 |
| `大物实验报告` | [进入页面](physics-experiments.md) | 较完整 | 可用 README | 45 | pdf:26; docx:12; md:4; opju:1; xlsx:1 |
| `学海无涯` | [进入页面](study-skills.md) | 可用 | 占位 README | 11 | pdf:9; md:2 |
| `微分方程与复变函数` | [进入页面](differential-equations-complex-functions.md) | 较完整 | 较完整 README | 38 | pdf:31; docx:4; md:3 |
| `思想道德与法治` | [进入页面](ideology-morality-law.md) | 可用 | 可用 README | 5 | pdf:2; docx:2; md:1 |
| `数据结构` | [进入页面](data-structures.md) | 可用 | 空 README | 4 | md:3; pdf:1 |
| `机器学习` | [进入页面](machine-learning.md) | 待补充 | 简短 README | 2 | md:2 |
| `机器视觉技术` | [进入页面](machine-vision.md) | 较完整 | 较完整 README | 0 | pdf; md; cpp; m; py |
| `概率论与数理统计` | [进入页面](probability-statistics.md) | 较完整 | 较完整 README | 37 | pdf:29; md:3; doc:3; docx:2 |
| `电路基础` | [进入页面](circuit-basics.md) | 较完整 | 可用 README | 28 | pdf:17; doc:6; md:5 |
| `痴人喃喃` | [进入页面](mental-health-notes.md) | 资料多但入口薄弱 | 占位 README | 16 | pdf:14; md:1; docx:1 |
| `离散数学` | [进入页面](discrete-math.md) | 较完整 | 较完整 README | 44 | pdf:37; md:5; docx:2 |
| `线性代数` | [进入页面](linear-algebra.md) | 较完整 | 较完整 README | 105 | pdf:95; md:6; pptx:2; docx:2 |
| `自动化与智能科学概论` | [进入页面](intro-automation-intelligent-science.md) | 较完整 | 较完整 README | 28 | docx:13; pdf:12; md:3 |
| `英语口语与写作` | [进入页面](english-speaking-writing.md) | 可用 | 可用 README | 2 | pdf:1; md:1 |
| `运筹学` | [进入页面](operations-research.md) | 可用 | 简短 README | 18 | pdf:14; md:3; docx:1 |
| `马克思主义原理` | [进入页面](marxism-principles.md) | 较完整 | 可用 README | 10 | docx:6; md:3; pdf:1 |
| `高等数学A上` | [进入页面](calculus-a-1.md) | 较完整 | 较完整 README | 38 | pdf:17; doc:14; md:4; docx:3 |
| `高等数学A下` | [进入页面](calculus-a-2.md) | 较完整 | 较完整 README | 8 | pdf:5; md:3 |
| `高级语言程序设计2-1` | [进入页面](advanced-programming-2-1.md) | 较完整 | 较完整 README | 72 | pdf:31; pptx:26; md:6; doc:6; docx:3 |
| `高级语言程序设计2-2` | [进入页面](advanced-programming-2-2.md) | 较完整 | 可用 README | 36 | docx:13; pdf:13; md:5; pptx:5 |

## 推荐先看

- 入口较完整的课程可以先看：`线性代数`、`离散数学`、`微分方程与复变函数`、`概率论与数理统计`、`高级语言程序设计2-1`。
- 入口薄弱但资料较多的栏目可以优先补：`大学物理`、`痴人喃喃`、`学海无涯`、`数据结构`。
- 专业课目前已经人工整理：`机器视觉技术`；`机器学习` 仍是轻量入口页。

## 维护说明

课程页由 `scripts/build-course-pages.py` 根据 `analysis/course_index.csv`、`analysis/readme_issues.csv` 和 `_remote_nku_ai_study` 生成。`machine-vision.md` 为人工精修页，脚本不会覆盖。
