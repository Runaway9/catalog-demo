# 青屿优选 · 静态商品目录演示

一个**原生 HTML / CSS / JavaScript** 编写的中文商品目录演示站，无需构建步骤、无需后端，
可以直接丢到 GitHub Pages、Netlify、对象存储或本地任意静态服务器上运行。

> ⚠️ 这是一个**演示项目**：站内所有店名、商品名称、价格、库存、参数与图片均为原创虚构内容，
> 不提供真实的购买、支付、订单、物流或售后服务。项目中**已按要求省略**登录、购物车、下单与支付流程。

## 功能

- **分类筛选**：圆角胶囊标签，一键切换类目，浏览器内即时完成，无需刷新。
- **关键词搜索**：输入商品名 / 分类 / 标签 / 简介即时匹配，支持多关键词（空格分隔）。
- **分组列表**：按分类分组展示，每组可折叠收起，折叠状态在筛选后保留。
- **商品详情**：点击「查看详情」弹出详情面板（图片、参数表、简介）。
- **响应式**：手机与桌面自适应，手机端商品行自动改为两栏紧凑布局。
- **相对路径**：所有图片与脚本均使用相对路径，部署到仓库子路径（如
  `https://<user>.github.io/catalog-demo/`）后依然可以正常加载。

## 目录结构

```
catalog-demo/
├── index.html                 # 页面结构
├── assets/
│   ├── css/
│   │   └── style.css          # 全部样式（含移动端断点）
│   ├── js/
│   │   ├── data.js            # ★ 商品数据（日常只需要改这个文件）
│   │   └── app.js             # 分类 / 搜索 / 渲染逻辑
│   └── img/                   # 35 张原创商品插画（640×640 PNG）
└── tools/
    └── gen_images.py          # 商品图片生成脚本（Pillow，可重新生成）
```

## 修改商品数据

**只需要编辑 `assets/js/data.js`**，刷新页面即可生效，无需改动任何 HTML 或 CSS。

文件里有两段内容：

### 1. `categories` — 分类标签

```js
categories: [
  { id: 'all',     name: '全部' },
  { id: 'home',    name: '居家生活' },
  { id: 'outdoor', name: '户外随行' }
]
```

`id` 是唯一标识（`'all'` 代表全部），`name` 是标签上显示的文字。
新增分类时，只要给商品设置对应的 `cat` 值即可。

### 2. `products` — 商品列表

```js
{
  id:       'home-pillow',           // 唯一标识
  name:     '栖云棉麻抱枕套',         // 商品名称
  cat:      'home',                  // 对应 categories 里的 id
  price:    49.00,                   // 售价（元）
  origPrice: 69.00,                  // 划线原价，可写 null
  stock:    583,                     // 库存件数
  tag:      '推荐',                  // 角标：推荐 / 新品 / 热卖，可写 null
  img:      'assets/img/home-pillow.png', // 相对路径图片
  desc:     '一段商品简介……',         // 详情简介
  specs:    [['面料', '棉麻混纺'], ['尺寸', '45 × 45 cm']]  // 参数表
}
```

**增删商品的三个要点：**

1. `id` 不能重复。
2. `cat` 必须和 `categories` 中某个 `id` 对得上，否则该商品会显示在「未分类」里。
3. `img` 必须是**相对路径**（以 `assets/` 开头），不要写成 `/img/xxx.png` 这种绝对路径，
   否则部署到仓库子路径后图片会 404。新增图片请放进 `assets/img/` 目录。

### 3. 顶部公告

`site.notice` 是一个字符串数组，每一项渲染成公告框里的一行：

```js
site: {
  name: '青屿优选',
  slogan: '小而美的日常好物',
  notice: ['本站为静态演示站……', '服务时间：09:00 – 21:00']
}
```

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

## 重新生成商品图片

35 张商品插画由 `tools/gen_images.py` 用 Pillow 程序化绘制，风格统一、无版权风险：

```bash
python tools/gen_images.py
```

脚本会重新生成 `assets/img/` 下的全部 PNG（640×640）。

## 部署到 GitHub Pages

1. 在仓库根目录执行 `gh api repos/<owner>/<repo>/pages -X POST -f source[branch]=main -f source[path]=/`
   （或在仓库 **Settings → Pages** 里把 Source 选为 *Deploy from a branch*，分支 `main`、目录 `/ (root)`）。
2. 站点地址为 `https://<owner>.github.io/<repo>/`。

因为项目全部使用相对路径，部署到仓库子路径后无需任何额外配置即可正常显示。

## 技术说明

- 无框架、无依赖、无构建步骤，纯浏览器原生 API。
- 筛选逻辑集中在 `assets/js/app.js` 的 `filtered()` / `matches()` 两个函数里，改起来很直观。
- 使用 `<details>` / `<summary>` 实现分组折叠，天然支持键盘操作与无障碍语义。
- 商品行使用 CSS Grid 的具名区域（`grid-template-areas`）实现桌面 / 手机两套布局。
