#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核对网站数据文件 assets/js/data.js 与 Runaway.xlsx 是否一致。

    python tools/verify_site.py
"""
import json
import os
import subprocess
import sys

from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = r"C:\Users\93619\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
XLSX = os.path.join(ROOT, "Runaway.xlsx")

problems = []
count = 0


def ok(label, cond, detail=""):
    global count
    count += 1
    if not cond:
        problems.append("%s  %s" % (label, detail))


def load_site_data():
    js = ("global.window = {};require(%s);"
          "process.stdout.write(JSON.stringify(global.window.CATALOG_DATA));") % \
        json.dumps(os.path.join(ROOT, "assets", "js", "data.js").replace("\\", "\\\\"))
    p = subprocess.run([NODE, "-e", js], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("执行 data.js 失败: %s" % p.stderr.decode("utf-8", "replace"))
    return json.loads(p.stdout.decode("utf-8"))


site = load_site_data()
wb = load_workbook(XLSX, data_only=True)

# ---------------- 公告 ----------------
ws = wb["公告内容"]
title = ""
lines = []
for r in range(2, ws.max_row + 1):
    label = str(ws.cell(row=r, column=1).value or "").strip()
    body = str(ws.cell(row=r, column=2).value or "").strip()
    if not body:
        continue
    if label.startswith("公告标题"):
        title = body
    else:
        lines.append(body)

ok("公告标题一致", site["site"]["noticeTitle"] == title,
   "%r != %r" % (site["site"].get("noticeTitle"), title))
ok("公告正文条数", len(site["site"]["notice"]) == len(lines),
   "%d != %d" % (len(site["site"]["notice"]), len(lines)))
ok("公告正文内容", site["site"]["notice"] == lines)
ok("站名 Runaway", site["site"]["name"] == "Runaway", repr(site["site"]["name"]))

# ---------------- 分类 ----------------
sheet_names = [s for s in wb.sheetnames if s not in ("公告内容", "采集汇总")]
site_cats = [c["name"] for c in site["categories"]]
ok("第一个分类是「全部」", site_cats[0] == "全部", repr(site_cats[:1]))
ok("分类数 = 全部 + 商品表数", len(site_cats) == len(sheet_names) + 1,
   "%d != %d" % (len(site_cats), len(sheet_names) + 1))
ok("分类覆盖所有商品表", set(sheet_names) <= set(site_cats),
   "缺少 %s" % (set(sheet_names) - set(site_cats)))
ok("分类无多余项", set(site_cats) - {"全部"} == set(sheet_names),
   "多出 %s" % (set(site_cats) - {"全部"} - set(sheet_names)))

# ---------------- 商品 ----------------
total = 0
out_count = 0
for sname in sheet_names:
    ws = wb[sname]
    rows = []
    for r in range(2, ws.max_row + 1):
        name = str(ws.cell(row=r, column=1).value or "").strip()
        if not name:
            continue
        price = ws.cell(row=r, column=3).value
        stock = ws.cell(row=r, column=4).value
        status = str(ws.cell(row=r, column=5).value or "").strip()
        rows.append((name, price, stock, status))

    cat = next(c for c in site["categories"] if c["name"] == sname)
    items = [p for p in site["products"] if p["cat"] == cat["id"]]
    ok("[%s] 商品数量" % sname, len(items) == len(rows),
       "站内 %d / Excel %d" % (len(items), len(rows)))
    ok("[%s] 顺序与 Excel 一致" % sname,
       [p["name"] for p in items] == [r[0] for r in rows])

    for p, (name, price, stock, status) in zip(items, rows):
        ok("[%s] %s 价格" % (sname, name), abs(p["price"] - float(price)) < 1e-9,
           "%r != %r" % (p["price"], price))
        ok("[%s] %s 库存" % (sname, name), int(p["stock"]) == int(stock),
           "%r != %r" % (p["stock"], stock))
        want = "缺货" if int(stock) == 0 else (status or "有货")
        ok("[%s] %s 库存状态" % (sname, name), p["stockStatus"] == want,
           "%r != %r" % (p["stockStatus"], want))
        if want == "缺货":
            out_count += 1
        ok("[%s] %s 图片路径存在" % (sname, name),
           os.path.exists(os.path.join(ROOT, p["img"].replace("/", os.sep))), p["img"])
        ok("[%s] %s 价格两位小数" % (sname, name), round(p["price"], 2) == p["price"])
    total += len(items)

ok("商品总数", total == len(site["products"]), "%d" % total)
ok("站内商品总数与 Excel 一致", total == sum(
    1 for s in sheet_names for r in range(2, wb[s].max_row + 1)
    if str(wb[s].cell(row=r, column=1).value or "").strip()))
ok("缺货条数统计", out_count == sum(1 for p in site["products"] if p["stockStatus"] == "缺货"),
   "%d" % out_count)

# ---------------- 输出 ----------------
print("站点数据: assets/js/data.js")
print("公告标题: %s" % site["site"]["noticeTitle"])
print("公告正文: %d 条" % len(site["site"]["notice"]))
print()
print("分类 (%d):" % len(site["categories"]))
for i, c in enumerate(site["categories"], 1):
    n = len([p for p in site["products"] if p["cat"] == c["id"]])
    print("  %d. %-22s %2d 件" % (i, c["name"], n))
print()
print("商品总数: %d    缺货: %d    有货: %d"
      % (total, out_count, total - out_count))
print("核对项: %d，通过 %d，失败 %d" % (count, count - len(problems), len(problems)))
if problems:
    print("\n失败明细:")
    for p in problems[:40]:
        print("  -", p)
    sys.exit(1)
print("全部通过 ✓")
