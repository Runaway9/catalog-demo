# Runaway · 静态商品目录

一个**原生 HTML / CSS / JavaScript** 编写的中文商品目录页面，无需构建步骤、无需后端，
可以直接丢到 GitHub Pages、Netlify、对象存储或本地任意静态服务器上运行。

> 商品数据来自仓库根目录的 `Runaway.xlsx`，由脚本同步成 `assets/js/data.js`。
> 页面是**纯静态**的，只做展示与筛选，**不提供在线购买、支付、订单与配送**。

## 功能

- **分类筛选**：圆角胶囊标签，一键切换类目，浏览器内即时完成，无需刷新。
- **关键词搜索**：输入商品名 / 分类 / 标签 / 库存状态即时匹配，支持多关键词（空格分隔）。
- **搜索与分类叠加**：两者同时生效，可在一个类目里继续搜关键词。
- **分组列表**：按分类分组展示，每组可折叠收起，折叠状态在筛选后保留。
- **库存状态**：库存为 0 的商品统一显示「缺货」，并做淡化处理；也可以直接搜「缺货」。
- **商品详情**：点击「查看详情」弹出详情面板（图片、库存状态、参数表）。
- **响应式**：手机与桌面自适应，手机端商品行自动改为两栏紧凑布局。
- **相对路径**：所有图片与脚本均使用相对路径，部署到仓库子路径后依然可以正常加载。

## 目录结构

```
Runaway/
├── index.html                 # 页面结构
├── Runaway.xlsx               # ★ 商品与公告的数据源
├── assets/
│   ├── css/
│   │   └── style.css          # 全部样式（含移动端断点）
│   ├── js/
│   │   ├── data.js            # 站点数据（由 sync_data.py 从 Excel 生成）
│   │   └── app.js             # 分类 / 搜索 / 渲染逻辑
│   └── img/
│       └── placeholder.png    # 统一占位图（商品没有图片时使用）
└── tools/
    ├── sync_data.py           # Runaway.xlsx  ->  assets/js/data.js
    ├── verify_site.py         # 核对 data.js 与 Excel 是否一致
    ├── gen_images.py          # 生成商品插画 / 占位图
    └── build_xlsx.py          # 把站点数据导出成 Excel
```

## 更新商品与公告

**改 Excel，再跑一条命令：**

```bash
python tools/sync_data.py
```

脚本会读取 `Runaway.xlsx` 并重新生成 `assets/js/data.js`，然后刷新页面即可看到新内容。

### Excel 的表结构

| 工作表 | 作用 |
|---|---|
| `公告内容` | 两列：`项目` / `内容`。`公告标题` 行是公告标题，`公告正文 N` 行是正文，空单元格会被跳过 |
| 商品工作表 | 每张表一个分类，表内第一行是表头：`商品名称`、`分类`、`售价（元）`、`库存`、`库存状态`、`标签` |
| `采集汇总` | **不作为商品来源**，只用于核对数量 |

约定：

- 商品表的行顺序就是网页上的展示顺序。
- 分类标签的显示顺序见 `tools/sync_data.py` 里的 `SHEET_ORDER`；不在该列表里的表会按工作簿顺序追加在后面。
- `库存` 为 0 的商品，页面统一显示「缺货」（无论 `库存状态` 列写的是什么）。
- `售价（元）` 在页面上统一显示两位小数。
- 商品表可通过 `图片路径` 列指定本地图片。没有可用图片时，脚本按分类使用 `assets/img/<分类 ID>.svg`，没有分类插图时使用 `assets/img/placeholder.png`。

### 核对数据

```bash
python tools/verify_site.py
```

会逐条比对 `assets/js/data.js` 与 `Runaway.xlsx`：分类数量与名称、每个分类的商品数与顺序、
名称 / 价格 / 库存 / 库存状态 / 图片路径，并统计缺货条数。

## 本地预览

用任意静态服务器打开即可（**不要**直接双击 `index.html`，
部分浏览器会限制 `file://` 下的资源加载）：

```bash
# Python（任选其一）
python -m http.server 8000

# Node.js
npx serve .
```

然后访问 <http://localhost:8000/>。

## 导出成 Excel

把站点当前的数据导出成一份 Excel 工作簿（每类商品一张表）：

```bash
python tools/build_xlsx.py
```

输出为 `青屿优选.xlsx`。

## 重新生成商品图片

```bash
python tools/gen_images.py --sheet
```

脚本会用 Pillow 重新生成 `assets/img/` 下的 PNG（640×640），并输出一张预览大图。
目录使用 `assets/img/` 中的分类 SVG 插图，`placeholder.png` 用作缺少分类插图时的后备图片。

## 部署到 GitHub Pages

1. 推送 `main` 分支。
2. 在仓库 **Settings → Pages** 里把 Source 选为 *Deploy from a branch*，分支 `main`、目录 `/ (root)`。
   或用 CLI：
   ```bash
   gh api repos/<owner>/<repo>/pages -X POST -f source[branch]=main -f source[path]=/ 
   ```
3. 站点地址为 `https://<owner>.github.io/<repo>/`。

因为项目全部使用相对路径，部署到仓库子路径后无需任何额外配置即可正常显示。

## 技术说明

- 无框架、无依赖、无构建步骤，纯浏览器原生 API。
- 筛选逻辑集中在 `assets/js/app.js` 的 `filtered()` / `matches()` 两个函数里。
- 使用 `<details>` / `<summary>` 实现分组折叠，天然支持键盘操作与无障碍语义。
- 商品行使用 CSS Grid 的具名区域（`grid-template-areas`）实现桌面 / 手机两套布局。
- `data.js` 由脚本生成，请优先改 Excel；直接手改 `data.js` 会在下次同步时被覆盖。
