---
title: "JEPA：一种面向世界模型的自监督学习思路"
description: "JEPA 不追求像素级重建，而是在表示空间中预测被遮挡区域，为理解世界模型、自监督表征学习和具身智能提供了一个简洁视角。"
date: "2026-04-25"
tags: ["JEPA", "self-supervised learning", "world model", "representation learning"]
category: "Research"
cover: "images/blog/jepa-cover.svg"
draft: false
---

## 为什么关注 JEPA

JEPA，全称 Joint Embedding Predictive Architecture，是 Yann LeCun 等人提出的一类自监督学习框架。它的核心问题很直接：模型能不能不依赖人工标注，通过观察世界本身，学到对未来、结构和语义有用的表示？

这件事和 world model 很接近。一个有用的世界模型不一定要复原每一个像素，而是应该知道哪些因素重要、哪些变化可预测、哪些信息和决策相关。JEPA 的价值就在这里：它把学习目标从“重建原始输入”转向“预测抽象表示”。

## 从重建像素到预测表示

很多自监督方法会使用遮挡重建。例如给模型一张被遮住的图片，让它补回缺失区域。这类方法很自然，但也有一个问题：像素细节太多，其中有很多并不重要。

比如一辆车的表面纹理、树叶的细节、道路上微小的噪声，都可能占据大量像素误差，但它们并不一定影响智能体对场景的理解。

JEPA 的思路是：

> 不预测原始像素，而预测目标区域在表示空间中的 embedding。

也就是说，模型看到一部分上下文后，不需要画出被遮住的部分，只需要预测那部分“语义表示”应该是什么。

## JEPA 的基本结构

一个简化的 JEPA 可以分成三部分：

1. Context encoder  
   编码可见区域，得到上下文表示。

2. Target encoder  
   编码目标区域，得到目标表示。训练时可见，推理时不需要。

3. Predictor  
   根据上下文表示预测目标表示。

训练目标不是像素级误差，而是让 predictor 的输出接近 target encoder 给出的表示。

用很粗略的形式写，就是：

```text
context → context encoder → predictor → predicted target embedding

target  → target encoder  → true target embedding

loss = distance(predicted target embedding, true target embedding)
```

这里的关键是：target embedding 本身是抽象的，它不要求模型保留所有低层细节。

## 为什么这可能适合世界模型

世界模型的目标不是“拍脑袋生成一张看起来真实的图”，而是为智能体提供可以用于推理和行动的内部状态。

如果模型只学习像素，它可能会把能力浪费在纹理、光照、噪声上。对自动驾驶或具身智能来说，更重要的是：

- 哪些物体存在；
- 它们之间有什么空间关系；
- 哪些区域可能发生运动；
- 当前状态对未来有什么约束；
- 哪些变化和行动有关。

JEPA 通过表示空间预测，天然鼓励模型学习更抽象、更稳定的结构。这一点和 object-centric reasoning、scene graph、physical reasoning 等方向是相通的。

## 和生成式模型的区别

生成式模型通常要回答：“缺失部分长什么样？”

JEPA 更像是在回答：“缺失部分在语义上应该是什么？”

这两个问题不一样。前者可能要求大量细节；后者更关注结构和语义。

对于智能体来说，后一个问题往往更重要。因为行动决策通常不需要知道每一片树叶怎么长，而需要知道前方有没有行人、车辆是否会切入、物体之间是否可能碰撞。

## 对自动驾驶的启发

在自动驾驶场景中，JEPA 式学习可以给出几个启发：

1. 表示比像素更重要  
   车辆不需要完整复原摄像头图像，而需要理解可行动的场景状态。

2. 预测应该发生在抽象状态上  
   比起预测未来视频帧，预测未来 object state、risk state 或 scene representation 可能更直接。

3. 遮挡和不确定性是核心问题  
   道路场景中经常有遮挡。JEPA 的“从上下文预测缺失表示”与遮挡理解天然相关。

4. 可以连接 closed-loop decision making  
   如果表示空间和行动后果有关，它就能成为 planning 或 RL 的状态基础。

## 一个值得继续追的问题

JEPA 的关键挑战在于：表示空间到底应该学成什么样？

如果 target encoder 学到的表示本身不包含物体、关系、动力学或风险信息，那么 predictor 学得再好，也未必有助于智能体决策。

所以，面向自动驾驶和 embodied intelligence 的 JEPA 可能需要进一步引入：

- object-centric 表示；
- 时序预测；
- 物理约束；
- 多模态语言监督；
- 和 action / planning 相关的目标。

## 小结

JEPA 的核心价值不是一个具体模型结构，而是一种学习观念：

> 智能体不必重建世界的全部细节，但需要预测世界中对理解和行动有用的抽象状态。

这个思想很适合连接 self-supervised learning、world models、自动驾驶、VLM video reasoning 和 embodied intelligence。后续如果要构建面向闭环决策的世界模型，JEPA 是一个值得持续关注的基础方向。
