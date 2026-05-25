---
name: anti-performative-completion
enabled: true
event: stop
action: warn
conditions:
  - field: transcript
    operator: regex_match
    pattern: (?s)(✅.*){3,}.*已(检查|完成|验证|更新|同步|回填|确认)
---

🚩 **可能在表演性完成**

你刚才写了一串 ✅ 配 "已完成/已验证/已检查"。回头看每个 ✅ 后面是不是都跟着真命令的 stdout——没有的话，要么补跑命令把输出贴出来，要么把声明改成"我修改了 X，请用户核对"。
