#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新打开「青屿优选.xlsx」，并与 assets/js/data.js、index.html 的原始数据逐项核对。"""
import json
import os
import re
import subprocess
import sys

from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = r"C:\Users\93619\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
XLSX = os.path.join(ROOT, "青屿优选.xlsx")

problems = []
checks = []


def ok(label, cond, detail=""):
    checks.append((label, cond, detail))
    if not cond:
        problems.append("%s %s" % (label, detail))


def load_catalog():
    js = ("global.window = {};require(%s);"
          "process.stdout.write(JSON.stringify(global.window.CATALOG_DATA));") % \
        json.dumps(os.path.join(ROOT, "assets", "js", "data.js").replace("\\", "\\\\"))
    p = subprocess.run([NODE, "-e", js], cwd=ROOT, capture_output=True)
    return json.loads(p.stdout.decode("utf-8"))


catalog = load_catalog()
products = catalog["products"]
categories = catalog["categories"]
notice_lines = catalog["site"]["notice"]
title = catalog["site"]["noticeTitle"]

wb = load_workbook(XLSX, data_only=False)
names = wb.sheetnames

# 1) 工作表顺序
expected = ["公告内容"] + [c["name"] for c in categories if c["id"] != "all"]
ok("工作表顺序", names == expected, "实际=%s 期望=%s" % (names, expected))
ok("工作表数量", len(names) == len(expected), "实际 %d" % len(names))
ok("跳过「全部」", "全部" not in names)

# 2) 公告表
ws = wb["公告内容"]
hdr = [c.value for c in ws[1]]
ok("公告表列名", hdr == ["项目", "内容"], str(hdr))
ok("公告标题行", ws.cell(row=2, column=1).value == "公告标题" and
   ws.cell(row=2, column=2).value == title,
   "%r / %r" % (ws.cell(row=2, column=1).value, ws.cell(row=2, column=2).value))
body = [ws.cell(row=r, column=2).value for r in range(3, ws.max_row + 1)]
ok("公告正文条数", len(body) == len(notice_lines), "实际 %d 期望 %d" % (len(body), len(notice_lines)))
ok("公告正文顺序与内容一致", body == notice_lines)
ok("公告每条单独一行", all(isinstance(b, str) and b.strip() for b in body))

# 3) 商品表
HEADERS = ["商品 ID", "商品名称", "分类", "售价（元）", "原价（元）",
           "库存", "库存状态", "标签", "商品简介", "规格参数", "图片路径"]
total_rows = 0
for cat in categories:
    if cat["id"] == "all":
        continue
    cname = cat["name"]
    ws = wb[cname]
    hdr = [c.value for c in ws[1]]
    ok("[%s] 列名" % cname, hdr == HEADERS, str(hdr))

    src = [p for p in products if p["cat"] == cat["id"]]
    rows = list(ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True))
    ok("[%s] 商品数量" % cname, len(rows) == len(src),
       "实际 %d 期望 %d" % (len(rows), len(src)))
    total_rows += len(rows)

    for i, (row, p) in enumerate(zip(rows, src), start=2):
        tag = "[%s] 第%d行" % (cname, i)
        ok(tag + " ID", row[0] == p["id"], "%r != %r" % (row[0], p["id"]))
        ok(tag + " 名称", row[1] == p["name"])
        ok(tag + " 分类", row[2] == cname)
        ok(tag + " 售价为数字", isinstance(row[3], (int, float)) and
           abs(row[3] - p["price"]) < 1e-9, repr(row[3]))
        if p.get("origPrice") is None:
            ok(tag + " 原价留空", row[4] is None, repr(row[4]))
        else:
            ok(tag + " 原价为数字", isinstance(row[4], (int, float)) and
               abs(row[4] - p["origPrice"]) < 1e-9, repr(row[4]))
        ok(tag + " 库存为数字", isinstance(row[5], int) and row[5] == p["stock"], repr(row[5]))
        ok(tag + " 库存状态", (row[6] or "") == (p.get("stockStatus") or ""), repr(row[6]))
        ok(tag + " 标签", (row[7] or "") == (p.get("tag") or ""), repr(row[7]))
        ok(tag + " 简介", row[8] == p["desc"])
        expect_spec = "\n".join("%s：%s" % (k, v) for k, v in p["specs"])
        ok(tag + " 规格参数", row[9] == expect_spec)
        ok(tag + " 图片路径", row[10] == p["img"] and not row[10].startswith("/"), repr(row[10]))

    # 顺序与网站一致
    ok("[%s] 顺序与网站一致" % cname,
       [r[0] for r in rows] == [p["id"] for p in src])

ok("商品总数", total_rows == len(products), "实际 %d 期望 %d" % (total_rows, len(products)))

# 4) 格式
for cat in categories:
    if cat["id"] == "all":
        continue
    ws = wb[cat["name"]]
    ok("[%s] 冻结首行" % cat["name"], ws.freeze_panes == "A2", repr(ws.freeze_panes))
    ok("[%s] 自动筛选" % cat["name"], ws.auto_filter.ref is not None, repr(ws.auto_filter.ref))
    c = ws.cell(row=2, column=9)
    ok("[%s] 简介自动换行" % cat["name"], bool(c.alignment.wrap_text))
    c = ws.cell(row=2, column=10)
    ok("[%s] 规格自动换行" % cat["name"], bool(c.alignment.wrap_text))
    ok("[%s] 售价数字格式" % cat["name"],
       ws.cell(row=2, column=4).number_format == "#,##0.00",
       ws.cell(row=2, column=4).number_format)
    ok("[%s] 库存数字格式" % cat["name"],
       ws.cell(row=2, column=6).number_format == "#,##0",
       ws.cell(row=2, column=6).number_format)

ws = wb["公告内容"]
ok("[公告内容] 冻结首行", ws.freeze_panes == "A2", repr(ws.freeze_panes))
if ws.max_row >= 3:
    ok("[公告内容] 正文自动换行", bool(ws.cell(row=3, column=2).alignment.wrap_text))

# ---------------------------------------------------------------- 输出
print("文件: %s" % XLSX)
print("大小: %.1f KB" % (os.path.getsize(XLSX) / 1024.0))
print()
print("工作表顺序:")
for i, n in enumerate(names, 1):
    ws = wb[n]
    cnt = ws.max_row - 1
    extra = "（表头 1 行 + 数据 %d 行）" % cnt if n != "公告内容" else "（表头 1 行 + 数据 %d 行）" % cnt
    print("  %d. %-8s %s" % (i, n, extra))
print()
print("核对项: %d 项，通过 %d 项，失败 %d 项" %
      (len(checks), len(checks) - len(problems), len(problems)))
if problems:
    print("\n失败明细:")
    for p in problems[:40]:
        print("  -", p)
    sys.exit(1)
print("全部通过 ✓")
