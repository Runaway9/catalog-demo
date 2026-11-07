#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「青屿优选.xlsx」——把 catalog-demo 站点的真实数据导出成 Excel 工作簿。

数据来源：
  * 商品数据 : assets/js/data.js  (window.CATALOG_DATA)
  * 公告标题 : index.html          (.notice-title)
  * 公告正文 : assets/js/data.js  (site.notice，按网页渲染顺序)

用法： python tools/build_xlsx.py
"""
import json
import os
import re
import subprocess
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = r"C:\Users\93619\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
OUT = os.path.join(ROOT, "青屿优选.xlsx")

# ---------------------------------------------------------------- 取数据
def load_catalog():
    """用 Node 执行 data.js，拿到 window.CATALOG_DATA 的真实内容。"""
    js = (
        "global.window = {};"
        "require(%s);"
        "process.stdout.write(JSON.stringify(global.window.CATALOG_DATA));"
    ) % json.dumps(os.path.join(ROOT, "assets", "js", "data.js").replace("\\", "\\\\"))
    p = subprocess.run([NODE, "-e", js], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("读取 data.js 失败: %s" % p.stderr.decode("utf-8", "replace"))
    return json.loads(p.stdout.decode("utf-8"))


def load_notice_title():
    """公告标题现在由 data.js 提供（index.html 里由脚本填充）。"""
    return load_catalog().get("site", {}).get("noticeTitle", "")


# ---------------------------------------------------------------- 样式
HEADER_FILL = PatternFill("solid", fgColor="2563EB")
HEADER_FONT = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
BODY_FONT = Font(name="微软雅黑", size=10)
TITLE_FONT = Font(name="微软雅黑", size=10, bold=True)
THIN = Side(style="thin", color="D9DEE8")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

WRAP_TOP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center")
LEFT_TOP = Alignment(horizontal="left", vertical="top")


def style_header(sheet, headers):
    for idx, name in enumerate(headers, start=1):
        c = sheet.cell(row=1, column=idx, value=name)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    sheet.row_dimensions[1].height = 26


def set_widths(sheet, widths):
    for idx, w in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(idx)].width = w


# ---------------------------------------------------------------- 建表
def build_notice_sheet(wb, title, lines):
    ws = wb.active
    ws.title = "公告内容"
    style_header(ws, ["项目", "内容"])

    ws.append(["公告标题", title])
    for i, line in enumerate(lines, start=1):
        ws.append(["公告正文 %d" % i, line])

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=2):
        for c in row:
            c.font = BODY_FONT
            c.border = BORDER
            c.alignment = WRAP_TOP
        row[0].font = TITLE_FONT
        row[0].alignment = LEFT_TOP

    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 92
    ws.freeze_panes = "A2"
    return ws


PRODUCT_HEADERS = ["商品 ID", "商品名称", "分类", "售价（元）", "原价（元）",
                   "库存", "库存状态", "标签", "商品简介", "规格参数", "图片路径"]
PRODUCT_WIDTHS = [16, 26, 12, 12, 12, 9, 10, 9, 46, 40, 30]


def build_product_sheet(wb, sheet_name, cat_name, products):
    ws = wb.create_sheet(sheet_name)
    style_header(ws, PRODUCT_HEADERS)

    for p in products:
        specs = p.get("specs") or []
        spec_text = "\n".join("%s：%s" % (k, v) for k, v in specs)
        ws.append([
            p["id"],
            p["name"],
            cat_name,
            p.get("price"),
            p.get("origPrice"),          # 缺失 -> None -> 空单元格
            p.get("stock"),
            p.get("stockStatus") or "",
            p.get("tag"),                # 缺失 -> 空
            p.get("desc") or "",
            spec_text,
            p.get("img") or "",
        ])

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(PRODUCT_HEADERS)):
        for c in row:
            c.font = BODY_FONT
            c.border = BORDER
            c.alignment = LEFT_TOP
        row[3].number_format = "#,##0.00"   # 售价
        row[4].number_format = "#,##0.00"   # 原价
        row[5].number_format = "#,##0"      # 库存
        row[2].alignment = CENTER
        row[6].alignment = CENTER
        row[7].alignment = CENTER
        row[8].alignment = WRAP_TOP         # 商品简介
        row[9].alignment = WRAP_TOP         # 规格参数

    set_widths(ws, PRODUCT_WIDTHS)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(PRODUCT_HEADERS)), ws.max_row)
    return ws


def main():
    catalog = load_catalog()
    title = load_notice_title()
    notice_lines = catalog.get("site", {}).get("notice", [])
    categories = catalog.get("categories", [])
    products = catalog.get("products", [])

    wb = Workbook()
    build_notice_sheet(wb, title, notice_lines)

    # 「全部」是筛选入口，跳过；其余分类按网站顺序单独建表
    for cat in categories:
        if cat["id"] == "all":
            continue
        items = [p for p in products if p["cat"] == cat["id"]]
        build_product_sheet(wb, cat["name"], cat["name"], items)

    wb.save(OUT)
    print("已生成: %s" % OUT)
    print("公告标题: %s" % title)
    print("公告正文 %d 条" % len(notice_lines))
    print("商品 %d 件" % len(products))
    return 0


if __name__ == "__main__":
    sys.exit(main())
