# 算法设计与分析

## 课程速览

| 项目 | 信息 |
| --- | --- |
| 资料完整度 | 较完整 |
| README 状态 | 较完整 README |
| 文件数量 | 20 |
| 主要类型 | `pdf:9`；`png:4`；`md:3`；`cpp:2`；`py:1`；`jpg:1` |

## 课程介绍

> 主要参考：`算法设计与分析/README.md`、`算法设计与分析/Princeton slides/README.md`、`算法设计与分析/2026年算法期末题回忆.md`、目录和文件名。

课程教材为 Kleinberg 与 Tardos 的 *Algorithm Design*，课内范围为教材前八章：稳定匹配、算法分析基础、图、贪心、分治、动态规划、网络流、NP 与计算难解性。根 README 建议直接读英文原版，中文译本质量较差；教材的证明比 PPT 更详细，课后题也有一定难度。

README 强调这门课的重点是体会算法思想，而不只是掌握 PPT 内容；加深理解最好的方式是自己手写代码，推荐刷洛谷、力扣相关题单。README 中逐章说明了需要掌握的内容，例如贪心的核心在于提出策略并证明其最优，动态规划需要积累合并策略。

## 仓库资料与链接

- [原始目录](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90)：`算法设计与分析/`
- [Princeton slides](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/Princeton%20slides)：与教材配套的公开课件，覆盖算法分析、图、贪心、分治、动态规划、最大流。
- [2026年算法期末题回忆](https://github.com/summerwind0131/NKU-AI-Study/blob/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/2026%E5%B9%B4%E7%AE%97%E6%B3%95%E6%9C%9F%E6%9C%AB%E9%A2%98%E5%9B%9E%E5%BF%86.md)：按章节整理的回忆版考点。
- [算法设计答案](https://github.com/summerwind0131/NKU-AI-Study/blob/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E7%AD%94%E6%A1%88.pdf)：课后题参考答案（约 21 MB）。
- [期末实验报告-fyr](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/%E6%9C%9F%E6%9C%AB%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-fyr) 与 [算法实验报告](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/%E7%AE%97%E6%B3%95%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A)：最小生成树相关的实验报告与代码。
- 文件数量：`20`；主要类型：`pdf:9`、`png:4`、`md:3`、`cpp:2`。

## 推荐阅读顺序

1. [根 README](https://github.com/summerwind0131/NKU-AI-Study/blob/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/README.md)：先看各章节要点、推荐资源和备考策略。
2. 教材原版与 [Princeton slides](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/Princeton%20slides)：按章节学习，课件比课内 PPT 更适合自学。
3. 课后题与 [算法设计答案](https://github.com/summerwind0131/NKU-AI-Study/blob/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E7%AD%94%E6%A1%88.pdf)：先独立思考再对照答案。
4. [2026年算法期末题回忆](https://github.com/summerwind0131/NKU-AI-Study/blob/main/%E7%AE%97%E6%B3%95%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/2026%E5%B9%B4%E7%AE%97%E6%B3%95%E6%9C%9F%E6%9C%AB%E9%A2%98%E5%9B%9E%E5%BF%86.md)：熟悉题型和考查方式。

## 备考 / 作业提醒

- README 指出较难的是贪心、分治和动态规划三道题，但期末一般出较经典的题目，难度低于作业题。
- 答题过程要写清楚：给出严谨的伪代码，证明完整不跳步，只写文字描述得分很少。
- 2026 年回忆涉及稳定匹配、复杂度记号、DFS 找环、贪心子序列匹配、分治求最大利润、最长公共子序列、Ford-Fulkerson 正确性证明和 NP 归约；不同年份可能变化。
- 推荐资源：OI Wiki、AcWing 算法课、洛谷题单、jyy 算法竞赛系列。
- 实验报告和代码只用于参考思路，不要直接提交。

## 待补充

- 补充课内 PPT 与教材章节的对应关系。
- 为实验报告目录补充实验题目说明，并清理可能包含的个人信息。

## 资料边界

本页只根据 README、目录和文件名整理导航，不抽取课件、答案或报告正文。回忆题和个人经验不代表未来考核，请以当年课程要求为准。
