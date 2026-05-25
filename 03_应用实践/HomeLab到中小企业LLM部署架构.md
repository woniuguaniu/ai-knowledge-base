# HomeLab 到中小企业:开源 LLM 部署架构

> **一句话**:模型选好了(✅)、量化算清了(✅)、显卡架构理顺了(✅)、推理引擎选完了(✅)、驱动 / CUDA / PyTorch 跑通了(✅)——现在你面对一个新问题:**怎么把"能跑"变成"能用 / 能稳 / 能给团队用 / 能挡住误用"?** 本文是从家庭单显卡到中小企业 8 卡集群的部署架构指南。
>
> ⚠️ **本篇为 Claude 原创补充笔记**,非 LINUX DO @flymyd 原稿(详见末尾「作者声明」)。

---

## 目录

- [0. 为什么"能跑"还不够](#0-为什么能跑还不够)
- [1. 部署架构分层模型](#1-部署架构分层模型)
- [2. 场景 A:个人 HomeLab(单 GPU,1-3 用户)](#2-场景-a个人-homelab单-gpu1-3-用户)
- [3. 场景 B:工作室 / 小团队(2-4 卡,10-50 用户)](#3-场景-b工作室--小团队2-4-卡10-50-用户)
- [4. 场景 C:中小企业(4-8 卡,50-500 用户)](#4-场景-c中小企业4-8-卡50-500-用户)
- [5. 反向代理与统一网关](#5-反向代理与统一网关)
- [6. API Key 管理与限流](#6-api-key-管理与限流)
- [7. 监控与日志](#7-监控与日志)
- [8. 容灾与高可用](#8-容灾与高可用)
- [9. 成本预算速查](#9-成本预算速查)
- [10. 与本知识库其他章节的关联](#10-与本知识库其他章节的关联)
- [11. 术语速查](#11-术语速查)
- [12. 作者声明、来源与局限性](#12-作者声明来源与局限性)

---

## 0. 为什么"能跑"还不够

```
单跑命令 vs 真实生产环境
─────────────────────────────────────────────────────

python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-7B --port 8000
            ↑
       这只能让一个开发者自己用

真实生产环境:
  ✓ 多用户 → 谁能用?用多少?
  ✓ 鉴权    → 怎么发 API key?
  ✓ 限流    → 防止单用户打爆
  ✓ 监控    → 是不是健康?延迟多少?谁在用?
  ✓ 容灾    → GPU 崩了怎么办?
  ✓ 模型管理 → 同时跑几个模型怎么调度?
  ✓ 版本管理 → 模型升级怎么平滑切换?
  ✓ 域名 + HTTPS → 不能让明文 token 在网上裸奔
```

**部署架构的本质:在"推理引擎 / 模型"之上加一层"控制平面"**。

---

## 1. 部署架构分层模型

无论规模大小,部署架构都可以拆成 4 层:

```
┌─────────────────────────────────────────────────────┐
│ Layer 4: 接入层(用户 / 应用)                       │
│         ChatBox / Web UI / 自研应用 / Claude Code    │
└─────────────────────────────────────────────────────┘
                       ↓ HTTPS / OpenAI 兼容
┌─────────────────────────────────────────────────────┐
│ Layer 3: 网关层(Nginx / Caddy / Kong / LiteLLM)     │
│         域名 / TLS / 路由 / 鉴权 / 限流 / 日志        │
└─────────────────────────────────────────────────────┘
                       ↓ 内网
┌─────────────────────────────────────────────────────┐
│ Layer 2: 推理服务层(vLLM / SGLang / Ollama / ...)   │
│         多实例 / 多模型 / 负载均衡                    │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ Layer 1: 硬件层(GPU / CPU / RAM / 网络)             │
└─────────────────────────────────────────────────────┘
```

**规模越大,每一层就越复杂**:
- HomeLab 可能 Layer 3 都不需要(直接客户端连推理引擎)
- 中小企业一定要有 Layer 3(网关层是合规、安全、可观测性的基础)

---

## 2. 场景 A:个人 HomeLab(单 GPU,1-3 用户)

### 2.1 典型画像

| 维度 | 配置 |
|---|---|
| 硬件 | 1 张 3090 / 4090 / 单 Mac M2 Ultra |
| 用户 | 自己 + 家人 / 1-2 个朋友 |
| 用法 | ChatBox 客户端 / 自己开发的小应用 |
| 预算 | 零额外投入 |
| 容忍度 | 服务挂了,自己重启就行 |

### 2.2 极简架构(单进程,最小化)

```
   你的笔记本/手机
        ↓ http://192.168.1.100:11434
   家里的台式机
   └── Ollama(自启)
       └── Qwen3-7B
```

**实现**:

```bash
# 在家用台式机上(以 Linux 为例)
# 1. 装 Ollama,设置环境变量允许局域网访问
sudo systemctl edit ollama
# 添加:
# [Service]
# Environment="OLLAMA_HOST=0.0.0.0:11434"
sudo systemctl restart ollama

# 2. 拉模型
ollama pull qwen3:7b

# 3. 在家庭路由器上设置静态 IP(或 mDNS),让台式机的 IP 固定
# 4. 在 ChatBox / OpenAI 兼容客户端配置:
#    Base URL: http://192.168.1.100:11434/v1
#    Model: qwen3:7b
#    API Key: 随便写(Ollama 默认不鉴权)
```

### 2.3 升级版:加一层 Nginx + 简单鉴权

如果想从外网也能用,或者想给朋友共享但要简单防护:

```nginx
# /etc/nginx/conf.d/llm.conf
server {
    listen 443 ssl;
    server_name llm.yourdomain.com;
    
    ssl_certificate     /etc/letsencrypt/live/llm.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/llm.yourdomain.com/privkey.pem;
    
    # 极简鉴权:固定的 Bearer Token
    location / {
        set $valid_key 0;
        if ($http_authorization = "Bearer sk-your-secret-token-here") {
            set $valid_key 1;
        }
        if ($valid_key = 0) {
            return 401;
        }
        
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_read_timeout 600s;
    }
}
```

**注意事项**:
- 用 [Let's Encrypt](https://letsencrypt.org) 申请免费 HTTPS 证书
- `proxy_buffering off` 是 SSE 流式响应**必须**的,否则会卡顿
- `proxy_read_timeout 600s` 防止长输出超时

### 2.4 升级版进阶:内网穿透(无公网 IP)

如果你家是 NAT 上网无公网 IP,常见方案:

| 方案 | 优点 | 缺点 |
|---|---|---|
| **Tailscale**(推荐) | 零配置 + 端到端加密 + 跨平台 | 商业产品,免费版 100 设备/3 用户 |
| **frp** | 开源 + 自托管 | 需要公网中转服务器 |
| **Cloudflare Tunnel** | 免费 + 自动 HTTPS | 流量经过 CF,不适合敏感数据 |
| **WireGuard** | 性能最好 | 需要公网入口 |

> 💡 **HomeLab 推荐 Tailscale**:十分钟搞定,所有设备之间用 100.x.x.x 的私有 IP 互通,免去配置反向代理 + DNS + 证书的繁琐。

---

## 3. 场景 B:工作室 / 小团队(2-4 卡,10-50 用户)

### 3.1 典型画像

| 维度 | 配置 |
|---|---|
| 硬件 | 1-2 台机器,2-4 张 3090/4090,共 48-96GB 显存 |
| 用户 | 10-50 人(开发团队 / 小研究组) |
| 用法 | 自研产品 + 内部工具 + 个人调用混合 |
| 预算 | 服务器 5-20 万,运维零散 |
| 容忍度 | 工作时间不能挂,周末挂可以接受 |

### 3.2 推荐架构

```
       员工(50 人)
         ↓ HTTPS
    ┌─────────────────────────────────┐
    │ Nginx + LiteLLM(网关)         │
    │ - 域名 + TLS                    │
    │ - 用户级 API Key                │
    │ - 限流(RPM / TPM)              │
    │ - 日志 → SQLite / PostgreSQL    │
    └─────────────────────────────────┘
         ↓ 内网
    ┌──────────────┬──────────────┐
    │ vLLM (4090)  │ vLLM (4090)  │
    │ Qwen3-32B AWQ│ Qwen3-32B AWQ│
    │ port 8000    │ port 8001    │
    └──────────────┴──────────────┘
         ↑
    [负载均衡:由 Nginx 上游做]
```

### 3.3 关键组件:LiteLLM

[LiteLLM](https://github.com/BerriAI/litellm) 是一个**专为 LLM API 设计的网关**,提供:

- **OpenAI 兼容接口**,可代理 100+ 提供商(OpenAI / Claude / Gemini / 自部署 vLLM 等)
- **用户 / 团队 / 组织三级权限**
- **RPM / TPM 限流**
- **预算追踪**
- **请求日志 + 用量统计**
- **fallback / 重试 / 路由**

**部署示例**:

```yaml
# config.yaml
model_list:
  - model_name: qwen3-32b           # 暴露给用户的模型名
    litellm_params:
      model: openai/Qwen/Qwen3-32B-Instruct-AWQ
      api_base: http://10.0.1.10:8000/v1
      api_key: dummy
  - model_name: qwen3-32b           # 同名 = 自动负载均衡
    litellm_params:
      model: openai/Qwen/Qwen3-32B-Instruct-AWQ
      api_base: http://10.0.1.10:8001/v1
      api_key: dummy

general_settings:
  master_key: sk-litellm-master-secret-xxx
  database_url: "postgresql://litellm:pwd@localhost:5432/litellm"
```

```bash
docker run -d \
  -p 4000:4000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml --port 4000
```

启动后:
- 管理面板:`http://localhost:4000/ui` — 创建用户、发 key、看用量
- API 端点:`http://localhost:4000/v1/chat/completions` — 完全 OpenAI 兼容

### 3.4 多模型混合部署策略

```yaml
# 实例 1:NVIDIA 4090,跑大模型
- Qwen3-32B-AWQ          → vLLM,port 8000

# 实例 2:NVIDIA 4090,跑小模型 + 嵌入
- Qwen3-7B-AWQ           → vLLM,port 8001(快速通用)
- bge-m3                  → Infinity / TEI,port 8002(嵌入)
- bge-reranker-v2-m3      → Infinity,port 8003(重排)

# 实例 3:CPU 服务器,跑工具
- whisper-large-v3        → faster-whisper,port 8004(语音转文字)
```

> 💡 **诀窍**:**小模型扎堆放一卡,大模型独占一卡**。Qwen3-7B + bge + Reranker 一张 4090 24G 完全够,Qwen3-32B 必须独占。

---

## 4. 场景 C:中小企业(4-8 卡,50-500 用户)

### 4.1 典型画像

| 维度 | 配置 |
|---|---|
| 硬件 | 1-3 台 8 卡服务器,A100 / H100 / 4090 / L40S |
| 用户 | 50-500 人(整个公司) |
| 用法 | 产品 API / 内部工具 / Coding Copilot / RAG 知识库 |
| 预算 | 服务器 30-200 万,运维专人 |
| 容忍度 | SLA 99% 以上(年度宕机 < 87.6 小时)|

### 4.2 推荐架构

```
                    外部用户 + 内部员工 + 应用
                              ↓
                     ┌─────────────────┐
                     │ 负载均衡器       │
                     │ (NLB / HAProxy) │
                     └────────┬────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        │ LiteLLM 集群(2+ 实例,共享 PostgreSQL)   │
        │ + Prometheus / Grafana / Loki             │
        └─────────────────────┬─────────────────────┘
                              ↓ 内网
   ┌──────────┬──────────┬──────────┬──────────┐
   │ vLLM x4  │ vLLM x4  │ vLLM x2  │ Infinity │
   │ Qwen-72B │ Qwen-72B │ Qwen-32B │ bge-m3 + │
   │ (TP=2)   │ (TP=2)   │ AWQ      │ reranker │
   └──────────┴──────────┴──────────┴──────────┘
       8x A100              4x 4090      2x A10
```

### 4.3 关键设计点

#### 4.3.1 隔离层:模型 vs 网关 vs 用户

| 层 | 不该跨越的边界 |
|---|---|
| 模型层 | 不该直接对外暴露(没鉴权 / 没限流 / 内核版本绑死) |
| 网关层 | 不该承担推理(无 GPU)|
| 用户层 | 不该直接配模型 endpoint(改一次 = 改所有客户端)|

#### 4.3.2 多副本与故障切换

```yaml
# LiteLLM 多副本配置
model_list:
  - model_name: qwen-flagship
    litellm_params:
      model: openai/Qwen/Qwen2.5-72B-Instruct
      api_base: http://gpu-1.internal:8000/v1
    model_info: {weight: 1}    # 权重 1
  - model_name: qwen-flagship
    litellm_params:
      model: openai/Qwen/Qwen2.5-72B-Instruct
      api_base: http://gpu-2.internal:8000/v1
    model_info: {weight: 1}

router_settings:
  routing_strategy: simple-shuffle  # 或 least-busy / latency-based
  num_retries: 3
  timeout: 60
```

#### 4.3.3 数据隔离

| 数据类型 | 隔离层级 |
|---|---|
| 用户 prompt | 默认不存(隐私);需要的话单独脱敏后存 |
| API 调用日志 | 按团队 / 部门拆库 |
| 模型权重 | 共享(同公司) |
| KV cache | 进程级隔离(用户 A 的 cache 不能被 B 命中) |

> ⚠️ **重要**:**LiteLLM 默认会把请求日志存到数据库**——如果业务涉及敏感数据(医疗、金融),必须配置 `litellm_settings.turn_off_message_logging: true`,或自建脱敏中间件。

#### 4.3.4 推荐辅助组件

| 组件 | 作用 | 部署难度 |
|---|---|---|
| **Prometheus** | 指标采集(QPS / 延迟 / 显存) | ⭐⭐ |
| **Grafana** | 仪表盘可视化 | ⭐⭐ |
| **Loki** | 日志聚合 | ⭐⭐⭐ |
| **OpenTelemetry** | 全链路 trace | ⭐⭐⭐⭐ |
| **Langfuse** | LLM 专用 trace + eval | ⭐⭐⭐ |

---

## 5. 反向代理与统一网关

### 5.1 Nginx 配置(最常用)

```nginx
# /etc/nginx/conf.d/llm-gateway.conf
upstream litellm {
    server 10.0.1.20:4000;
    server 10.0.1.21:4000 backup;     # 备机
}

# 限流:每 IP 每秒 10 请求,峰值 30
limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;

server {
    listen 443 ssl http2;
    server_name api.your-company.com;
    
    ssl_certificate     /etc/letsencrypt/live/api.your-company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.your-company.com/privkey.pem;
    
    # 大请求体支持(多模态 base64 图片可能很大)
    client_max_body_size 50M;
    
    location /v1/ {
        limit_req zone=perip burst=30 nodelay;
        
        proxy_pass http://litellm;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE 流式响应关键配置
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        chunked_transfer_encoding off;
        
        # 超时
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }
}
```

### 5.2 Caddy 配置(更简洁)

```caddy
# Caddyfile - 自动 HTTPS,无需手动证书
api.your-company.com {
    reverse_proxy 10.0.1.20:4000 10.0.1.21:4000 {
        lb_policy round_robin
        health_uri /health
        health_interval 30s
    }
}
```

### 5.3 关键参数详解

| 参数 | 作用 | 必须性 |
|---|---|---|
| `proxy_buffering off` | SSE 流式必须 | ⭐⭐⭐⭐⭐ |
| `proxy_read_timeout 600s` | 长输出不超时 | ⭐⭐⭐⭐⭐ |
| `client_max_body_size 50M` | 多模态图片上传 | ⭐⭐⭐⭐ |
| `chunked_transfer_encoding off` | SSE 兼容 | ⭐⭐⭐⭐ |
| `gzip off` (在该 location)| 不压缩流式响应 | ⭐⭐⭐⭐ |

---

## 6. API Key 管理与限流

### 6.1 API Key 的设计原则

| 维度 | 设计建议 |
|---|---|
| **格式** | `sk-<env>-<random>` 模仿 OpenAI:`sk-prod-abc123...` |
| **存储** | **数据库存哈希(bcrypt / argon2),不存明文** |
| **轮转** | 每 90 天提醒一次,提供"无缝轮转"(双 key 并行) |
| **作用域** | 绑定到具体模型 / 模型组 / IP 段 |
| **失效** | 立即失效需要数据库黑名单 + 网关缓存刷新 |

### 6.2 限流的三种维度

```
┌─────────────────────────────────────────┐
│ 维度 1:RPM(Requests Per Minute)       │
│ 防止暴力调用              典型:60/min   │
├─────────────────────────────────────────┤
│ 维度 2:TPM(Tokens Per Minute)         │
│ 防止用单个超长请求打爆    典型:200k/min │
├─────────────────────────────────────────┤
│ 维度 3:Budget(月度预算)               │
│ 商业模式所需              典型:$50/月   │
└─────────────────────────────────────────┘
```

LiteLLM 原生支持三种限流,在 UI 上对每个 key 配置。

### 6.3 防滥用最小套件

| 措施 | 实现 |
|---|---|
| **IP 白名单**(强约束) | Nginx 的 `allow / deny` |
| **JWT 鉴权**(SSO) | 网关层(LiteLLM 支持 JWT) |
| **Prompt 注入检测** | 见 [Agent 安全攻防](../06_Agent工程/Agent安全攻防.md) |
| **请求大小上限** | Nginx `client_max_body_size` |
| **审计日志** | 所有请求落库 + 定期 audit |
| **敏感词过滤** | 网关层正则 / LLM-as-Judge |

---

## 7. 监控与日志

### 7.1 必须看的 4 个指标

| 指标 | 含义 | 告警阈值参考 |
|---|---|---|
| **QPS** | 每秒请求数 | 突然增 5 倍以上,可能被刷 |
| **P95 延迟** | 95% 请求的响应时间 | 超过 5 秒,用户开始抱怨 |
| **GPU 利用率** | nvidia-smi 的 GPU-Util | 持续 95%+ 说明扛不住了 |
| **显存使用** | nvidia-smi 的 Memory-Usage | 95%+ 说明 KV cache 快爆 |

### 7.2 推荐栈:Prometheus + Grafana + DCGM

```bash
# 1. NVIDIA DCGM Exporter(GPU 指标)
docker run -d --gpus all --rm -p 9400:9400 \
  nvcr.io/nvidia/k8s/dcgm-exporter:latest

# 2. vLLM 自带 /metrics 端点(Prometheus 格式)
# 直接在 prometheus.yml 加 scrape config

# 3. Prometheus 拉取
# scrape_configs:
#   - job_name: 'vllm'
#     static_configs: [{ targets: ['gpu-1:8000', 'gpu-2:8001'] }]
#   - job_name: 'dcgm'
#     static_configs: [{ targets: ['gpu-1:9400', 'gpu-2:9400'] }]

# 4. Grafana 导入仪表盘(社区已有 vLLM / DCGM 的现成模板)
```

### 7.3 LLM 专用观测:Langfuse

普通 APM 看不到的 LLM 特殊维度:
- 每个请求的 **完整 prompt + completion**(开发环境必备)
- **每模型成本对比**
- **CoT 思考链可视化**
- **用户级 / 会话级追踪**

```python
# 客户端集成示例
from langfuse import Langfuse
from langfuse.openai import OpenAI  # 自动埋点

client = OpenAI(base_url="https://api.your-company.com/v1")
# 之后正常调用,Langfuse 自动记录
```

---

## 8. 容灾与高可用

### 8.1 单机版的"容灾"

```
对象:1 张 4090,Ollama 进程
方案:
  ① systemd 自启 + RestartSec=10(进程崩溃自动重启)
  ② NUT 不间断电源(防突然断电烧硬盘)
  ③ 每周全盘备份模型 + 配置(rsync 到 NAS)
```

### 8.2 多机版的高可用

```
对象:多台 GPU 服务器
方案:
  ① LiteLLM 集群 + Postgres 共享状态
  ② 每个模型至少 2 副本(N+1 冗余)
  ③ Nginx upstream backup + health check
  ④ 主备数据中心(成本极高,中小企业很少做)
```

### 8.3 升级与发布

| 策略 | 说明 |
|---|---|
| **滚动升级** | 先升 1 个节点,验证 → 全量 |
| **蓝绿发布** | 整批换新,出问题秒切回旧 |
| **金丝雀** | 5% 流量先用新版本,观察 30 分钟再全量 |
| **影子流量** | 新旧并行,新版本只读不返,对比效果 |

> 💡 **中小企业实践**:**滚动升级** 是最实用的——不需要双倍硬件,出问题影响范围小。

---

## 9. 成本预算速查

### 9.1 硬件成本(2026 年初参考价)

| 配置 | 显存 | 价格(人民币) | 适用 |
|---|---|---|---|
| 1x 二手 3090 | 24GB | 5-7k | 个人 HomeLab |
| 1x 4090 | 24GB | 14-18k | 个人高端 |
| 2x 3090 + NVLink | 48GB | 12-15k | 小工作室 |
| 4x 4090 服务器 | 96GB | 80-120k | 小团队 |
| 8x A100 80G | 640GB | 200-400 万 | 中大型企业 |
| 1x Apple M2 Ultra 192GB | 192GB 统一内存 | 5-7 万 | Mac 玩家旗舰 |

### 9.2 电费 / 网费

| 项目 | 月度成本 |
|---|---|
| 4090 单卡 24h × 30 天(0.6 元/度,~450W)| 约 200 元 |
| 8x A100 服务器整机 24h(~6kW)| 约 2600 元 |
| 家用 200M 宽带 | 60-100 元 |
| 企业 100M 专线 | 1000-3000 元 |

### 9.3 自建 vs 用 API 的盈亏平衡点

```
公式:
  自建月成本 = 硬件折旧/24 + 电费 + 运维工时

例(单 4090):
  硬件折旧:15000 / 36 = 417 元/月
  电费:200 元/月
  运维:周末 1 小时 ≈ 0(自己干)
  ─────────────────────────
  合计:617 元/月

调用商业 API 同等量的成本:
  qwen-plus 0.0008 元/1k input + 0.002 元/1k output
  假设月调用 100M token (输入 70M + 输出 30M):
    100M × 0.0014 平均 = 140 元
  → API 便宜!

  但如果月调用 1B token (输入 700M + 输出 300M):
    1B × 0.0014 平均 = 1400 元
  → 自建开始有优势

  10B token 月调用:
    → 自建优势巨大(API 1.4 万,自建 617 元)
```

> 💡 **决策原则**:**月调用量 < 1 亿 token,建议用 API(省心)**;**月调用量 > 10 亿 token + 有数据合规要求,建议自建**。

---

## 10. 与本知识库其他章节的关联

- **前置:模型选**:[各家 LLM 模型特点速查](各家LLM模型特点速查.md)——选哪家的哪个模型
- **前置:精度 / 量化**:[本地部署模型量化选型](本地部署模型量化选型.md)——决定显存占用
- **前置:推理引擎**:[LLM 推理引擎选型](LLM推理引擎选型.md)——本架构图里的"Layer 2"
- **前置:硬件**:[NVIDIA 显卡架构与 AI 算力](../05_技术基础/NVIDIA显卡架构与AI算力.md)——决定能跑什么
- **前置:工程基础**:[NVIDIA 驱动 / CUDA / PyTorch](../05_技术基础/NVIDIA驱动-CUDA-PyTorch工程基础.md)——服务器初始化必走
- **平行:商业 API 选型**:[LLM-API 选型方法论](LLM-API选型方法论.md)——自建 vs 用 API 的决策框架
- **下游:接入应用**:[Claude Code 实战速查](../06_Agent工程/Claude%20Code%20实战速查.md)——接 CC 用国产模型
- **安全**:[Agent 安全攻防](../06_Agent工程/Agent安全攻防.md)——网关层的防注入 / DLP 等
- **接口标准**:[LLM 接口规范实战](LLM接口规范实战.md)——下游所有客户端都走 OpenAI 兼容

---

## 11. 术语速查

| 术语 | 含义 |
|---|---|
| **HomeLab** | 家庭实验室,通常 1-2 张消费级显卡 |
| **网关 / Gateway** | 部署架构中的 Layer 3,统一入口 |
| **LiteLLM** | 流行的 LLM API 网关,支持 100+ 提供商 |
| **Nginx / Caddy** | 反向代理服务器,SSL / 路由 / 限流 |
| **upstream** | Nginx 术语,代表后端服务集群 |
| **SSE** | Server-Sent Events,LLM 流式响应的协议 |
| **TLS / HTTPS** | 传输层加密,生产环境必须 |
| **Let's Encrypt** | 免费 SSL 证书颁发机构 |
| **Tailscale / WireGuard** | 现代 VPN / 内网穿透方案 |
| **frp** | 开源内网穿透工具 |
| **RPM / TPM** | Requests / Tokens Per Minute,限流单位 |
| **JWT** | JSON Web Token,无状态鉴权方式 |
| **Bearer Token** | HTTP Authorization Header 格式 |
| **Prometheus** | 主流时序数据库 + 指标采集 |
| **Grafana** | 主流可视化仪表盘 |
| **DCGM Exporter** | NVIDIA 官方 GPU 指标采集器 |
| **Langfuse** | LLM 专用 trace / eval 平台 |
| **SLA** | Service Level Agreement,服务质量协议(如 99.9% 可用)|
| **N+1 冗余** | 至少多一份备份的容量规划 |
| **滚动升级 / 蓝绿 / 金丝雀** | 三种零停机发布策略 |
| **盈亏平衡点** | 自建 vs API 成本相等的调用量阈值 |

---

## 12. 作者声明、来源与局限性

### 12.1 作者声明

> ⚠️ **本篇是 Claude 基于公开技术资料和通用工程经验整理的科普综述,不是 LINUX DO @flymyd 的实战经验帖**。
>
> 原作者在「简单易懂的 LLM 相关知识梳理」目录中标记 ep.4「适合从 HomeLab 到小型企业的开源模型的各种部署方法」为待填坑,本笔记为补位之作。

### 12.2 主要来源

- LiteLLM 文档:https://docs.litellm.ai
- vLLM 部署文档:https://docs.vllm.ai/en/latest/serving/deploying_with_docker.html
- NVIDIA DCGM Exporter:https://github.com/NVIDIA/dcgm-exporter
- Caddy 反向代理:https://caddyserver.com/docs/quick-starts/reverse-proxy
- Tailscale:https://tailscale.com/kb
- Langfuse:https://langfuse.com/docs
- 知乎、Reddit、HN 上多个 self-host LLM 的经验帖(综合整理)

### 12.3 本笔记的局限性

| 维度 | 局限性 |
|---|---|
| **缺真实事故案例** | 没有"周三凌晨 3 点 OOM 把客户全挤掉"的生活化细节 |
| **企业级超大规模(1000 卡 +)** | 本文止步于中小企业,**超大集群 K8s + Volcano + Karmada 调度未涉及** |
| **K8s 部署** | 本文以"裸机 + Docker"为主,**K8s + Kubeflow / KubeRay 等云原生方案**没展开 |
| **多租户深度隔离** | 强隔离场景(政企内不同部门数据完全不能互通)需要更复杂的方案 |
| **国产化合规** | 信创要求 / 国产 GPU 全栈 / 等保三级的具体细节未覆盖 |
| **冷启动优化** | 模型加载、显存预热、JIT 编译等冷启动时间问题 |
| **CI/CD 集成** | 自动化模型版本发布、A/B 测试、灰度发布流程 |

### 12.4 给读者的建议

- **个人 HomeLab**:从 Ollama + 内网开始,够用就别折腾
- **小工作室**:LiteLLM + vLLM 是最实用的组合,**LiteLLM 的免费版功能足够覆盖大部分需求**
- **中小企业**:**多花点时间在 LiteLLM 的策略配置上**(用户管理 / 限流 / 预算),硬件可以渐进扩展
- **超大规模**:本文不够用,需要专门的 MLOps 团队,**推荐参考 NVIDIA NIM、Anyscale、Modal 等商业方案**
