#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runaway — 商品插画生成脚本
===========================================================================
用 Pillow 程序化绘制商品插画（640×640 PNG），风格统一、无版权风险。

    python tools/gen_images.py            # 生成全部
    python tools/gen_images.py --sheet    # 顺便输出预览大图

生成结果写入 assets/img/，文件名与 assets/js/data.js 中的 img 字段一一对应。
当前站点只在用 placeholder.png（统一占位图），其余条目是为旧版演示商品保留的，
需要时可以删掉 CATALOG 里对应的行再运行本脚本。
"""

import colorsys
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

# ----------------------------------------------------------------- 基本参数
S = 4                      # 超采样倍数（抗锯齿）
W = H = 640                # 成品尺寸
CW = CH = W * S            # 绘制画布尺寸
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'assets', 'img')

ACCENTS = ['#E76F51', '#1F6F6B', '#E9A23B', '#3E7CB1', '#8E6C9E']
CREAM = '#F6EFE2'


def hsv(h, s, v):
    """h/s/v in 0..1 -> (r, g, b) 0..255"""
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


class Canvas:
    """带超采样与常用绘图快捷方法的画布。"""

    def __init__(self, hue, sat=0.42):
        self.hue = hue
        self.sat = sat
        self.body = hsv(hue, sat, 0.80)
        self.dark = hsv(hue, sat + 0.10, 0.62)
        self.deep = hsv(hue, sat + 0.14, 0.50)
        self.light = hsv(hue, max(sat - 0.10, 0.0), 0.94)
        self.pale = hsv(hue, max(sat - 0.16, 0.0), 0.98)
        self.accent = ACCENTS[0]
        self.accent2 = ACCENTS[1]

        top = hsv(hue, sat * 0.45, 0.985)
        bot = hsv(hue, sat * 0.62, 0.905)
        img = Image.new('RGB', (CW, CH), top)
        d = ImageDraw.Draw(img)
        for y in range(CH):
            t = y / (CH - 1)
            d.line([(0, y), (CW, y)],
                   fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
        self.img = img
        self.d = ImageDraw.Draw(img, 'RGBA')

    # ---------------------------------------------------------- 基础图元
    def _s(self, box):
        return [v * S for v in box]

    def _p(self, pts):
        return [(x * S, y * S) for x, y in pts]

    def rrect(self, box, r, fill=None, outline=None, width=0):
        self.d.rounded_rectangle(self._s(box), radius=r * S, fill=fill,
                                 outline=outline, width=int(width * S))

    def ell(self, box, fill=None, outline=None, width=0):
        self.d.ellipse(self._s(box), fill=fill, outline=outline, width=int(width * S))

    def poly(self, pts, fill=None, outline=None, width=0):
        self.d.polygon(self._p(pts), fill=fill)
        if outline and width:
            self.d.line(self._p(list(pts) + [pts[0]]), fill=outline,
                        width=int(width * S), joint='curve')

    def line(self, pts, fill, width=2, joint='curve'):
        self.d.line(self._p(pts), fill=fill, width=int(width * S), joint=joint)

    def arc(self, box, start, end, fill, width=2):
        self.d.arc(self._s(box), start, end, fill=fill, width=int(width * S))

    def pie(self, box, start, end, fill=None, outline=None, width=0):
        self.d.pieslice(self._s(box), start, end, fill=fill, outline=outline,
                        width=int(width * S))

    # ---------------------------------------------------------- 装饰元素
    def dots(self, spots, color, r=6):
        for (cx, cy) in spots:
            self.ell([cx - r, cy - r, cx + r, cy + r], fill=color)

    def ring(self, cx, cy, r, color, width=3):
        self.ell([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)

    def shadow(self, cx=320, cy=505, rx=130, ry=17, alpha=26):
        layer = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse(self._s([cx - rx, cy - ry, cx + rx, cy + ry]),
                   fill=(60, 80, 120, alpha))
        layer = layer.filter(ImageFilter.GaussianBlur(radius=9 * S))
        self.img.paste(Image.alpha_composite(self.img.convert('RGBA'),
                                             layer).convert('RGB'), (0, 0))
        self.d = ImageDraw.Draw(self.img, 'RGBA')

    def save(self, name):
        os.makedirs(OUT_DIR, exist_ok=True)
        out = self.img.resize((W, H), Image.LANCZOS)
        path = os.path.join(OUT_DIR, name)
        out.save(path, 'PNG', optimize=True)
        return path


# ===================================================================== 数字
# 7 段数码管，用于翻页钟
SEG_MAP = {
    '0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc',
    '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg',
}


def digit(c, x, y, w, h, ch, color, t=None):
    """在 (x, y) 画一个宽 w 高 h 的 7 段数字。"""
    t = t or max(4, int(w * 0.17))
    segs = SEG_MAP.get(ch, '')
    hw, hh = w / 2.0, h / 2.0

    def bar(cx, cy, bw, bh, name):
        if name in segs:
            c.rrect([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2],
                    t / 2.0, fill=color)

    # a b c d e f g
    bar(x + hw / 2, y + t / 2, w - t, t, 'a')                       # top
    bar(x + w - t / 2, y + hh / 2, t, h - t, 'b')                   # top-right
    bar(x + w - t / 2, y + h - hh / 2, t, h - t, 'c')               # bottom-right
    bar(x + hw / 2, y + h - t / 2, w - t, t, 'd')                   # bottom
    bar(x + t / 2, y + h - hh / 2, t, h - t, 'e')                   # bottom-left
    bar(x + t / 2, y + hh / 2, t, h - t, 'f')                       # top-left
    bar(x + hw / 2, y + h / 2, w - t, t, 'g')                       # middle


# ============================================================== 商品绘制
def p_home_pillow(c):
    c.shadow(320, 500, 140, 18)
    # 靠垫主体（略带鼓感：两只交叠的圆角块）
    c.rrect([150, 165, 490, 470], 52, fill=c.body)
    c.rrect([150, 165, 490, 470], 52, outline=c.deep, width=3)
    # 内衬面板 + 滚边，形成典型的靠垫结构
    c.rrect([186, 200, 454, 434], 38, fill=c.light)
    c.rrect([186, 200, 454, 434], 38, outline=c.pale, width=5)
    # 右上角翻折（明显的一块深色折角）
    c.poly([(392, 168), (487, 168), (487, 263)], fill=c.dark)
    c.line([(392, 170), (392, 262), (486, 262)], c.deep, 4)
    c.poly([(392, 168), (487, 168), (487, 200), (440, 200)], fill=c.deep)
    # 织物褶皱
    c.arc([210, 250, 350, 370], 205, 335, c.body, 5)
    c.arc([300, 300, 450, 420], 190, 320, c.body, 5)
    c.dots([(508, 118), (536, 152), (512, 188)], c.light, 8)


def p_home_candle(c):
    c.shadow(320, 505, 95, 13)
    # 玻璃杯
    c.rrect([235, 300, 405, 495], 26, fill=(255, 255, 255, 120),
            outline=c.deep, width=4)
    # 蜡油
    c.rrect([246, 330, 394, 490], 20, fill=CREAM)
    c.ell([246, 316, 394, 344], fill=(250, 244, 232))
    # 灯芯
    c.line([(320, 318), (320, 292)], (70, 55, 40), 5)
    # 火焰
    c.poly([(320, 218), (347, 268), (338, 292), (320, 300), (302, 292),
            (293, 268)], fill=c.accent)
    c.ell([307, 258, 333, 296], fill='#FFD166')
    # 杯口高光
    c.arc([245, 302, 395, 340], 190, 350, (255, 255, 255, 200), 5)
    c.dots([(150, 180), (132, 215), (160, 248)], c.light, 7)


def p_home_mug(c):
    c.shadow(320, 500, 120, 15)
    # 把手（先画，被杯身遮住一半）
    c.ell([395, 300, 505, 420], outline=c.dark, width=20)
    # 杯身
    c.rrect([195, 245, 435, 470], 30, fill=c.body)
    c.rrect([195, 245, 435, 470], 30, outline=c.deep, width=3)
    # 杯口
    c.ell([195, 232, 435, 278], fill=c.light)
    c.ell([212, 243, 418, 270], fill=(90, 70, 55))
    # 高光
    c.rrect([228, 290, 252, 420], 12, fill=c.pale)
    c.dots([(480, 170), (510, 205)], c.light, 8)


def p_home_shelf(c):
    c.shadow(320, 515, 165, 16)
    # 交叉支架
    c.line([(232, 262), (408, 452)], c.dark, 13)
    c.line([(408, 262), (232, 452)], c.dark, 13)
    c.line([(232, 262), (232, 462)], c.dark, 11)
    c.line([(408, 262), (408, 462)], c.dark, 11)
    c.line([(232, 452), (408, 452)], c.dark, 10)
    # 层板
    c.rrect([175, 240, 465, 272], 10, fill=c.body)
    c.rrect([175, 240, 465, 272], 10, outline=c.deep, width=3)
    c.rrect([175, 418, 465, 450], 10, fill=c.body)
    c.rrect([175, 418, 465, 450], 10, outline=c.deep, width=3)
    # 层板上的小物件
    c.rrect([215, 195, 285, 240], 8, fill=c.light)
    c.rrect([300, 205, 345, 240], 8, fill=c.accent)
    c.dots([(120, 200), (145, 232)], c.light, 7)


def p_home_clock(c):
    c.shadow(320, 470, 105, 12)
    # 脚
    c.rrect([250, 425, 288, 462], 9, fill=c.dark)
    c.rrect([352, 425, 390, 462], 9, fill=c.dark)
    # 外壳
    c.ell([175, 160, 465, 450], fill=c.body, outline=c.deep, width=4)
    c.ell([203, 188, 437, 422], fill=c.pale)
    # 刻度
    for ang, (x1, y1, x2, y2) in {
        12: (320, 210, 320, 228), 3: (410, 305, 392, 305),
        6: (320, 400, 320, 382), 9: (230, 305, 248, 305),
    }.items():
        c.line([(x1, y1), (x2, y2)], c.dark, 7)
    # 指针
    c.line([(320, 305), (320, 235)], c.deep, 9)
    c.line([(320, 305), (378, 340)], c.accent, 8)
    c.ell([306, 291, 334, 319], fill=c.deep)
    c.dots([(110, 230), (138, 260)], c.light, 8)


def p_outdoor_backpack(c):
    c.shadow(320, 510, 135, 15)
    # 背带
    c.rrect([178, 235, 208, 470], 15, fill=c.dark)
    c.rrect([432, 235, 462, 470], 15, fill=c.dark)
    # 提手
    c.arc([262, 150, 378, 250], 190, 350, c.deep, 13)
    # 主体
    c.rrect([205, 205, 435, 495], 58, fill=c.body)
    c.rrect([205, 205, 435, 495], 58, outline=c.deep, width=3)
    # 顶盖
    c.pie([205, 195, 435, 400], 180, 360, fill=c.dark)
    c.rrect([205, 292, 435, 320], 14, fill=c.dark)
    # 前袋
    c.rrect([252, 340, 388, 452], 26, fill=c.light)
    c.rrect([252, 340, 388, 452], 26, outline=c.deep, width=3)
    # 扣具
    c.rrect([305, 292, 335, 322], 7, fill=c.accent)
    c.line([(268, 372), (372, 372)], c.deep, 4)
    c.dots([(135, 210), (108, 245)], c.light, 8)


def p_outdoor_bottle(c):
    c.shadow(320, 500, 80, 11)
    # 提环
    c.arc([300, 100, 400, 190], 195, 345, c.dark, 11)
    # 瓶盖
    c.rrect([262, 150, 378, 232], 16, fill=c.dark)
    for x in range(278, 368, 18):
        c.line([(x, 162), (x, 220)], c.deep, 4)
    # 颈环
    c.rrect([252, 222, 388, 252], 8, fill=c.deep)
    # 瓶身
    c.rrect([250, 244, 390, 492], 30, fill=c.body)
    c.rrect([250, 244, 390, 492], 30, outline=c.deep, width=3)
    # 高光
    c.rrect([275, 275, 295, 455], 10, fill=c.pale)
    c.rrect([355, 275, 368, 455], 6, fill=c.light)
    # 腰带
    c.rrect([250, 340, 390, 372], 6, fill=c.accent)
    c.dots([(150, 240), (128, 275)], c.light, 8)


def p_outdoor_chair(c):
    c.shadow(320, 505, 150, 14)
    # 椅背
    c.rrect([228, 175, 318, 305], 22, fill=c.body)
    c.rrect([228, 175, 318, 305], 22, outline=c.deep, width=3)
    c.line([(240, 225), (306, 225)], c.deep, 4)
    c.line([(240, 262), (306, 262)], c.deep, 4)
    # 座面
    c.poly([(222, 296), (430, 296), (452, 352), (240, 352)], fill=c.body)
    c.poly([(222, 296), (430, 296), (452, 352), (240, 352)], outline=c.deep, width=3)
    # X 型折叠腿
    c.line([(250, 350), (420, 478)], c.dark, 13)
    c.line([(420, 350), (250, 478)], c.dark, 13)
    c.line([(250, 350), (250, 478)], c.dark, 11)
    c.line([(420, 350), (420, 478)], c.dark, 11)
    # 束带
    c.rrect([310, 330, 350, 362], 6, fill=c.accent)
    c.dots([(470, 200), (496, 235)], c.light, 8)


def p_outdoor_umbrella(c):
    c.shadow(320, 505, 85, 11)
    # 伞尖
    c.poly([(320, 112), (334, 152), (306, 152)], fill=c.deep)
    # 收拢的伞面（宽而长，明显是折叠状态）
    c.poly([(266, 152), (374, 152), (346, 396), (294, 396)], fill=c.body)
    c.poly([(266, 152), (374, 152), (346, 396), (294, 396)], outline=c.deep, width=3)
    # 伞骨褶皱
    c.line([(320, 154), (320, 394)], c.deep, 4)
    c.line([(286, 158), (305, 392)], c.light, 7)
    c.line([(354, 158), (335, 392)], c.light, 7)
    c.line([(276, 158), (299, 392)], c.dark, 4)
    c.line([(364, 158), (341, 392)], c.dark, 4)
    # 横向缠绕带
    for y in (196, 300):
        c.rrect([274, y, 366, y + 22], 8, fill=c.accent)
    # 伞杆
    c.line([(320, 396), (320, 436)], c.deep, 14)
    # J 形手柄
    c.line([(320, 436), (320, 452)], c.deep, 14)
    c.arc([268, 440, 366, 528], 0, 180, c.deep, 15)
    c.rrect([312, 498, 330, 524], 9, fill=c.deep)
    c.dots([(160, 250), (135, 288)], c.light, 8)


def p_outdoor_cutlery(c):
    c.shadow(320, 505, 145, 12)
    # 勺
    c.ell([215, 175, 295, 285], fill=c.body)
    c.ell([230, 192, 280, 268], fill=c.light)
    c.rrect([242, 278, 268, 480], 13, fill=c.body)
    # 叉
    for i in range(4):
        c.rrect([312 + i * 20, 160, 322 + i * 20, 232], 5, fill=c.body)
    c.rrect([308, 225, 396, 262], 12, fill=c.body)
    c.rrect([340, 258, 364, 480], 12, fill=c.body)
    # 刀
    c.poly([(430, 162), (470, 162), (470, 300), (438, 300), (430, 250)], fill=c.body)
    c.rrect([438, 296, 462, 480], 12, fill=c.body)
    # 束带
    c.rrect([230, 350, 470, 376], 8, fill=c.accent)
    c.dots([(150, 200), (128, 235)], c.light, 8)


def p_digital_charger(c):
    c.shadow(320, 500, 120, 13)
    # 底座
    c.ell([180, 250, 460, 420], fill=c.deep)
    # 顶面
    c.ell([180, 218, 460, 388], fill=c.body)
    c.ell([180, 218, 460, 388], outline=c.deep, width=3)
    # 磁吸环
    c.ell([238, 262, 402, 356], outline=c.light, width=7)
    c.ell([268, 278, 372, 340], outline=c.pale, width=4)
    # 指示灯
    c.ell([312, 300, 328, 316], fill=c.accent)
    # 线缆
    c.line([(320, 418), (320, 470), (420, 480), (470, 440)], c.dark, 12)
    c.dots([(135, 230), (112, 268)], c.light, 8)


def p_digital_stand(c):
    c.shadow(320, 500, 165, 14)
    # 支撑斜面
    c.poly([(212, 352), (350, 168), (416, 205), (278, 388)], fill=c.body)
    c.poly([(212, 352), (350, 168), (416, 205), (278, 388)], outline=c.deep, width=3)
    # 防滑条
    for i in range(3):
        c.line([(258 + i * 42, 320 - i * 30), (300 + i * 42, 352 - i * 30)],
               c.light, 8)
    # 底座
    c.poly([(168, 430), (300, 392), (478, 434), (346, 472)], fill=c.body)
    c.poly([(168, 430), (300, 392), (478, 434), (346, 472)], outline=c.deep, width=3)
    # 前挡沿
    c.rrect([160, 418, 232, 452], 12, fill=c.dark)
    c.dots([(505, 195), (528, 230)], c.light, 8)


def p_digital_cable(c):
    c.shadow(320, 500, 135, 13)
    # 盘绕的线
    for r, col, wd in ((150, c.dark, 13), (112, c.body, 13), (74, c.light, 13)):
        c.arc([320 - r, 300 - r * 0.86, 320 + r, 300 + r * 0.86], 200, 340, col, wd)
    c.arc([320 - 150, 300 - 129, 320 + 150, 300 + 129], 18, 150, c.dark, 13)
    c.arc([320 - 74, 300 - 64, 320 + 74, 300 + 64], 22, 140, c.light, 13)
    # 接头
    c.rrect([452, 168, 492, 258], 9, fill=c.accent)
    c.rrect([462, 258, 482, 300], 6, fill=c.deep)
    c.rrect([148, 372, 188, 462], 9, fill=c.accent)
    c.rrect([158, 320, 178, 372], 6, fill=c.deep)
    c.dots([(150, 190), (128, 228)], c.light, 8)


def p_digital_mouse(c):
    c.shadow(320, 500, 90, 11)
    # 机身
    c.rrect([212, 175, 428, 468], 92, fill=c.body)
    c.rrect([212, 175, 428, 468], 92, outline=c.deep, width=3)
    # 上盖分割线
    c.line([(320, 178), (320, 300)], c.deep, 4)
    # 滚轮
    c.rrect([308, 200, 332, 252], 12, fill=c.accent)
    # 侧键
    c.arc([214, 300, 320, 380], 140, 230, c.deep, 4)
    # 底部指示条
    c.rrect([250, 430, 390, 448], 9, fill=c.light)
    c.dots([(500, 215), (523, 250)], c.light, 8)


def p_digital_powerbank(c):
    c.shadow(320, 500, 110, 12)
    # 机身
    c.rrect([198, 165, 442, 480], 34, fill=c.body)
    c.rrect([198, 165, 442, 480], 34, outline=c.deep, width=3)
    # 电量灯
    for i in range(4):
        c.ell([238 + i * 26, 208, 252 + i * 26, 222], fill=c.accent)
    # 容量条
    c.rrect([238, 248, 402, 262], 7, fill=c.light)
    # USB 接口
    c.rrect([282, 412, 358, 436], 8, fill=c.deep)
    c.rrect([292, 418, 348, 430], 6, fill=c.pale)
    # 提环
    c.arc([390, 120, 470, 190], 200, 340, c.dark, 11)
    c.dots([(140, 300), (118, 336)], c.light, 8)


def p_kitchen_pot(c):
    c.shadow(320, 500, 150, 14)
    # 两侧把手
    c.rrect([138, 300, 188, 340], 14, fill=c.dark)
    c.rrect([452, 300, 502, 340], 14, fill=c.dark)
    # 锅身
    c.rrect([185, 260, 455, 468], 40, fill=c.body)
    c.rrect([185, 260, 455, 468], 40, outline=c.deep, width=3)
    # 锅盖
    c.ell([175, 205, 465, 305], fill=c.light)
    c.ell([175, 205, 465, 305], outline=c.deep, width=3)
    c.ell([205, 222, 435, 288], fill=c.pale)
    # 盖钮
    c.rrect([300, 165, 340, 215], 14, fill=c.accent)
    c.ell([292, 152, 348, 186], fill=c.accent)
    # 珐琅彩条
    c.rrect([185, 372, 455, 392], 6, fill=c.accent)
    c.dots([(120, 210), (98, 245)], c.light, 8)


def p_kitchen_pour(c):
    c.shadow(320, 505, 115, 12)
    # 鹅颈壶嘴：从壶身右肩升起，绕过头顶向左下弯出
    c.line([(396, 262), (398, 180)], c.dark, 19)
    c.arc([268, 112, 398, 242], 180, 360, c.dark, 19)
    c.line([(272, 176), (250, 214)], c.dark, 19)
    c.ell([236, 200, 268, 228], fill=c.deep)
    # 手柄
    c.arc([142, 256, 262, 414], 90, 270, c.dark, 16)
    c.rrect([196, 300, 238, 328], 13, fill=c.dark)
    # 壶身
    c.rrect([232, 236, 402, 486], 38, fill=c.body)
    c.rrect([232, 236, 402, 486], 38, outline=c.deep, width=3)
    # 壶盖
    c.ell([226, 208, 408, 272], fill=c.light)
    c.ell([226, 208, 408, 272], outline=c.deep, width=3)
    c.ell([294, 180, 340, 214], fill=c.dark)
    # 束带
    c.rrect([232, 360, 402, 384], 7, fill=c.accent)
    c.dots([(468, 300), (496, 336)], c.light, 8)


def p_kitchen_scissors(c):
    c.shadow(320, 500, 145, 13)
    # 刀刃
    c.poly([(292, 320), (486, 172), (508, 200), (306, 336)], fill=c.body)
    c.poly([(292, 320), (486, 172), (508, 200), (306, 336)], outline=c.deep, width=3)
    c.poly([(292, 320), (486, 468), (508, 440), (306, 304)], fill=c.light)
    c.poly([(292, 320), (486, 468), (508, 440), (306, 304)], outline=c.deep, width=3)
    # 连接柄的金属臂
    c.line([(292, 320), (196, 268)], c.deep, 15)
    c.line([(292, 320), (196, 372)], c.deep, 15)
    # 指环
    c.ell([128, 208, 262, 330], outline=c.accent, width=20)
    c.ell([128, 310, 262, 432], outline=c.accent, width=20)
    # 铆钉
    c.ell([272, 300, 312, 340], fill=c.dark)
    c.ell([283, 311, 301, 329], fill=c.light)
    c.dots([(130, 150), (160, 140)], c.light, 8)


def p_kitchen_colander(c):
    c.shadow(320, 500, 140, 13)
    # 碗身
    c.poly([(178, 292), (462, 292), (398, 438), (242, 438)], fill=c.body)
    c.poly([(178, 292), (462, 292), (398, 438), (242, 438)], outline=c.deep, width=3)
    # 碗沿
    c.ell([170, 266, 470, 320], fill=c.light)
    c.ell([170, 266, 470, 320], outline=c.deep, width=3)
    # 沥水孔
    for row, (ys, n) in enumerate(((332, 5), (372, 4), (408, 3))):
        for i in range(n):
            x = 235 + i * (170 // max(n - 1, 1))
            c.ell([x - 8, ys - 8, x + 8, ys + 8], fill=c.deep)
    # 把手
    c.rrect([452, 280, 528, 306], 13, fill=c.dark)
    c.dots([(140, 220), (116, 252)], c.light, 8)


def p_kitchen_jars(c):
    c.shadow(320, 505, 165, 13)
    jars = [(168, 258, 118), (300, 312, 96), (428, 282, 84)]
    for idx, (x, top, w) in enumerate(jars):
        body_c = c.body if idx != 1 else c.light
        c.rrect([x, top, x + w, 480], 16, fill=body_c)
        c.rrect([x, top, x + w, 480], 16, outline=c.deep, width=3)
        # 木盖
        c.rrect([x - 7, top - 34, x + w + 7, top + 2], 12, fill=c.dark)
        c.ell([x - 7, top - 46, x + w + 7, top - 16], fill=c.accent if idx == 1 else c.dark)
        # 标签
        c.rrect([x + 12, top + 60, x + w - 12, top + 122], 8, fill=c.pale)
        c.line([(x + 22, top + 82), (x + w - 22, top + 82)], c.deep, 4)
        c.line([(x + 22, top + 100), (x + w - 34, top + 100)], c.light, 4)
    c.dots([(120, 190), (96, 222)], c.light, 8)


def p_office_clock(c):
    c.shadow(320, 480, 140, 12)
    # 机身
    c.rrect([160, 235, 480, 430], 28, fill=c.body)
    c.rrect([160, 235, 480, 430], 28, outline=c.deep, width=3)
    # 两个翻页面板
    for idx, x in enumerate((196, 336)):
        c.rrect([x, 268, x + 108, 396], 12, fill=c.pale)
        c.rrect([x, 268, x + 108, 396], 12, outline=c.deep, width=3)
        # 翻页缝隙
        c.line([(x, 332), (x + 108, 332)], c.deep, 4)
        # 上半页数字
        digit(c, x + 16, 282, 34, 44, '1' if idx == 0 else '3', c.deep)
        digit(c, x + 58, 282, 34, 44, '2' if idx == 0 else '4', c.deep)
        # 下半页数字
        digit(c, x + 16, 338, 34, 44, '0' if idx == 0 else '5', c.accent)
        digit(c, x + 58, 338, 34, 44, '8' if idx == 0 else '6', c.accent)
    # 底部按钮
    c.rrect([268, 406, 372, 424], 9, fill=c.dark)
    c.dots([(520, 190), (545, 224)], c.light, 8)


def p_office_pouch(c):
    c.shadow(320, 430, 150, 12)
    # 主体
    c.rrect([165, 262, 475, 400], 44, fill=c.body)
    c.rrect([165, 262, 475, 400], 44, outline=c.deep, width=3)
    # 拉链
    c.line([(190, 296), (440, 296)], c.deep, 6)
    for x in range(200, 440, 26):
        c.line([(x, 288), (x, 304)], c.light, 4)
    # 拉头
    c.rrect([434, 278, 472, 314], 10, fill=c.accent)
    c.rrect([448, 314, 458, 350], 5, fill=c.deep)
    # 缝线
    c.line([(200, 358), (440, 358)], c.light, 3)
    c.dots([(140, 180), (116, 212)], c.light, 8)


def p_office_notebook(c):
    c.shadow(320, 505, 135, 13)
    # 封面
    c.rrect([182, 145, 458, 488], 12, fill=c.body)
    c.rrect([182, 145, 458, 488], 12, outline=c.deep, width=3)
    # 方格纹
    for x in range(210, 450, 40):
        c.line([(x, 170), (x, 462)], c.light, 3)
    for y in range(178, 470, 40):
        c.line([(206, y), (434, y)], c.light, 3)
    # 书脊
    c.rrect([182, 145, 214, 488], 10, fill=c.dark)
    # 弹力绳
    c.rrect([368, 145, 388, 488], 6, fill=c.accent)
    c.dots([(120, 230), (96, 262)], c.light, 8)


def p_office_sticky(c):
    c.shadow(320, 480, 140, 12)
    # 便签叠层
    for i in range(4):
        off = i * 7
        c.rrect([206 + off, 258 + off, 424 - off, 452 - off], 8,
                fill=c.light if i == 3 else c.pale)
    # 顶层便签文字线
    for i in range(4):
        c.line([(238, 300 + i * 26), (392, 300 + i * 26)], c.deep, 4)
    # 顶边
    c.rrect([227, 258, 403, 282], 6, fill=c.body)
    # 笔
    c.rrect([432, 250, 456, 420], 12, fill=c.accent)
    c.poly([(432, 420), (456, 420), (444, 452)], fill=c.deep)
    c.rrect([432, 238, 456, 254], 7, fill=c.dark)
    c.dots([(150, 200), (126, 232)], c.light, 8)


def p_office_stapler(c):
    c.shadow(320, 480, 150, 12)
    # 底座
    c.poly([(160, 412), (452, 412), (472, 452), (152, 452)], fill=c.body)
    c.poly([(160, 412), (452, 412), (472, 452), (152, 452)], outline=c.deep, width=3)
    # 上臂
    c.poly([(186, 330), (444, 296), (456, 342), (196, 378)], fill=c.body)
    c.poly([(186, 330), (444, 296), (456, 342), (196, 378)], outline=c.deep, width=3)
    # 铰链
    c.ell([428, 288, 476, 336], fill=c.dark)
    # 前端压脚
    c.rrect([176, 372, 236, 414], 10, fill=c.dark)
    # 装订槽
    c.rrect([300, 380, 360, 400], 9, fill=c.deep)
    c.dots([(150, 220), (126, 252)], c.light, 8)


def p_apparel_cap(c):
    c.shadow(320, 450, 150, 12)
    # 帽檐
    c.poly([(250, 330), (566, 344), (552, 396), (252, 372)], fill=c.dark)
    c.poly([(250, 330), (566, 344), (552, 396), (252, 372)], outline=c.deep, width=3)
    # 帽冠
    c.pie([182, 218, 462, 428], 180, 360, fill=c.body)
    c.pie([182, 218, 462, 428], 180, 360, outline=c.deep, width=3)
    # 帽檐分界
    c.line([(182, 330), (462, 330)], c.deep, 4)
    # 透气孔
    c.ell([258, 262, 274, 278], fill=c.deep)
    c.ell([330, 248, 346, 264], fill=c.deep)
    c.ell([398, 268, 414, 284], fill=c.deep)
    # 调节扣
    c.rrect([230, 322, 300, 342], 9, fill=c.accent)
    c.dots([(125, 230), (100, 262)], c.light, 8)


def p_apparel_tote(c):
    c.shadow(320, 510, 150, 13)
    # 提手
    c.arc([228, 148, 412, 322], 180, 360, c.dark, 15)
    c.arc([228, 148, 412, 322], 186, 300, c.deep, 4)
    # 袋身
    c.poly([(172, 276), (468, 276), (452, 500), (188, 500)], fill=c.body)
    c.poly([(172, 276), (468, 276), (452, 500), (188, 500)], outline=c.deep, width=3)
    # 上口翻边
    c.rrect([168, 262, 472, 300], 12, fill=c.light)
    c.rrect([168, 262, 472, 300], 12, outline=c.deep, width=3)
    # 内衬
    c.rrect([196, 292, 444, 318], 8, fill=c.pale)
    # 缝线
    c.line([(210, 330), (218, 470)], c.light, 3)
    c.line([(430, 330), (422, 470)], c.light, 3)
    c.dots([(130, 200), (106, 232)], c.light, 8)


def p_apparel_watch(c):
    c.shadow(320, 520, 90, 10)
    # 表带
    c.rrect([290, 70, 350, 240], 22, fill=c.dark)
    c.rrect([290, 400, 350, 570], 22, fill=c.dark)
    for y in range(92, 228, 26):
        c.line([(298, y), (342, y)], c.deep, 4)
    for y in range(424, 560, 26):
        c.line([(298, y), (342, y)], c.deep, 4)
    # 表壳
    c.ell([222, 218, 418, 414], fill=c.body)
    c.ell([222, 218, 418, 414], outline=c.deep, width=4)
    # 表盘
    c.ell([248, 244, 392, 388], fill=c.pale)
    # 刻度
    for ang in range(0, 360, 30):
        import math as _m
        r1, r2 = 58, 66
        cx, cy = 320, 316
        a = _m.radians(ang)
        c.line([(cx + r1 * _m.cos(a), cy + r1 * _m.sin(a)),
                (cx + r2 * _m.cos(a), cy + r2 * _m.sin(a))], c.dark, 4)
    # 指针
    c.line([(320, 316), (320, 262)], c.deep, 8)
    c.line([(320, 316), (368, 336)], c.accent, 7)
    c.ell([308, 304, 332, 328], fill=c.deep)
    # 表冠
    c.rrect([414, 296, 438, 322], 8, fill=c.dark)
    c.dots([(140, 200), (116, 232)], c.light, 8)


def p_apparel_socks(c):
    c.shadow(320, 500, 140, 12)
    # 后面的袜子
    c.rrect([356, 200, 428, 350], 18, fill=c.light)
    c.poly([(356, 344), (428, 344), (486, 398), (486, 448), (356, 448)], fill=c.light)
    c.rrect([356, 196, 428, 236], 10, fill=c.accent)
    # 前面的袜子
    c.rrect([222, 160, 300, 330], 20, fill=c.body)
    c.poly([(222, 324), (300, 324), (356, 380), (356, 434), (222, 434)], fill=c.body)
    c.rrect([222, 156, 300, 198], 11, fill=c.accent)
    # 织纹
    c.line([(240, 230), (282, 230)], c.light, 4)
    c.line([(240, 262), (282, 262)], c.light, 4)
    c.line([(240, 294), (282, 294)], c.light, 4)
    c.dots([(140, 230), (116, 262)], c.light, 8)


def p_apparel_scarf(c):
    c.shadow(320, 460, 155, 12)
    # 折叠主体
    c.rrect([168, 190, 472, 398], 22, fill=c.body)
    c.rrect([168, 190, 472, 398], 22, outline=c.deep, width=3)
    # 编织横纹
    for i in range(5):
        y = 216 + i * 38
        c.line([(184, y), (456, y)], c.light, 7)
    # 对折边
    c.rrect([168, 190, 472, 232], 20, fill=c.dark)
    c.rrect([168, 190, 472, 232], 20, outline=c.deep, width=3)
    # 流苏
    for i in range(11):
        x = 186 + i * 26
        c.line([(x, 396), (x, 432)], c.dark, 6)
        c.line([(x, 432), (x - 4, 448)], c.dark, 5)
    c.dots([(125, 180), (102, 212)], c.light, 8)


def p_beauty_cleanser(c):
    c.shadow(320, 500, 95, 11)
    # 翻盖
    c.rrect([268, 430, 372, 496], 14, fill=c.dark)
    c.rrect([282, 424, 358, 448], 10, fill=c.deep)
    # 管身
    c.poly([(258, 168), (382, 168), (368, 438), (272, 438)], fill=c.body)
    c.poly([(258, 168), (382, 168), (368, 438), (272, 438)], outline=c.deep, width=3)
    # 封口
    c.rrect([254, 152, 386, 178], 8, fill=c.light)
    # 标签
    c.rrect([272, 250, 368, 330], 10, fill=c.pale)
    c.line([(288, 276), (352, 276)], c.deep, 5)
    c.line([(288, 302), (340, 302)], c.light, 5)
    c.dots([(160, 220), (136, 252)], c.light, 8)


def p_beauty_mask(c):
    c.shadow(320, 480, 150, 12)
    # 袋体
    c.rrect([160, 205, 480, 448], 18, fill=c.body)
    c.rrect([160, 205, 480, 448], 18, outline=c.deep, width=3)
    # 封边
    c.rrect([160, 205, 480, 245], 12, fill=c.light)
    for x in range(178, 468, 22):
        c.line([(x, 208), (x, 242)], c.deep, 3)
    # 中央圆形标
    c.ell([258, 282, 382, 406], fill=c.pale)
    c.ell([258, 282, 382, 406], outline=c.deep, width=3)
    c.ell([296, 320, 344, 368], fill=c.accent)
    # 两侧文字线
    c.line([(186, 286), (240, 286)], c.light, 6)
    c.line([(186, 312), (228, 312)], c.light, 6)
    c.line([(400, 286), (454, 286)], c.light, 6)
    c.line([(400, 312), (442, 312)], c.light, 6)
    c.dots([(120, 190), (96, 222)], c.light, 8)


def p_beauty_handcream(c):
    c.shadow(320, 500, 80, 10)
    # 盖子
    c.rrect([272, 430, 368, 496], 14, fill=c.dark)
    for x in range(288, 360, 14):
        c.line([(x, 438), (x, 486)], c.deep, 3)
    # 管身
    c.rrect([252, 190, 388, 442], 26, fill=c.body)
    c.rrect([252, 190, 388, 442], 26, outline=c.deep, width=3)
    # 封口
    c.rrect([258, 176, 382, 202], 8, fill=c.light)
    # 标签
    c.rrect([272, 268, 368, 348], 10, fill=c.pale)
    c.line([(290, 292), (350, 292)], c.deep, 5)
    c.line([(290, 320), (332, 320)], c.light, 5)
    c.dots([(165, 250), (141, 282)], c.light, 8)


def p_beauty_toothbrush(c):
    c.shadow(320, 505, 85, 10)
    # 底座
    c.ell([248, 470, 392, 516], fill=c.light)
    c.rrect([248, 462, 392, 492], 12, fill=c.dark)
    # 手柄
    c.rrect([282, 235, 358, 478], 30, fill=c.body)
    c.rrect([282, 235, 358, 478], 30, outline=c.deep, width=3)
    # 电源键
    c.ell([302, 300, 338, 336], fill=c.accent)
    # 颈
    c.rrect([292, 200, 348, 248], 16, fill=c.light)
    # 刷头
    c.rrect([286, 132, 354, 212], 22, fill=c.body)
    c.rrect([286, 132, 354, 212], 22, outline=c.deep, width=3)
    # 刷毛
    c.rrect([292, 112, 348, 142], 12, fill=c.deep)
    for i in range(6):
        c.line([(300 + i * 9, 116), (300 + i * 9, 138)], c.pale, 3)
    c.dots([(160, 250), (136, 282)], c.light, 8)


def p_beauty_towel(c):
    c.shadow(320, 455, 155, 12)
    # 上面一条
    c.rrect([186, 196, 454, 306], 20, fill=c.body)
    c.rrect([186, 196, 454, 306], 20, outline=c.deep, width=3)
    # 下面一条
    c.rrect([160, 300, 480, 424], 20, fill=c.light)
    c.rrect([160, 300, 480, 424], 20, outline=c.deep, width=3)
    # 织纹条
    c.rrect([186, 246, 454, 268], 8, fill=c.accent)
    c.rrect([160, 350, 480, 372], 8, fill=c.accent)
    # 毛边
    for x in range(200, 460, 24):
        c.line([(x, 264), (x, 290)], c.pale, 4)
    c.dots([(120, 200), (96, 232)], c.light, 8)


def p_placeholder(c):
    """统一占位图：没有真实图片的商品都用它。"""
    c.shadow(320, 500, 150, 13)
    # 箱体
    c.rrect([178, 252, 462, 462], 18, fill=c.body)
    c.rrect([178, 252, 462, 462], 18, outline=c.deep, width=3)
    # 箱盖
    c.rrect([160, 196, 480, 264], 12, fill=c.light)
    c.rrect([160, 196, 480, 264], 12, outline=c.deep, width=3)
    # 封箱胶带
    c.rrect([300, 196, 340, 462], 6, fill=c.accent)
    c.line([(320, 196), (320, 462)], c.deep, 3)
    # 中央标记
    c.rrect([258, 318, 382, 388], 12, fill=c.pale)
    c.ell([300, 336, 340, 368], fill=c.light)
    c.line([(266, 410), (374, 410)], c.light, 5)
    c.dots([(140, 210), (116, 244)], c.light, 8)


# ================================================================== 商品表
# (文件名, 绘制函数, 色相, 饱和度, 主强调色)
CATALOG = [
    ('home-pillow.png',      p_home_pillow,      0.56, 0.38, '#E9A23B'),
    ('home-candle.png',      p_home_candle,      0.60, 0.34, '#E76F51'),
    ('home-mug.png',         p_home_mug,         0.54, 0.30, '#E9A23B'),
    ('home-shelf.png',       p_home_shelf,       0.09, 0.42, '#1F6F6B'),
    ('home-clock.png',       p_home_clock,       0.52, 0.36, '#1F6F6B'),

    ('outdoor-backpack.png', p_outdoor_backpack, 0.34, 0.40, '#E9A23B'),
    ('outdoor-bottle.png',   p_outdoor_bottle,   0.46, 0.34, '#E76F51'),
    ('outdoor-chair.png',    p_outdoor_chair,    0.38, 0.44, '#E76F51'),
    ('outdoor-umbrella.png', p_outdoor_umbrella, 0.62, 0.40, '#1F6F6B'),
    ('outdoor-cutlery.png',  p_outdoor_cutlery,  0.30, 0.36, '#3E7CB1'),

    ('digital-charger.png',  p_digital_charger,  0.58, 0.36, '#1F6F6B'),
    ('digital-stand.png',    p_digital_stand,    0.63, 0.30, '#E9A23B'),
    ('digital-cable.png',    p_digital_cable,    0.50, 0.40, '#E9A23B'),
    ('digital-mouse.png',    p_digital_mouse,    0.55, 0.38, '#3E7CB1'),
    ('digital-powerbank.png', p_digital_powerbank, 0.68, 0.34, '#E76F51'),

    ('kitchen-pot.png',      p_kitchen_pot,      0.05, 0.46, '#1F6F6B'),
    ('kitchen-pour.png',     p_kitchen_pour,     0.02, 0.38, '#8E6C9E'),
    ('kitchen-scissors.png', p_kitchen_scissors, 0.72, 0.32, '#3E7CB1'),
    ('kitchen-colander.png', p_kitchen_colander, 0.14, 0.40, '#E9A23B'),
    ('kitchen-jars.png',     p_kitchen_jars,     0.09, 0.36, '#E76F51'),

    ('office-clock.png',     p_office_clock,     0.57, 0.34, '#E76F51'),
    ('office-pouch.png',     p_office_pouch,     0.08, 0.40, '#E9A23B'),
    ('office-notebook.png',  p_office_notebook,  0.66, 0.30, '#1F6F6B'),
    ('office-sticky.png',    p_office_sticky,    0.13, 0.42, '#E9A23B'),
    ('office-stapler.png',   p_office_stapler,   0.58, 0.28, '#E76F51'),

    ('apparel-cap.png',      p_apparel_cap,      0.97, 0.34, '#1F6F6B'),
    ('apparel-tote.png',     p_apparel_tote,     0.11, 0.40, '#3E7CB1'),
    ('apparel-watch.png',    p_apparel_watch,    0.60, 0.30, '#E9A23B'),
    ('apparel-socks.png',    p_apparel_socks,    0.44, 0.36, '#E9A23B'),
    ('apparel-scarf.png',    p_apparel_scarf,    0.93, 0.32, '#E76F51'),

    ('beauty-cleanser.png',  p_beauty_cleanser,  0.42, 0.36, '#E9A23B'),
    ('beauty-mask.png',      p_beauty_mask,      0.88, 0.34, '#1F6F6B'),
    ('beauty-handcream.png', p_beauty_handcream, 0.77, 0.30, '#E76F51'),
    ('beauty-toothbrush.png', p_beauty_toothbrush, 0.53, 0.38, '#3E7CB1'),
    ('beauty-towel.png',     p_beauty_towel,     0.36, 0.32, '#E9A23B'),

    # 统一占位图（没有真实图片的商品都使用它）
    ('placeholder.png',      p_placeholder,      0.58, 0.13, '#8A94A6'),
]


def contact_sheet(names):
    """把所有商品图拼成一张预览大图，方便肉眼检查。"""
    cols, cell, pad = 7, 150, 6
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (cell + pad) + pad,
                              rows * (cell + pad + 18) + pad), (245, 247, 251))
    d = ImageDraw.Draw(sheet)
    for i, name in enumerate(names):
        im = Image.open(os.path.join(OUT_DIR, name)).convert('RGB')
        im = im.resize((cell, cell), Image.LANCZOS)
        x = pad + (i % cols) * (cell + pad)
        y = pad + (i // cols) * (cell + pad + 18)
        sheet.paste(im, (x, y))
        d.text((x + 2, y + cell + 3), name[:-4][:20], fill=(60, 70, 90))
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '_contact_sheet.png')
    sheet.save(path)
    return path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fn, hue, sat, accent in CATALOG:
        c = Canvas(hue, sat)
        c.accent = accent
        fn(c)
        path = c.save(name)
        print('  ok  %-26s %s' % (name, os.path.basename(path)))

    print('\n完成：%d 张图片已写入 %s' % (len(CATALOG), OUT_DIR))

    if '--sheet' in sys.argv:
        print('预览大图：%s' % contact_sheet([n for n, _, _, _, _ in CATALOG]))


if __name__ == '__main__':
    main()
