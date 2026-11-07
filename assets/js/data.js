/* ==========================================================================
   Runaway — 站点数据（由 tools/sync_data.py 从 Runaway.xlsx 自动生成）
   --------------------------------------------------------------------------
   想改商品或公告，优先改 Excel（Runaway.xlsx）后运行：
       python tools/sync_data.py
   本文件由脚本覆盖生成，直接手改会在下次同步时丢失。
   ========================================================================== */

window.CATALOG_DATA = {
  site: {
    name: "Runaway",
    slogan: "账号与礼品卡目录",
    noticeTitle: "本站商品没有实际购买功能，如需购买请联系下方联系方式",
    notice: [
      "联系QQ：616007226",
      "联系微信：AbyssalEcho",
    ]
  },

  categories: [
    { id: "all", name: "全部" },
    { id: "twitter", name: "推特账号" },
    { id: "apple", name: "苹果账号" },
    { id: "google", name: "谷歌账号" },
    { id: "gpt", name: "GPT系列" },
    { id: "itunes-giftcard", name: "苹果礼品卡（可充值GPT）" },
  ],

  products: [
    {
      id: "twitter-01",
      name: "推特账号〖2009-2025/邮箱/2fa〗",
      cat: "twitter",
      price: 15,
      origPrice: null,
      stock: 178,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/twitter.svg",
      desc: "推特账号 · 库存 178 · 有货",
      specs: [
        ["分类", "推特账号"],
        ["售价（元）", "15.00"],
        ["库存", "178"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "twitter-02",
      name: "推特账号〖2006-2025注册/token/2FA/hotmail邮箱/带30-100粉丝〗",
      cat: "twitter",
      price: 30,
      origPrice: null,
      stock: 174,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/twitter.svg",
      desc: "推特账号 · 库存 174 · 有货",
      specs: [
        ["分类", "推特账号"],
        ["售价（元）", "30.00"],
        ["库存", "174"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "apple-01",
      name: "〖香港ID〗〖无密保/API/可下APP〗",
      cat: "apple",
      price: 15,
      origPrice: null,
      stock: 200,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/apple.svg",
      desc: "苹果账号 · 库存 200 · 有货",
      specs: [
        ["分类", "苹果账号"],
        ["售价（元）", "15.00"],
        ["库存", "200"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "apple-02",
      name: "〖日本ID〗〖无密保/API/可下APP〗",
      cat: "apple",
      price: 15,
      origPrice: null,
      stock: 200,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/apple.svg",
      desc: "苹果账号 · 库存 200 · 有货",
      specs: [
        ["分类", "苹果账号"],
        ["售价（元）", "15.00"],
        ["库存", "200"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "apple-03",
      name: "〖美区ID〗〖无密保/API/可下APP〗",
      cat: "apple",
      price: 15,
      origPrice: null,
      stock: 207,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/apple.svg",
      desc: "苹果账号 · 库存 207 · 有货",
      specs: [
        ["分类", "苹果账号"],
        ["售价（元）", "15.00"],
        ["库存", "207"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "apple-04",
      name: "〖美区ID〗〖半年/带密保/没开IC/带火煎〗",
      cat: "apple",
      price: 35,
      origPrice: null,
      stock: 293,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/apple.svg",
      desc: "苹果账号 · 库存 293 · 有货",
      specs: [
        ["分类", "苹果账号"],
        ["售价（元）", "35.00"],
        ["库存", "293"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "google-01",
      name: "〖Google〗7天以上新号/随机IP/👍推荐",
      cat: "google",
      price: 15,
      origPrice: null,
      stock: 1129,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/google.svg",
      desc: "谷歌账号 · 库存 1129 · 有货",
      specs: [
        ["分类", "谷歌账号"],
        ["售价（元）", "15.00"],
        ["库存", "1129"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "google-02",
      name: "〖Google〗2FA/随机IP/登gmail无需短信👍推荐",
      cat: "google",
      price: 30,
      origPrice: null,
      stock: 562,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/google.svg",
      desc: "谷歌账号 · 库存 562 · 有货",
      specs: [
        ["分类", "谷歌账号"],
        ["售价（元）", "30.00"],
        ["库存", "562"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "gpt-01",
      name: "GPT Plus 1个月",
      cat: "gpt",
      price: 150,
      origPrice: null,
      stock: 138,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/gpt.svg",
      desc: "GPT系列 · 库存 138 · 有货",
      specs: [
        ["分类", "GPT系列"],
        ["售价（元）", "150.00"],
        ["库存", "138"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "gpt-02",
      name: "GPT Pro 1个月",
      cat: "gpt",
      price: 750,
      origPrice: null,
      stock: 89,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/gpt.svg",
      desc: "GPT系列 · 库存 89 · 有货",
      specs: [
        ["分类", "GPT系列"],
        ["售价（元）", "750.00"],
        ["库存", "89"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "gpt-03",
      name: "GPT Pro200X 1个月",
      cat: "gpt",
      price: 1250,
      origPrice: null,
      stock: 545,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/gpt.svg",
      desc: "GPT系列 · 库存 545 · 有货",
      specs: [
        ["分类", "GPT系列"],
        ["售价（元）", "1250.00"],
        ["库存", "545"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "gpt-04",
      name: "GPT Go 1个月",
      cat: "gpt",
      price: 60,
      origPrice: null,
      stock: 1614,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/gpt.svg",
      desc: "GPT系列 · 库存 1614 · 有货",
      specs: [
        ["分类", "GPT系列"],
        ["售价（元）", "60.00"],
        ["库存", "1614"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "gpt-05",
      name: "Codex接码",
      cat: "gpt",
      price: 15,
      origPrice: null,
      stock: 1614,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/gpt.svg",
      desc: "GPT系列 · 库存 1614 · 有货",
      specs: [
        ["分类", "GPT系列"],
        ["售价（元）", "15.00"],
        ["库存", "1614"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "itunes-giftcard-01",
      name: "iTunes 礼品卡 20 美金 (美国)",
      cat: "itunes-giftcard",
      price: 170,
      origPrice: null,
      stock: 200,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/itunes-giftcard.svg",
      desc: "苹果礼品卡（可充值GPT） · 库存 200 · 有货",
      specs: [
        ["分类", "苹果礼品卡（可充值GPT）"],
        ["售价（元）", "170.00"],
        ["库存", "200"],
        ["库存状态", "有货"],
      ]
    },
    {
      id: "itunes-giftcard-02",
      name: "iTunes 礼品卡 25 CAD (加拿大)",
      cat: "itunes-giftcard",
      price: 160,
      origPrice: null,
      stock: 200,
      stockStatus: "有货",
      tag: null,
      img: "assets/img/itunes-giftcard.svg",
      desc: "苹果礼品卡（可充值GPT） · 库存 200 · 有货",
      specs: [
        ["分类", "苹果礼品卡（可充值GPT）"],
        ["售价（元）", "160.00"],
        ["库存", "200"],
        ["库存状态", "有货"],
      ]
    },
  ]
};
