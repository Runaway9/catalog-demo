#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整导出 Runaway.xlsx 的所有单元格，并检查隐藏表/隐藏行。"""
import os

from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "Runaway.xlsx")

wb = load_workbook(XLSX, data_only=True)
print("工作表列表 (%d):" % len(wb.sheetnames))
for ws in wb.worksheets:
    hidden_rows = [r for r, d in ws.row_dimensions.items() if d.hidden]
    print("  - %-24s state=%-8s rows=%-4d cols=%-3d hidden_rows=%s"
          % (ws.title, ws.sheet_state, ws.max_row, ws.max_column, hidden_rows))
print("=" * 90)

total = 0
for ws in wb.worksheets:
    print("\n### [%s]" % ws.title)
    for r in range(1, ws.max_row + 1):
        cells = []
        for c in range(1, ws.max_column + 1):
            cell = ws.cell(row=r, column=c)
            v = cell.value
            cells.append("%s" % ("" if v is None else v))
        print("  r%-3d | %s" % (r, " | ".join(cells)))
    if ws.title != "公告内容":
        n = ws.max_row - 1
        total += n
        print("  -> 商品数 %d" % n)

print("\n" + "=" * 90)
print("商品表合计: %d" % total)
