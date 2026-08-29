# Transformer 架构详解

> 大模型时代的基石架构，所有主流 LLM 的核心。

---

## 一句话总结

**Transformer 是当今所有大模型（GPT、Claude、Gemini等）的核心架构，相当于大模型的"骨架"。**

---

## 历史背景

- **提出时间**: 2017 年
- **提出者**: Google（论文《Attention Is All You Need》）
- **解决问题**: RNN 处理序列数据的效率和长距离依赖问题

---

## 它解决了什么问题？

### RNN 的困境

```
RNN 的处理方式：
"我 → 今天 → 去 → 北京 → 吃 → 了 → 烤鸭"
  ↓      ↓      ↓     ↓     ↓     ↓     ↓
 一个一个处理，像排队过安检，又慢又容易"忘事"
```

**问题**：
1. 无法并行，训练慢
2. 长序列容易"遗忘"前面的内容
3. 梯度消失/爆炸问题

### Transformer 的解决方案

```
Transformer 的处理方式：
"我 今天 去 北京 吃 了 烤鸭"
  ↓↓↓↓↓↓↓ 同时处理 ↓↓↓↓↓↓↓
 所有词一起看，像开会讨论，又快又能看到全局
```

---

## 核心机制：自注意力（Self-Attention）

### 直观理解

**句子**："小明把苹果给了小红，因为**她**饿了"

问题：**"她"指的是谁？**

```
注意力机制的工作方式：

"她" 会去"询问"每个词：你和我有多相关？

  小明  →  相关度：0.1  （男的，不太可能）
  苹果  →  相关度：0.05 （物品，排除）
  小红  →  相关度：0.8  （女的，接收苹果的人，很可能！）
  饿了  →  相关度：0.3  （描述状态）

结论："她" = 小红 ✓
```

### 数学表示

```
注意力计算公式：

Attention(Q, K, V) = softmax(Q × K^T / √d_k) × V

其中：
- Q (Query): 查询向量，"我想找什么？"
- K (Key): 键向量，"我有什么特征？"
- V (Value): 值向量，"我的实际内容"
- √d_k: 缩放因子，防止点积过大
```

### 代码示例

```python
import torch
import torch.nn.functional as F

def self_attention(Q, K, V):
    """
    自注意力计算
    Q, K, V: shape = (batch_size, seq_len, d_model)
    """
    d_k = Q.size(-1)

    # 计算注意力分数
    scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(d_k))

    # softmax 归一化
    attention_weights = F.softmax(scores, dim=-1)

    # 加权求和
    output = torch.matmul(attention_weights, V)

    return output, attention_weights
```

---

## Transformer 的整体结构

```
输入: "今天天气真好"
        ↓
   ┌─────────────┐
   │  词嵌入层    │  把文字变成数字向量
   │  + 位置编码  │  加入位置信息
   └─────────────┘
        ↓
   ┌─────────────┐
   │  多头注意力   │  ← 核心！让词与词互相"交流"
   │  + 残差连接  │     多个角度同时分析
   │  + LayerNorm │
   └─────────────┘
        ↓
   ┌─────────────┐
   │  前馈神经网络 │  进一步加工信息
   │  + 残差连接  │
   │  + LayerNorm │
   └─────────────┘
        ↓
   （重复 N 层，大模型通常几十到上百层，GPT-4 的具体层数官方未公开）
        ↓
输出: 预测下一个词 / 理解语义
```

---

## 关键组件

### 1. 词嵌入（Word Embedding）
将离散的文字转换为连续的向量表示。

### 2. 位置编码（Positional Encoding）
因为 Transformer 并行处理，需要额外注入位置信息。

```python
# 正弦余弦位置编码
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

> 💡 现代大模型基本不再用上面的正弦余弦位置编码，主流方案是 **RoPE（旋转位置编码）**。
> RoPE 还可以通过 **YaRN** 等技术外推到比训练时更长的上下文（如 32K → 128K）。
> 详见 [Dense 与 MoE 架构对比 § YaRN](Dense与MoE架构对比.md#4-yarn把短上下文模型拉长的技术)。

### 3. 残差连接（Residual Connection）
```python
output = LayerNorm(x + Sublayer(x))
```
缓解深层网络的梯度问题。

### 4. 前馈网络（FFN）
```python
FFN(x) = ReLU(x × W1 + b1) × W2 + b2
```
两层全连接网络，中间维度通常是隐藏层的 4 倍。

> 💡 上面是 **2017 原版 Transformer** 的写法，现代大模型（LLaMA / Qwen / DeepSeek 等）已普遍换成三件套：
> - **Pre-LN** 取代 Post-LN：归一化挪到子层**之前**(`x + Sublayer(LN(x))`)，训练更稳、能堆得更深
> - **RMSNorm** 取代 LayerNorm：去掉均值中心化，只按均方根缩放，更快
> - **SwiGLU** 取代 ReLU FFN：门控激活，同等算力下效果更好(中间维度也常调成约 8/3 倍而非 4 倍)

---

## 大模型家族的分化

```
Transformer (2017)
     │
     ├── Encoder-only → BERT（理解型）
     │                   - 双向注意力
     │                   - 适合分类、问答、NER
     │
     ├── Decoder-only → GPT、Claude（生成型）
     │                   - 单向注意力（causal mask）
     │                   - 适合文本生成、对话
     │
     └── Encoder-Decoder → T5、BART
                          - 适合翻译、摘要
```

---

## 为什么 Transformer 如此成功？

| 特点 | 说明 |
|------|------|
| **并行计算** | 所有位置同时处理，GPU 利用率高 |
| **长距离依赖** | 任意两个位置可以直接交互 |
| **可扩展性** | 模型越大、数据越多，效果越好（Scaling Law） |
| **通用性** | 文本、图像、音频、视频都能用 |

---

## 类比总结

把大模型比作一个**超级学霸**：
- **Transformer** = 学霸的大脑结构
- **注意力机制** = 学霸的"抓重点"能力
- **参数量** = 脑容量大小
- **训练数据** = 读过的所有书

---

## 相关链接

- [注意力机制详解](注意力机制.md)
- [大模型如何"理解"文本](大模型如何理解文本.md) —— 本文讲底层结构，那篇从"任务能力"视角串起来回答"为什么 Transformer 能做主题分析、摘要"
- [DeepSeek 的创新](../01_模型架构/DeepSeek.md)

---

## 参考资料

- 原始论文: [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- Jay Alammar 的可视化讲解: The Illustrated Transformer

---

*创建时间: 2024-12-10*

---

## 来源与局限性

### 来源

正文中出现的出处标记：

- 原始论文：Attention Is All You Need https://arxiv.org/abs/1706.03762
- 参考资料：Jay Alammar 的可视化讲解: The Illustrated Transformer

- 正文引用的外部域名：`arxiv.org`

> 本节由脚本依据正文的出处标记自动归纳，**未经逐句人工复核**。下表只陈述可统计的客观事实，不代表对内容质量的判断；如与正文冲突，以正文为准。

### 局限性

| 维度 | 客观情况 |
|---|---|
| 时效性 | 含约 1 处具体版本号/型号表述；文件最后修改于 2026-06-03 |
| 覆盖范围 | 全文约 3k 字，覆盖范围以正文目录为准，未展开的边界情况请另行查证 |
| 实战验证 | 正文含约 0 处实测/复现/踩坑类表述（自动统计，仅供参考；具体哪些结论经过动手验证需读正文判断） |

---

*最后更新：2026-06-03（据 git 提交历史回填，非内容重新审校日期）*
