#!/usr/bin/env python3
"""MAEA Demo Sprint 心跳监控 — 检查 demo/ 目录产出变化"""

import os, json, sys
from datetime import datetime

DEMO_DIR = os.path.expanduser("~/projects/MAEA-Framework/demo")
STATE_FILE = os.path.expanduser("~/.hermes/data/maea-demo-heartbeat.json")

EXPECTED = ["protocol.py", "agents.py", "registry.py", "demo.py", "README.md"]

def check():
    files = {}
    for f in EXPECTED:
        path = os.path.join(DEMO_DIR, f)
        if os.path.exists(path):
            size = os.path.getsize(path)
            mtime = os.path.getmtime(path)
            files[f] = {"size": size, "mtime": mtime}
        else:
            files[f] = None

    # 读取上一次状态
    prev = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as fp:
            prev = json.load(fp)

    # 对比
    changes = []
    for f in EXPECTED:
        old = prev.get(f)
        new = files.get(f)
        if old is None and new is None:
            changes.append(f"  ⬜ {f}  未创建")
        elif old is None and new is not None:
            changes.append(f"  🆕 {f}  {new['size']}B")
        elif old is not None and new is None:
            changes.append(f"  ❌ {f}  已删除")
        elif old["size"] != new["size"]:
            delta = new["size"] - old["size"]
            sign = "+" if delta >= 0 else ""
            changes.append(f"  📝 {f}  {old['size']}→{new['size']}B ({sign}{delta})")
        else:
            changes.append(f"  — {f}  {new['size']}B  无变化")

    # 保存当前状态
    state = {}
    for f, v in files.items():
        if v is not None:
            state[f] = v
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as fp:
        json.dump(state, fp)

    # 计算完成度
    done = sum(1 for f in EXPECTED if files[f] is not None and files[f]["size"] > 200)
    pct = done * 100 // len(EXPECTED)

    # 是否是首次运行
    first_run = not prev

    now = datetime.now().strftime("%H:%M")
    
    # 判断是否需要输出
    has_changes = first_run
    if not first_run:
        for f in EXPECTED:
            old = prev.get(f)
            new = files.get(f)
            if (old is None) != (new is None): has_changes = True; break
            if old and new and old["size"] != new["size"]: has_changes = True; break

    if not has_changes:
        return None  # 静默

    status = "🔄 首次检查" if first_run else "📊 Sprint 心跳"
    
    return f"""{status} · {now}
{'─'*40}
完成度: {'█'*done}{'░'*(5-done)} {done}/{len(EXPECTED)} ({pct}%)
{'─'*40}
{chr(10).join(changes)}"""

result = check()
if result:
    print(result)
