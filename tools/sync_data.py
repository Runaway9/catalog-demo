#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 Runaway.xlsx 同步成网站的数据文件 assets/js/data.js。

    python tools/sync_data.py

规则
----
* 「公告内容」工作表 -> site.noticeTitle（第一行数据）+ site.notice（正文，空行跳过）
* 其余商品工作表     -> 每个工作表一个分类，工作簿内的行顺序即展示顺序
* 「采集汇总」        -> 不作为商品来源，只用于核对数量
* 商品没有可用图片时优先使用分类插图，其次使用统一占位图
* 库存为 0 时，库存状态显示「缺货」
"""
import io
import json
import os
import sys

from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "Runaway.xlsx")
OUT = os.path.join(ROOT, "assets", "js", "data.js")
PLACEHOLDER = "assets/img/placeholder.png"

SITE_NAME = "Runaway"
SITE_SLOGAN = "账号与礼品卡目录"

# 网站上分类标签的显示顺序；不在此列表里的商品表按工作簿顺序追加在后面
SHEET_ORDER = [
    "电报账号", "电报2月~1年", "电报1年以上", "推特账号", "苹果账号",
    "谷歌账号", "GPT系列", "其他账号", "电报业务",
]

# 工作表名 -> 分类 id（英文，用于生成稳定的商品 ID）
SHEET_IDS = {
    "电报账号": "telegram",
    "电报2月~1年": "telegram-2m-1y",
    "电报1年以上": "telegram-1y-plus",
    "推特账号": "twitter",
    "苹果账号": "apple",
    "苹果礼品卡（可充值GPT）": "itunes-giftcard",
    "谷歌账号": "google",
    "GPT系列": "gpt",
    "其他账号": "others",
    "电报业务": "telegram-service",
}

SUMMARY_SHEET = "采集汇总"
NOTICE_SHEET = "公告内容"

PRODUCT_COLUMNS = ["商品名称", "分类", "售价（元）", "库存", "库存状态", "标签"]
IMAGE_COLUMNS = ["图片", "图片路径", "封面", "图片地址"]


def js(value):
    """输出合法的 JS 字符串字面量。"""
    return json.dumps(value, ensure_ascii=False)


def cell_text(value):
    if value is None:
        return ""
    return str(value).strip()


def num(value, default=None):
    if value is None or value == "":
        return default
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return int(f) if f == int(f) else f


def read_notice(ws):
    """公告内容表：第一行数据是标题，其余按行是正文；空白内容跳过。"""
    title, lines = "", []
    for r in range(2, ws.max_row + 1):
        label = cell_text(ws.cell(row=r, column=1).value)
        body = cell_text(ws.cell(row=r, column=2).value)
        if not body:
            continue
        if label.startswith("公告标题") or (not title and not lines):
            title = body
        else:
            lines.append(body)
    return title, lines


def read_products(ws, sheet_name):
    """读取一张商品表，保留表内行顺序。"""
    header = [cell_text(ws.cell(row=1, column=c).value) for c in range(1, ws.max_column + 1)]
    idx = {name: i for i, name in enumerate(header) if name}

    def col(*names):
        for n in names:
            if n in idx:
                return idx[n]
        return None

    i_name = col("商品名称")
    i_price = col("售价（元）", "售价")
    i_stock = col("库存")
    i_status = col("库存状态")
    i_tag = col("标签")
    i_img = col(*IMAGE_COLUMNS)
    if i_name is None:
        return []

    items = []
    for r in range(2, ws.max_row + 1):
        name = cell_text(ws.cell(row=r, column=i_name + 1).value)
        if not name:
            continue                      # 跳过整行空白
        price = num(ws.cell(row=r, column=i_price + 1).value) if i_price is not None else None
        stock = num(ws.cell(row=r, column=i_stock + 1).value) if i_stock is not None else None
        stock = int(stock) if isinstance(stock, float) else stock
        raw_status = cell_text(ws.cell(row=r, column=i_status + 1).value) if i_status is not None else ""
        tag = cell_text(ws.cell(row=r, column=i_tag + 1).value) if i_tag is not None else ""

        if stock == 0:
            status = "缺货"
        elif raw_status:
            status = raw_status
        else:
            status = "有货"

        img = ""
        if i_img is not None:
            candidate = cell_text(ws.cell(row=r, column=i_img + 1).value)
            if candidate and os.path.exists(os.path.join(ROOT, candidate.replace("/", os.sep))):
                img = candidate
        items.append({
            "name": name,
            "price": price,
            "stock": stock,
            "status": status,
            "tag": tag,
            "img": img,
        })
    return items


def main():
    if not os.path.exists(XLSX):
        print("找不到 %s" % XLSX)
        return 1

    wb = load_workbook(XLSX, data_only=True)
    print("工作簿: %s" % XLSX)
    print("工作表: %s" % ", ".join(wb.sheetnames))

    # ---------------- 公告 ----------------
    notice_title, notice_lines = "", []
    if NOTICE_SHEET in wb.sheetnames:
        notice_title, notice_lines = read_notice(wb[NOTICE_SHEET])
    else:
        print("警告: 没有「%s」工作表" % NOTICE_SHEET)

    # ---------------- 商品 ----------------
    product_sheets = [s for s in wb.sheetnames
                      if s not in (NOTICE_SHEET, SUMMARY_SHEET)]
    ordered = [s for s in SHEET_ORDER if s in product_sheets]
    extra = [s for s in product_sheets if s not in SHEET_ORDER]
    ordered += extra
    if extra:
        print("提示: 以下商品表不在预设顺序中，已按工作簿顺序追加 -> %s" % ", ".join(extra))
    missing = [s for s in SHEET_ORDER if s not in wb.sheetnames]
    if missing:
        print("提示: 预设顺序中的工作表在附件里不存在，已跳过 -> %s" % ", ".join(missing))

    categories = [{"id": "all", "name": "全部"}]
    products = []
    total = 0
    for si, sheet_name in enumerate(ordered):
        items = read_products(wb[sheet_name], sheet_name)
        if not items:
            print("  跳过空表: %s" % sheet_name)
            continue
        cid = SHEET_IDS.get(sheet_name, "cat%d" % (si + 1))
        categories.append({"id": cid, "name": sheet_name})
        category_image = "assets/img/%s.svg" % cid
        if not os.path.isfile(os.path.join(ROOT, category_image)):
            category_image = PLACEHOLDER
        for i, it in enumerate(items, start=1):
            price = it["price"]
            specs = [
                ["分类", sheet_name],
                ["售价（元）", "%.2f" % price if isinstance(price, (int, float)) else ""],
                ["库存", str(it["stock"]) if it["stock"] is not None else ""],
                ["库存状态", it["status"]],
            ]
            if it["tag"]:
                specs.append(["标签", it["tag"]])
            desc = "%s · 库存 %s · %s" % (
                sheet_name,
                it["stock"] if it["stock"] is not None else "-",
                it["status"],
            )
            products.append({
                "id": "%s-%02d" % (cid, i),
                "name": it["name"],
                "cat": cid,
                "price": price,
                "origPrice": None,
                "stock": it["stock"],
                "stockStatus": it["status"],
                "tag": it["tag"] or None,
                "img": it["img"] or category_image,
                "desc": desc,
                "specs": specs,
            })
        total += len(items)
        print("  %-24s -> %-22s %2d 件" % (sheet_name, cid, len(items)))

    # ---------------- 采集汇总核对 ----------------
    if SUMMARY_SHEET in wb.sheetnames:
        ws = wb[SUMMARY_SHEET]
        numbers = []
        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                v = num(ws.cell(row=r, column=c).value)
                if isinstance(v, int):
                    numbers.append(v)
        print("采集汇总表里的整数: %s（本次导出 %d 件）" % (numbers, total))

    # ---------------- 写 data.js ----------------
    o = io.StringIO()
    o.write("""/* ==========================================================================
   %s — 站点数据（由 tools/sync_data.py 从 Runaway.xlsx 自动生成）
   --------------------------------------------------------------------------
   想改商品或公告，优先改 Excel（Runaway.xlsx）后运行：
       python tools/sync_data.py
   本文件由脚本覆盖生成，直接手改会在下次同步时丢失。
   ========================================================================== */

