# 机器视觉技术

## 课程速览

| 项目 | 信息 |
| --- | --- |
| 所属方向 | 人工智能 / 计算机视觉 |
| 主要内容 | 传统图像处理、特征检测、二值图像、CNN、图像分类、目标检测、图像分割 |
| 常用工具 | MATLAB、C++ / OpenCV、Python / PyTorch |
| 资料完整度 | 较完整，包含课件、往年题、考试回忆、实验报告、课程设计资料和外部代码仓库 |
| 资料边界 | 考试回忆不是标准答案，实验报告和代码只适合作为学习参考 |

## 课程介绍

机器视觉技术主要覆盖传统图像处理、特征检测、二值图像分析、卷积神经网络、图像分类、目标检测与图像分割。课程资料已经比较完整，适合作为本 Wiki 首批整理的课程页。

## 仓库资料与链接

完整实验代码仓库：[summerwind0131/nku_machine_vision](https://github.com/summerwind0131/nku_machine_vision)

| 类型 | 位置 | 说明 |
| --- | --- | --- |
| 课件 | [机器视觉技术/课件/](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E6%9C%BA%E5%99%A8%E8%A7%86%E8%A7%89%E6%8A%80%E6%9C%AF/%E8%AF%BE%E4%BB%B6) | 包含绪论、图像基础、二值图像、特征检测、CNN、图像分类、目标检测与图像分割，以及 `复习2026.pdf` |
| 往年题 | [机器视觉技术/往年真题及练习题/](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E6%9C%BA%E5%99%A8%E8%A7%86%E8%A7%89%E6%8A%80%E6%9C%AF/%E5%BE%80%E5%B9%B4%E7%9C%9F%E9%A2%98%E5%8F%8A%E7%BB%83%E4%B9%A0%E9%A2%98) | 当前收录两份机器视觉卷子，适合熟悉题型 |
| 考试回忆 | [机器视觉技术/2026 机器视觉回忆.md](https://github.com/summerwind0131/NKU-AI-Study/blob/main/%E6%9C%BA%E5%99%A8%E8%A7%86%E8%A7%89%E6%8A%80%E6%9C%AF/2026%20%E6%9C%BA%E5%99%A8%E8%A7%86%E8%A7%89%E5%9B%9E%E5%BF%86.md) | 按选择、判断、简答、解答、编程题整理的回忆版考点 |
| 实验资料 | [机器视觉技术/机器视觉实验 sfy/](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E6%9C%BA%E5%99%A8%E8%A7%86%E8%A7%89%E6%8A%80%E6%9C%AF/%E6%9C%BA%E5%99%A8%E8%A7%86%E8%A7%89%E5%AE%9E%E9%AA%8C%20sfy) | 实验二、三、四的报告、图片和 C++ 实现 |
| 实验与课程设计 | [机器视觉技术/机器视觉实验by fyr/](https://github.com/summerwind0131/NKU-AI-Study/tree/main/%E6%9C%BA%E5%99%A8%E8%A7%86%E8%A7%89%E6%8A%80%E6%9C%AF/%E6%9C%BA%E5%99%A8%E8%A7%86%E8%A7%89%E5%AE%9E%E9%AA%8Cby%20fyr) | 实验二、三、四的 MATLAB / C++ 实现，以及课程设计 Part1 / Part2 |
| 代码仓库 | [summerwind0131/nku_machine_vision](https://github.com/summerwind0131/nku_machine_vision) | 包含 OpenCV 作业、练习代码、传统视觉手势识别和深度学习手势识别项目 |

## 推荐学习路线

1. 先读课件，把二值图像、特征检测、CNN、分类与检测这些主线概念串起来。
2. 做实验时优先理解每个算法要解决什么问题，再看代码实现细节。
3. 课程设计先确定任务形式：传统视觉更看重分割和特征，深度学习更看重数据划分、模型保存和测试脚本。
4. 期末前用往年题和 `2026 机器视觉回忆.md` 熟悉题型，再回到 PPT 查漏补缺。

## 实验与课程设计

实验二主要是距离检测与积分图像，实验三主要是直方图均衡化、中值滤波等图像增强，实验四主要是迭代最优阈值、OTSU 阈值检测等二值图像处理。普通实验整体不算难，主要注意路径、输入输出格式和报告截图。

课程设计更建议参考代码仓库中的 `final_projects/`：

- `final_projects/project1_traditional_gesture/`：传统视觉四分类手势识别，类别为 `A`、`C`、`Five`、`V`，包含单独测试代码、训练好的 `gesture_knn.yml` 和报告。
- `final_projects/project2_deep_gesture/`：ResNet18 六分类手势识别，类别为 `A`、`B`、`C`、`Five`、`Point`、`V`，包含 `test.py`、`checkpoints/best_model.pth` 和报告。
- `practice/`：课程练习代码，包括 LeNet、AlexNet、ResNet、R-CNN、U-Net 等。
- `src/`：C++ / OpenCV 小作业代码，根目录 `CMakeLists.txt` 会为 `src` 下每个 `.cpp` 生成一个可执行程序。

深度学习课程设计最好使用 GPU。CPU 可以跑，但训练和调参会明显拖慢进度。

## 备考建议

期末题型可能包含选择、判断、简答、计算 / 解答和编程题。2026 年回忆中出现过的内容包括：

- 滤波与噪声、灰度级范围、距离度量、HOG、OTSU、采样
- 卷积层输出尺寸与参数量、CNN 各层作用、ResNet 基本块
- Canny 与 Sobel、SIFT 特征匹配、形态学开闭运算
- `epoch`、`batch size`、`iteration` 的含义和换算

复习时建议重点练：

1. 常见算法的目标、流程和适用场景，例如 OTSU、Hough、Canny、SIFT、ROI Pooling。
2. 卷积输出尺寸、参数量、训练轮次相关计算。
3. 基础图像处理编程题，例如滤波、Sobel 边缘检测、简单 CNN / ResNet 模块。

往年题和回忆题更适合抓题型，不要把它们当作唯一复习范围。

## 课程建议

- 深度学习大作业要根据数据集规模选择方法，迁移学习通常更稳，也可以探索小样本学习或元学习。
- 深度学习作业一定要认真划分训练集、验证集和测试集，避免把验证结果和真正测试泛化混在一起。
- 传统视觉部分建议重点掌握概念、处理流程和调参思路，尤其是分割、特征和后处理。
- 深度学习部分如果想继续学，推荐补 CS231n lecture notes 和 assignments；中文资源可以参考李沐《动手学深度学习》、PyTorch 入门教程和计算机视觉相关课程。

## 资料边界

本页只做课程资料导航和个人经验整理。实验报告、课程设计代码可以借鉴思路，但不要直接照抄或提交他人材料。不同年份老师要求、数据集和评分方式都可能变化，请以当年课程要求为准。
