# NKU-AI-Study Wiki（测试版）

!!! warning "测试版提示"
    当前 Wiki 仍处于测试整理阶段，内容和导航会继续调整；请以课程 README、仓库原始资料和当年老师要求为准。

这是一份面向南开大学人工智能学院同学的学习资料导航。它不是课程资料的替代品，而是把仓库里的课程经验、复习资料、实验报告、代码链接和避坑提醒整理成更容易阅读的 Wiki。

## 这份 Wiki 想解决什么

- 让新同学快速知道每门课有哪类资料、应该先看什么。
- 把零散 README、课件、往年题、实验代码和专题资料组织成稳定入口。
- 记录真实学习体验：哪些内容值得重点复习，哪些资料只适合作参考。
- 保留资料边界：不承诺高分，不鼓励照抄，不替代当年老师要求。

## 资料总览

- [课程索引](courses/index.md)：直接进入全部课程和栏目主页，查看整理状态、完整度、README 状态和资料类型。
- [机器视觉技术](courses/machine-vision.md)：当前人工精修程度最高的专业课页面。
- [课程页模板](page-templates/course-template.md)：后续手动补课程页时可以沿用的结构。

## 推荐先看

- 想看精修样例：先看 [机器视觉技术](courses/machine-vision.md)、[线性代数](courses/linear-algebra.md)、[高级语言程序设计2-1](courses/advanced-programming-2-1.md)。
- 想补大一基础课：继续看 [离散数学](courses/discrete-math.md)、[高等数学A上](courses/calculus-a-1.md)、[高等数学A下](courses/calculus-a-2.md)、[概率论与数理统计](courses/probability-statistics.md)。
- 想找薄弱入口的资料导航：看 [大学物理](courses/college-physics.md)、[数据结构](courses/data-structures.md)、[机器学习](courses/machine-learning.md)。
- 想看学习方法和心理/生存资料：看 [学海无涯](courses/study-skills.md)、[痴人喃喃](courses/mental-health-notes.md)。
- 想了解使用边界：先看 [使用指南](usage.md)。

## 待补充重点

当前已经补强了第一批课程页和第二批入口页。后续可继续补 `中国近现代史纲要`、`升学`、`运筹学` 等入口较薄页面，也可以把 `大学物理`、`数据结构`、`机器学习` 继续向“章节路线”和“适用年份”方向细化。

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
