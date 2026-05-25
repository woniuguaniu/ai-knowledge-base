# NVIDIA 驱动 / CUDA / cuDNN / PyTorch:版本链条与踩坑手册

> **一句话**:你新买的 4090 装好了系统,准备 pip 装 PyTorch 跑 LLM——结果 `CUDA out of memory`、`undefined symbol`、`The NVIDIA driver on your system is too old`、`Could not load library libcudnn`……**这不是你的错,是 NVIDIA / 框架 / 驱动三方版本依赖链条非常复杂**。本文把这条链子从最底层(GPU 硬件)到最上层(PyTorch API)拆解,告诉你**哪个版本配哪个,撞了哪种错该怎么救**。
>
> ⚠️ **本篇为 Claude 原创补充笔记**,非 LINUX DO @flymyd 原稿(详见末尾「作者声明」)。

---

## 目录

- [0. 为什么这套链路这么折磨人](#0-为什么这套链路这么折磨人)
- [1. 整体架构与版本依赖链](#1-整体架构与版本依赖链)
- [2. NVIDIA Driver](#2-nvidia-driver)
- [3. CUDA Toolkit](#3-cuda-toolkit)
- [4. cuDNN](#4-cudnn)
- [5. PyTorch:版本对应表](#5-pytorch版本对应表)
- [6. Apple Silicon MPS 后端](#6-apple-silicon-mps-后端)
- [7. 常见报错与诊断](#7-常见报错与诊断)
- [8. 实战速查:从零到能跑](#8-实战速查从零到能跑)
- [9. 与本知识库其他章节的关联](#9-与本知识库其他章节的关联)
- [10. 术语速查](#10-术语速查)
- [11. 作者声明、来源与局限性](#11-作者声明来源与局限性)

---

## 0. 为什么这套链路这么折磨人

LLM / 深度学习的运行依赖一条"五层版本链",每层都有自己的版本号,且**层与层之间存在严格的兼容矩阵**:

```
┌─────────────────────────────────────────────────────┐
│ Layer 5: 应用框架 (PyTorch / TensorFlow / JAX)       │
├─────────────────────────────────────────────────────┤
│ Layer 4: 深度学习算子库 (cuDNN / cuBLAS / NCCL)       │
├─────────────────────────────────────────────────────┤
│ Layer 3: CUDA Toolkit (nvcc, runtime, libraries)     │
├─────────────────────────────────────────────────────┤
│ Layer 2: NVIDIA 驱动 (kernel driver + user space)     │
├─────────────────────────────────────────────────────┤
│ Layer 1: GPU 硬件 (Pascal / Volta / Ampere / ... )    │
└─────────────────────────────────────────────────────┘
```

**任何一层版本不匹配,整个栈就跑不起来**。最常见的报错形式:

| 报错关键词 | 通常根因 |
|---|---|
| `The NVIDIA driver on your system is too old` | 驱动版本太老,支持不了 PyTorch 编译时用的 CUDA |
| `CUDA error: no kernel image is available for execution on the device` | PyTorch 编译时没包含你这张卡的算力 |
| `Could not load library libcudnn` | cuDNN 没装或版本不对 |
| `undefined symbol: __cudaPopCallConfiguration` | CUDA runtime 版本和编译用的对不上 |
| `RuntimeError: CUDA out of memory` | 显存不够(不是版本问题,但容易被混淆) |

---

## 1. 整体架构与版本依赖链

### 1.1 关键概念辨析:Driver API vs Runtime API

CUDA 提供 **两套 API**,初学者最容易混淆:

| 项目 | Driver API | Runtime API |
|---|---|---|
| 谁提供 | **NVIDIA 驱动**(`libnvidia.so`) | **CUDA Toolkit**(`libcudart.so`) |
| 哪个层级 | 底层 | 上层(封装了 Driver API) |
| 谁直接用 | 大多数框架不直接用 | PyTorch / TensorFlow 这一层 |
| 版本来源 | `nvidia-smi` 显示的 "CUDA Version" | `nvcc --version` 显示的版本 |
| **是否一致** | **❌ 不必一致**——这是最大的坑 | — |

#### `nvidia-smi` 显示的 CUDA Version 是什么意思?

```bash
$ nvidia-smi
+---------------------------------------------------------+
| NVIDIA-SMI 535.104.05  Driver Version: 535.104.05  CUDA Version: 12.2 |
+---------------------------------------------------------+
```

**关键**:这里的 `CUDA Version: 12.2` 是"**该驱动最高支持的 CUDA Runtime 版本**",**不是**"系统装了 CUDA 12.2"。

实际上系统里可以同时装 CUDA 11.8、12.1、12.4,只要不超过这个上限就都能跑。**驱动是向下兼容的**——新驱动能跑老 CUDA,反之不行。

### 1.2 兼容矩阵速查表

| NVIDIA Driver | 最高支持 CUDA | 典型场景 |
|---|---|---|
| 470.x | CUDA 11.4 | 老服务器,LTS 长支持 |
| 510.x | CUDA 11.6 | — |
| 520.x | CUDA 11.8 | **PyTorch 2.0 起的最低门槛之一** |
| 530.x | CUDA 12.1 | — |
| 535.x | CUDA 12.2 | **当前 LTS,推荐** |
| 545.x | CUDA 12.3 | — |
| 550.x | CUDA 12.4 | — |
| 555.x | CUDA 12.5 | — |
| 560.x | CUDA 12.6 | 较新 |
| 570.x | CUDA 12.7 | 较新 |
| 575.x | CUDA 12.8 | 较新 |

> 📌 **实战经验**:**装驱动时优先选 LTS(长期支持)版本**,比如 535,而不是追最新。LTS 驱动更稳,bug 已修。

---

## 2. NVIDIA Driver

### 2.1 是什么

NVIDIA Driver 包含两层:

1. **Kernel Driver(内核模块)**:`nvidia.ko`,运行在 Linux 内核空间,直接和硬件通信
2. **User-space Driver(用户态库)**:`libnvidia-ml.so` 等,被 `nvidia-smi`、CUDA、应用调用

**没有驱动,GPU 在系统里就是一块铁**。

### 2.2 Linux 安装(Ubuntu 为例)

#### 方式 A:官方 .run 安装包(灵活但麻烦)

```bash
# 1. 禁用 nouveau(Linux 自带的开源 NVIDIA 驱动,会冲突)
sudo bash -c "echo blacklist nouveau > /etc/modprobe.d/blacklist-nouveau.conf"
sudo update-initramfs -u
sudo reboot

# 2. 关图形界面(Ubuntu Desktop)
sudo systemctl stop gdm   # 或 lightdm

# 3. 安装
sudo sh NVIDIA-Linux-x86_64-535.104.05.run

# 4. 验证
nvidia-smi
```

#### 方式 B:Ubuntu 仓库(推荐新手)

```bash
# 1. 添加仓库
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update

# 2. 查可用驱动
ubuntu-drivers devices

# 3. 自动装推荐版
sudo ubuntu-drivers autoinstall

# 或装指定版本
sudo apt install nvidia-driver-535

# 4. 重启
sudo reboot
nvidia-smi
```

### 2.3 Windows / WSL2 安装

- **Windows 原生**:NVIDIA 官网下载 Game Ready / Studio Driver,exe 一键装
- **WSL2**(Windows 上跑 Linux GPU 工作流):
  - **不要在 WSL2 里装 Linux 驱动**
  - 只在 **Windows 主机** 装最新 NVIDIA 驱动
  - WSL2 通过 `/dev/dxg` 共享主机 GPU
  - WSL2 内部装 CUDA Toolkit 时**选 WSL-Ubuntu 版本**,不是普通 Linux 版本

### 2.4 常见诊断命令

```bash
# 看驱动版本 + GPU 状态 + 进程
nvidia-smi

# 看驱动详细信息
cat /proc/driver/nvidia/version

# 看是否成功加载内核模块
lsmod | grep nvidia

# 看 GPU 详细规格
nvidia-smi -q -i 0
```

---

## 3. CUDA Toolkit

### 3.1 是什么

CUDA Toolkit 包含:

- **nvcc**:CUDA 编译器,编译 `.cu` 文件
- **CUDA Runtime**(`libcudart.so`):上层 API,大多数应用走这个
- **CUDA Libraries**:cuBLAS(线性代数)、cuRAND、cuFFT、cuSolver 等
- **开发头文件**、**示例代码**、**Profiler 工具**(nsight)

### 3.2 几种安装方式对比

| 方式 | 适合 | 命令/动作 |
|---|---|---|
| **conda 安装**(推荐) | 大多数 Python 用户 | `conda install -c nvidia cuda-toolkit=12.1` |
| **pip 安装** | 只用 PyTorch / TF | **不需要单独装** — PyTorch wheel 自带 CUDA 运行时库 |
| **官方 .deb / .rpm** | 系统级安装 | NVIDIA 官网下载,`sudo apt install cuda` |
| **官方 .run** | 灵活 | `sudo sh cuda_12.1.0_530.30.02_linux.run` |

> ⚠️ **常见误区 #1**:很多人在 conda 环境里又额外用 apt 装了 CUDA,结果系统 PATH 里有 2 个 nvcc,出现版本混乱。**只在一个地方装一次**。

> ⚠️ **常见误区 #2**:**只跑推理不需要 nvcc**——PyTorch 的预编译 wheel 已经带了 CUDA Runtime,只有写自定义算子(像 vLLM 的 Flash Attention)才需要 nvcc。

### 3.3 多版本 CUDA 共存

如果项目 A 要 CUDA 11.8、项目 B 要 CUDA 12.1,系统能不能同时装?

**能,但只能通过 conda 环境隔离**。系统 CUDA 装一个就够,框架用哪个版本由 conda env 里的 PyTorch wheel 决定。

```bash
# 项目 A:CUDA 11.8
conda create -n proj_a python=3.10
conda activate proj_a
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cu118

# 项目 B:CUDA 12.1
conda create -n proj_b python=3.10
conda activate proj_b
pip install torch==2.4.0 --index-url https://download.pytorch.org/whl/cu121
```

**两个环境共用同一个 NVIDIA 驱动**(因为驱动向下兼容)。

### 3.4 验证安装

```bash
# nvcc 版本(系统级 CUDA Toolkit 装的)
nvcc --version

# Python 里看 PyTorch 用的 CUDA(框架级)
python -c "import torch; print(torch.version.cuda)"
```

**这两个值经常不同**,这是正常的(详见 § 1.1)。

---

## 4. cuDNN

### 4.1 是什么

cuDNN(CUDA Deep Neural Network Library):**NVIDIA 为深度学习专门优化的算子库**。

- 提供卷积、池化、归一化、激活函数等的高性能 GPU 实现
- PyTorch / TensorFlow 在底层会调用 cuDNN
- **不装 cuDNN,框架也能跑**,但速度会慢很多;**部分模型(如某些 Transformer 实现)甚至会直接报错**

### 4.2 安装

#### 方式 A:PyTorch wheel 自带(最简单)

`pip install torch` 时,wheel 已经包含了 cuDNN 的副本,**大多数用户不需要单独装**。

#### 方式 B:系统级安装(开发自定义算子时需要)

1. 去 [NVIDIA cuDNN 下载页](https://developer.nvidia.com/cudnn)(**需要登录开发者账号**)
2. 选与 CUDA 版本对应的 cuDNN
3. 解压 .tar.gz,把 lib 文件和头文件分别拷到 CUDA 安装目录

```bash
tar -xvf cudnn-linux-x86_64-9.x.x.x_cuda12-archive.tar.xz
sudo cp -P include/cudnn*.h /usr/local/cuda/include/
sudo cp -P lib/libcudnn* /usr/local/cuda/lib64/
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

#### 方式 C:conda 安装

```bash
conda install -c conda-forge cudnn=8.9
```

### 4.3 cuDNN 与 CUDA 的版本对应

| cuDNN 主版本 | 支持的 CUDA |
|---|---|
| cuDNN 8.x | CUDA 11.x / 12.x |
| cuDNN 9.x | CUDA 12.x |

> 💡 **快速判断**:cuDNN **大版本号** 通常跟随 PyTorch 大版本走;升级 PyTorch 时让它自带的 cuDNN 跟着升,**不要手动拼装**。

### 4.4 验证

```python
import torch
print(torch.backends.cudnn.version())   # cuDNN 版本号
print(torch.backends.cudnn.enabled)     # 是否启用
print(torch.backends.cudnn.is_available())
```

---

## 5. PyTorch:版本对应表

### 5.1 PyTorch 与 CUDA 的对应矩阵

| PyTorch | 支持 CUDA 版本 | Python | 备注 |
|---|---|---|---|
| 2.0 | 11.7 / 11.8 | 3.8-3.11 | 2023 年 3 月 |
| 2.1 | 11.8 / 12.1 | 3.8-3.11 | 2023 年 10 月 |
| 2.2 | 11.8 / 12.1 | 3.8-3.11 | 2024 年 1 月 |
| 2.3 | 11.8 / 12.1 | 3.8-3.11 | 2024 年 4 月 |
| 2.4 | 11.8 / 12.1 / 12.4 | 3.8-3.12 | 2024 年 7 月 |
| 2.5 | 11.8 / 12.1 / 12.4 | 3.9-3.12 | 2024 年 10 月 |
| 2.6 | 11.8 / 12.4 / 12.6 | 3.9-3.13 | 2025 年 1 月 |
| 2.7+ | 12.6 / 12.8 起 | 3.10-3.13 | 较新 |

> 📌 **当前主流推荐组合**(截至 2026 年):
> - **驱动 535+** + **CUDA 12.1 或 12.4** + **PyTorch 2.4/2.5** + **Python 3.10/3.11**

### 5.2 安装命令

PyTorch 官方提供了**指定 CUDA 版本的预编译 wheel**:

```bash
# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CUDA 11.8(老硬件)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CPU 版本(没 GPU 时)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Nightly(最新功能,不稳)
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
```

**选 URL 的关键**:`/whl/cu121` 表示这个 wheel **内嵌了 CUDA 12.1 的运行时库**——它不需要你系统有 CUDA Toolkit。

### 5.3 验证 PyTorch 真的能用 GPU

```python
import torch

# 1. CUDA 可用?
print(torch.cuda.is_available())            # True / False

# 2. 几张卡?
print(torch.cuda.device_count())

# 3. 卡的名字?
print(torch.cuda.get_device_name(0))

# 4. 当前用的 CUDA 版本(框架级)?
print(torch.version.cuda)

# 5. cuDNN 版本?
print(torch.backends.cudnn.version())

# 6. 实测一下能不能算
x = torch.randn(1000, 1000, device='cuda')
y = x @ x.T
print(y.shape, y.device)
```

如果第 1 步就 `False`,**99% 是驱动 / CUDA / PyTorch 版本不匹配**。

---

## 6. Apple Silicon MPS 后端

如果你用 M1/M2/M3/M4 系列 MacBook,没有 NVIDIA GPU。但 Apple 提供了 **MPS(Metal Performance Shaders)** 作为 GPU 后端,PyTorch 自 1.12 起原生支持。

### 6.1 安装

```bash
# Apple Silicon Mac
pip install torch torchvision torchaudio
```

**不需要装 CUDA 任何东西**——pip 会自动给你装 MPS 后端版本。

### 6.2 验证与使用

```python
import torch

# 1. MPS 可用?
print(torch.backends.mps.is_available())     # True

# 2. 用 MPS
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
x = torch.randn(1000, 1000, device=device)
```

### 6.3 MPS 的现实

| 维度 | MPS 现状 |
|---|---|
| 训练 | 可以但慢,且部分算子缺失 / fallback to CPU |
| 推理 | 7B 量化模型可以,30B+ 需 64GB+ 统一内存 |
| 生态 | 主流框架(PyTorch / Transformers / llama.cpp / MLX)都支持,但**功能完整度不如 CUDA** |
| 配套 | 推荐 [MLX](https://github.com/ml-explore/mlx)(Apple 自研深度学习框架)— 针对统一内存深度优化 |

> 💡 **MacBook 跑大模型的更优选**:`llama.cpp` 或 `MLX` + GGUF 量化,见 [本地部署模型量化选型.md](../03_应用实践/本地部署模型量化选型.md)。

---

## 7. 常见报错与诊断

### 7.1 报错速查表

| 错误信息 | 根因 | 修复 |
|---|---|---|
| `The NVIDIA driver on your system is too old (found version 11xxx). Please update your driver to a newer version.` | 驱动太老 | 升级驱动到能支持当前 PyTorch CUDA 版本的级别 |
| `CUDA error: no kernel image is available for execution on the device` | PyTorch wheel 没编译你这张卡的算力(如 5090 sm_120) | 装 PyTorch nightly,或编译 from source |
| `CUDA error: device-side assert triggered` | 模型逻辑里有 index 越界 / NaN | 加 `CUDA_LAUNCH_BLOCKING=1` 重跑找根因 |
| `Could not load library libcudnn_ops_infer.so.8` | cuDNN 缺失或路径不对 | `find / -name "libcudnn*"`,加到 `LD_LIBRARY_PATH` |
| `undefined symbol: __cudaPopCallConfiguration` | 系统 CUDA Runtime 和编译时不一致 | 用 conda env 隔离,别混装 |
| `RuntimeError: CUDA out of memory. Tried to allocate ...` | 显存真的不够 | 减 batch size / 用量化 / 用 gradient checkpointing |
| `torch.cuda.is_available()` 返回 `False`(但 `nvidia-smi` 正常) | PyTorch wheel 是 CPU 版本 / 或装错了 CUDA 版本 | `pip show torch` 看版本,重装带 `cu121` 的 wheel |

### 7.2 诊断脚本(一键自检)

把下面这段保存为 `check_gpu.py`,跑一遍可快速定位问题:

```python
import sys
import platform
import subprocess

print("=" * 60)
print(f"Python:        {sys.version.split()[0]}")
print(f"Platform:      {platform.platform()}")

try:
    out = subprocess.check_output(["nvidia-smi"], text=True)
    driver_line = [l for l in out.split("\n") if "Driver Version" in l][0]
    print(f"NVIDIA driver: {driver_line.strip()}")
except FileNotFoundError:
    print("nvidia-smi: NOT FOUND (no driver?)")
except subprocess.CalledProcessError as e:
    print(f"nvidia-smi: FAILED ({e})")

try:
    out = subprocess.check_output(["nvcc", "--version"], text=True)
    print(f"nvcc:          {out.strip().split('release')[-1].split(',')[0].strip()}")
except FileNotFoundError:
    print("nvcc:          NOT FOUND (CUDA Toolkit not in PATH)")

try:
    import torch
    print(f"PyTorch:       {torch.__version__}")
    print(f"PyTorch CUDA:  {torch.version.cuda}")
    print(f"cuDNN:         {torch.backends.cudnn.version()}")
    print(f"CUDA available:{torch.cuda.is_available()}")
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            print(f"  GPU {i}:      {torch.cuda.get_device_name(i)}")
            print(f"    显存:       {torch.cuda.get_device_properties(i).total_memory / 1e9:.1f} GB")
            print(f"    算力:       sm_{torch.cuda.get_device_properties(i).major}{torch.cuda.get_device_properties(i).minor}")
except ImportError:
    print("PyTorch:       NOT INSTALLED")
print("=" * 60)
```

---

## 8. 实战速查:从零到能跑

### 8.1 Linux + NVIDIA GPU(Ubuntu 22.04)

```bash
# Step 1:装驱动
sudo apt update
sudo ubuntu-drivers autoinstall
sudo reboot

# Step 2:验证
nvidia-smi
# 应该能看到 GPU 信息和 "CUDA Version: 12.x"

# Step 3:装 Miniconda(管理 Python 环境)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Step 4:建环境 + 装 PyTorch
conda create -n llm python=3.10
conda activate llm
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Step 5:验证
python -c "import torch; print(torch.cuda.is_available())"
# 应该输出 True
```

### 8.2 WSL2(Windows 上跑 Linux)

```powershell
# Windows 主机
# 1. 装最新 NVIDIA 驱动(普通 Windows 驱动即可)

# 2. 装 WSL2 + Ubuntu
wsl --install -d Ubuntu-22.04

# 进入 WSL2 后,按 § 8.1 的 Step 3-5 走
# 但 Step 1 跳过,不要在 WSL 里装 Linux 驱动
```

### 8.3 macOS + Apple Silicon

```bash
# 1. 装 Miniconda
brew install miniconda

# 2. 建环境
conda create -n llm python=3.10
conda activate llm

# 3. 装 PyTorch(自动选 MPS 版本)
pip install torch torchvision torchaudio

# 4. 验证
python -c "import torch; print(torch.backends.mps.is_available())"
# 应该输出 True
```

---

## 9. 与本知识库其他章节的关联

- **硬件基础**:[NVIDIA 显卡架构与 AI 算力](NVIDIA显卡架构与AI算力.md)——架构演进 / Tensor Core / 显存原理 / NVLink,**理解为什么有版本依赖**
- **模型部署**:[本地部署模型量化选型](../03_应用实践/本地部署模型量化选型.md)——选好精度和量化方案后,用本文环境跑起来
- **推理引擎**:[LLM 推理引擎选型](../03_应用实践/LLM推理引擎选型.md)——环境配好后选 vLLM / SGLang / Ollama 等具体引擎
- **CV 框架基础**:[计算机视觉与深度学习框架](../00_核心概念/计算机视觉与深度学习框架.md)——PyTorch vs TensorFlow 的对比,以及 OpenCV / MTCNN 等

---

## 10. 术语速查

| 术语 | 全称 | 含义 |
|---|---|---|
| **Driver** | NVIDIA Driver | 让操作系统能识别 GPU 并通信的底层软件 |
| **CUDA** | Compute Unified Device Architecture | NVIDIA 的 GPU 并行计算平台 |
| **nvcc** | NVIDIA CUDA Compiler | 编译 `.cu` 源代码的编译器 |
| **CUDA Toolkit** | — | nvcc + Runtime + Libraries 的合集 |
| **Driver API** | — | 底层 CUDA API,直接和驱动对话 |
| **Runtime API** | — | 上层 CUDA API,大多数应用走这个 |
| **cuDNN** | CUDA Deep Neural Network library | NVIDIA 为深度学习优化的算子库 |
| **cuBLAS** | CUDA BLAS | 线性代数算子库 |
| **NCCL** | NVIDIA Collective Communications Library | 多 GPU / 多机集体通信库 |
| **TensorRT** | — | NVIDIA 的推理优化 / 部署框架 |
| **算力(Compute Capability)** | sm_xx | GPU 架构的版本号,如 sm_80 = A100,sm_89 = 4090,sm_90 = H100,sm_120 = 5090 |
| **PTX** | Parallel Thread Execution | CUDA 的中间表示,可被 JIT 编译为不同算力的机器码 |
| **MPS(NVIDIA)** | Multi-Process Service | 多进程共享 GPU 的机制,**注意别和 Apple 的 MPS 混淆** |
| **MPS(Apple)** | Metal Performance Shaders | Apple Silicon 的 GPU 计算后端 |
| **MLX** | — | Apple 自研的深度学习框架,针对统一内存优化 |
| **WSL2** | Windows Subsystem for Linux 2 | Windows 上的 Linux 虚拟化,**GPU 透传由主机 Windows 驱动负责** |
| **Conda** | — | Python 环境管理工具,LLM 圈事实标准 |
| **wheel** | `.whl` | Python 预编译包格式,PyTorch GPU 版本是带 CUDA Runtime 的 wheel |

---

## 11. 作者声明、来源与局限性

### 11.1 作者声明

> ⚠️ **本篇是 Claude 基于公开技术资料整理的科普综述,不是 LINUX DO @flymyd 的实战经验帖**。
>
> 原作者在「简单易懂的 LLM 相关知识梳理」目录中标记 ep.3-3 已发布,但本笔记整理者没有拿到原文 PDF,因此**无法整理作者的实战经验内容**。本笔记仅作为"作者填坑前的占位",建议有机会读到 @flymyd 的 ep.3-3 原文时**优先参考作者原文**,本笔记作为补充对照。

### 11.2 主要来源

- [NVIDIA 官方驱动下载页](https://www.nvidia.com/Download/index.aspx)
- [CUDA Toolkit 官方文档](https://docs.nvidia.com/cuda/)
- [cuDNN 官方文档](https://docs.nvidia.com/deeplearning/cudnn/)
- [PyTorch 官方 Get Started](https://pytorch.org/get-started/locally/)
- [PyTorch CUDA 兼容性矩阵](https://pytorch.org/get-started/previous-versions/)
- [Microsoft WSL2 + GPU 文档](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute)

### 11.3 本笔记的局限性

| 维度 | 局限性 |
|---|---|
| **个人体感** | 笔者没有亲历"装驱动失败 → 折腾 3 天"的实战体验,**生活化的踩坑细节缺失**(@flymyd 原文如果有,会比本文生动) |
| **企业级配置** | 本文聚焦个人 / 小团队场景,**多机训练 / Kubernetes GPU 调度 / 多卡 P2P 通信问题**未深入 |
| **故障案例库** | 报错速查表覆盖了高频问题,但具体到"某厂某型号 + 某驱动 + 某 CUDA 的奇葩 bug"无法穷举 |
| **时效性** | PyTorch / CUDA 版本对应表截至 2026 年初,**新版发布请以官网为准** |
| **国产 GPU** | 昇腾 / 寒武纪 / 海光 等的"驱动 / 算子库 / 框架"链条未覆盖(它们各有独立生态,详见相应官方文档) |

### 11.4 这篇笔记没回答的、但用户可能会问的问题

- **怎么搭建多机分布式训练环境(NCCL / Slurm)** → 超本文范围,推荐 PyTorch DDP 官方教程
- **怎么用 Docker 跑 GPU 工作流** → 推荐 NVIDIA Container Toolkit 官方文档
- **CUDA 编程入门** → 推荐《CUDA C 编程权威指南》或 NVIDIA 官方 CUDA Samples
- **GPU profiling 与性能优化** → 推荐 Nsight Systems / Nsight Compute 官方文档