window.CATALOG_DATA = {
  site: {
    name: %s,
    slogan: %s,
    noticeTitle: %s,
    notice: [
""" % (SITE_NAME, js(SITE_NAME), js(SITE_SLOGAN), js(notice_title)))
    for line in notice_lines:
        o.write("      %s,\n" % js(line))
    o.write("""    ]
  },

  categories: [
""")
    for c in categories:
        o.write("    { id: %s, name: %s },\n" % (js(c["id"]), js(c["name"])))
    o.write("""  ],

  products: [
""")
    for p in products:
        o.write("    {\n")
        o.write("      id: %s,\n" % js(p["id"]))
        o.write("      name: %s,\n" % js(p["name"]))
        o.write("      cat: %s,\n" % js(p["cat"]))
        o.write("      price: %s,\n" % ("null" if p["price"] is None else repr(p["price"])))
        o.write("      origPrice: null,\n")
        o.write("      stock: %s,\n" % ("null" if p["stock"] is None else repr(p["stock"])))
        o.write("      stockStatus: %s,\n" % js(p["stockStatus"]))
        o.write("      tag: %s,\n" % js(p["tag"]))
        o.write("      img: %s,\n" % js(p["img"]))
        o.write("      desc: %s,\n" % js(p["desc"]))
        o.write("      specs: [\n")
        for k, v in p["specs"]:
            o.write("        [%s, %s],\n" % (js(k), js(v)))
        o.write("      ]\n")
        o.write("    },\n")
    o.write("""  ]
};
""")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(o.getvalue())

    print()
    print("已写入 %s" % OUT)
    print("分类 %d 个（全部 + %d）  商品 %d 件  缺货 %d 条"
          % (len(categories), len(categories) - 1, total,
             sum(1 for p in products if p["stockStatus"] == "缺货")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
