/* ==========================================================================
   青屿优选 — 商品数据文件（集中维护入口）
   --------------------------------------------------------------------------
   想增删商品 / 修改价格 / 调整分类，只需要改这个文件，刷新页面即可生效。
   结构说明：
     categories  分类标签（tabs），id 为唯一标识，'all' 代表全部
     products    商品列表，cat 字段对应 categories 里的 id
                 price      售价（元）
                 origPrice  划线原价（可选，没有就写 null）
                 stock      库存件数
                 tag        角标文字（可选，如「推荐」「新品」「热卖」）
                 img        相对路径图片，务必保持在 assets/img/ 下
                 desc       商品简介
                 specs      参数列表 [[参数名, 参数值], ...]
   ========================================================================== */

window.CATALOG_DATA = {
  site: {
    name: '青屿优选',
    slogan: '小而美的日常好物',
    notice: [
      '本站为「青屿优选」静态演示站，页面内的商品、价格与库存均为虚构演示数据，不提供真实的购买、支付、物流或售后服务。',
      '筛选方式：点击上方分类标签可切换类目，在搜索框输入关键词可在当前类目中即时匹配，无需刷新页面。',
      '服务时间：09:00 – 21:00（示例）',
      '演示邮箱：hello@qingyu.example',
      '温馨提示：所有商品图片均为原创插画，仅用于演示排版效果。'
    ]
  },

  categories: [
    { id: 'all', name: '全部' },
    { id: 'home', name: '居家生活' },
    { id: 'outdoor', name: '户外随行' },
    { id: 'digital', name: '数码配件' },
    { id: 'kitchen', name: '厨房料理' },
    { id: 'office', name: '办公文具' },
    { id: 'apparel', name: '服饰配件' },
    { id: 'beauty', name: '美妆个护' }
  ],

  products: [
    /* ----------------------------- 居家生活 ----------------------------- */
    {
      id: 'home-pillow',
      name: '栖云棉麻抱枕套',
      cat: 'home',
      price: 49.00,
      origPrice: 69.00,
      stock: 583,
      tag: '推荐',
      img: 'assets/img/home-pillow.png',
      desc: '选用 100% 水洗棉麻混纺面料，触感柔软透气，四边隐形拉链设计，可整体拆洗。',
      specs: [['面料', '棉麻混纺'], ['尺寸', '45 × 45 cm'], ['工艺', '隐形拉链 / 可拆洗'], ['洗涤', '机洗 30℃ 以下']]
    },
    {
      id: 'home-candle',
      name: '晨雾香薰蜡烛',
      cat: 'home',
      price: 39.00,
      origPrice: null,
      stock: 214,
      tag: null,
      img: 'assets/img/home-candle.png',
      desc: '白茶与雪松调，燃烧时长约 25 小时，玻璃杯身可回收作为收纳罐使用。',
      specs: [['香型', '白茶雪松'], ['净含量', '180 g'], ['燃烧时长', '约 25 小时'], ['容器', '可回收玻璃']]
    },
    {
      id: 'home-mug',
      name: '素白陶瓷马克杯',
      cat: 'home',
      price: 29.90,
      origPrice: null,
      stock: 742,
      tag: null,
      img: 'assets/img/home-mug.png',
      desc: '高温釉面陶瓷烧制，杯口圆润不割唇，可用于微波炉与洗碗机清洗。',
      specs: [['材质', '高温釉面陶瓷'], ['容量', '400 ml'], ['是否可微波', '支持'], ['产地', '景德镇']]
    },
    {
      id: 'home-shelf',
      name: '折叠竹木置物架',
      cat: 'home',
      price: 89.00,
      origPrice: null,
      stock: 128,
      tag: null,
      img: 'assets/img/home-shelf.png',
      desc: '多层实木夹板与竹制层板，免安装折叠结构，展开后稳固承重，适合厨房与阳台。',
      specs: [['层数', '三层'], ['尺寸', '38 × 24 × 60 cm'], ['安装', '免安装折叠'], ['单层承重', '8 kg']]
    },
    {
      id: 'home-clock',
      name: '静音机械挂钟',
      cat: 'home',
      price: 69.00,
      origPrice: null,
      stock: 96,
      tag: null,
      img: 'assets/img/home-clock.png',
      desc: '石英机芯搭配静音扫秒设计，圆形表盘简洁耐看，附挂钉与备用电池。',
      specs: [['机芯', '石英 / 静音扫秒'], ['直径', '30 cm'], ['供电', 'AA 电池 × 1'], ['附件', '挂钉 / 备用电池']]
    },

    /* ----------------------------- 户外随行 ----------------------------- */
    {
      id: 'outdoor-backpack',
      name: '轻旅防泼水双肩包',
      cat: 'outdoor',
      price: 199.00,
      origPrice: 259.00,
      stock: 205,
      tag: '热卖',
      img: 'assets/img/outdoor-backpack.png',
      desc: '18L 轻量容量，主体面料经过防泼水处理，前置快取口袋，适合通勤与短途旅行。',
      specs: [['容量', '18 L'], ['面料', '210D 防泼水尼龙'], ['重量', '0.52 kg'], ['背负', '透气网面 + 可调肩带']]
    },
    {
      id: 'outdoor-bottle',
      name: '山野钛合金保温壶',
      cat: 'outdoor',
      price: 129.00,
      origPrice: null,
      stock: 316,
      tag: '推荐',
      img: 'assets/img/outdoor-bottle.png',
      desc: '双层真空钛合金内胆，保温 12 小时、保冷 24 小时，壶口可单手开合。',
      specs: [['容量', '500 ml'], ['材质', '钛合金 / 316 不锈钢'], ['保温', '约 12 小时'], ['保冷', '约 24 小时']]
    },
    {
      id: 'outdoor-chair',
      name: '露营折叠月亮椅',
      cat: 'outdoor',
      price: 259.00,
      origPrice: null,
      stock: 87,
      tag: null,
      img: 'assets/img/outdoor-chair.png',
      desc: '航空级铝合金骨架配高弹牛津布，收起后可放入背包侧袋，单手即可展开。',
      specs: [['承重', '120 kg'], ['收纳尺寸', '36 × 12 × 10 cm'], ['净重', '1.9 kg'], ['面料', '600D 高强牛津布']]
    },
    {
      id: 'outdoor-umbrella',
      name: '晴空防紫外线折叠伞',
      cat: 'outdoor',
      price: 79.00,
      origPrice: 99.00,
      stock: 1042,
      tag: null,
      img: 'assets/img/outdoor-umbrella.png',
      desc: 'UPF50+ 防晒涂层，三折结构收起后仅 24 cm，伞骨经抗风测试。',
      specs: [['防晒', 'UPF 50+'], ['直径', '98 cm'], ['折叠', '三折'], ['伞骨', '玻纤 + 合金']]
    },
    {
      id: 'outdoor-cutlery',
      name: '溪谷户外便携餐具',
      cat: 'outdoor',
      price: 45.00,
      origPrice: null,
      stock: 388,
      tag: null,
      img: 'assets/img/outdoor-cutlery.png',
      desc: '食品级钛合金一体成型，叉、勺、刀三件组合，自带收纳袋可卷曲固定。',
      specs: [['材质', '纯钛'], ['组合', '叉 / 勺 / 刀'], ['净重', '78 g'], ['收纳', '附赠布袋']]
    },

    /* ----------------------------- 数码配件 ----------------------------- */
    {
      id: 'digital-charger',
      name: '磁吸桌面无线充',
      cat: 'digital',
      price: 59.00,
      origPrice: null,
      stock: 654,
      tag: null,
      img: 'assets/img/digital-charger.png',
      desc: '磁吸对位自动吸附，15W 最高功率，铝合金外壳内置散热片，长时间充电不烫手。',
      specs: [['最大功率', '15 W'], ['材质', '铝合金'], ['接口', 'USB-C'], ['线长', '1.2 m 编织线']]
    },
    {
      id: 'digital-stand',
      name: '磨砂铝合金笔电支架',
      cat: 'digital',
      price: 119.00,
      origPrice: null,
      stock: 231,
      tag: '新品',
      img: 'assets/img/digital-stand.png',
      desc: '一体式折叠结构，硅胶防滑垫保护机身，六档高度可调，适合 11–17 英寸笔电。',
      specs: [['适配', '11 – 17 英寸'], ['高度', '六档可调'], ['材质', '阳极氧化铝'], ['重量', '0.62 kg']]
    },
    {
      id: 'digital-cable',
      name: '编织快充数据线 2 米',
      cat: 'digital',
      price: 25.90,
      origPrice: null,
      stock: 1877,
      tag: null,
      img: 'assets/img/digital-cable.png',
      desc: '尼龙编织外皮耐弯折不易断，支持 60W 快充，铝合金端子外壳。',
      specs: [['长度', '2 m'], ['最大功率', '60 W'], ['线材', '尼龙编织'], ['接头', 'USB-C to C']]
    },
    {
      id: 'digital-mouse',
      name: '静音蓝牙鼠标',
      cat: 'digital',
      price: 89.00,
      origPrice: null,
      stock: 468,
      tag: null,
      img: 'assets/img/digital-mouse.png',
      desc: '双模连接兼顾电脑与平板，按键按压噪音低于 30 分贝，一节电池续航约 12 个月。',
      specs: [['连接', '蓝牙 5.1 / 2.4G'], ['按键', '静音微动'], ['续航', '约 12 个月'], ['兼容', 'Windows / macOS / 平板']]
    },
    {
      id: 'digital-powerbank',
      name: '旅行收纳充电宝 10000mAh',
      cat: 'digital',
      price: 149.00,
      origPrice: 179.00,
      stock: 529,
      tag: null,
      img: 'assets/img/digital-powerbank.png',
      desc: '自带提环与折叠插头，收纳时不刮蹭其他物品，支持双向快充与过流保护。',
      specs: [['容量', '10000 mAh'], ['输出', '22.5 W 双向快充'], ['接口', 'USB-C × 1 / USB-A × 1'], ['认证', '航空运输标准']]
    },

    /* ----------------------------- 厨房料理 ----------------------------- */
    {
      id: 'kitchen-pot',
      name: '珐琅铸铁奶锅 18cm',
      cat: 'kitchen',
      price: 268.00,
      origPrice: null,
      stock: 76,
      tag: '推荐',
      img: 'assets/img/kitchen-pot.png',
      desc: '厚重铸铁锅体蓄热均匀，内外珐琅涂层不粘易清洁，燃气与电磁炉均适用。',
      specs: [['口径', '18 cm'], ['材质', '珐琅铸铁'], ['适用炉具', '燃气 / 电磁 / 烤箱'], ['净重', '2.4 kg']]
    },
    {
      id: 'kitchen-pour',
      name: '手作粗陶手冲咖啡壶',
      cat: 'kitchen',
      price: 158.00,
      origPrice: null,
      stock: 43,
      tag: null,
      img: 'assets/img/kitchen-pour.png',
      desc: '鹅颈细口出水可控，粗陶材质保留咖啡风味，每只壶身釉色略有差异。',
      specs: [['容量', '600 ml'], ['材质', '粗陶'], ['出水口', '鹅颈细口'], ['附件', '滤杯 / 滤纸']]
    },
    {
      id: 'kitchen-scissors',
      name: '家用不锈钢厨房剪',
      cat: 'kitchen',
      price: 35.90,
      origPrice: null,
      stock: 512,
      tag: null,
      img: 'assets/img/kitchen-scissors.png',
      desc: '一体锻造刀刃锋利耐用，配可拆洗的防滑手柄，剪骨剪肉两相宜。',
      specs: [['刃长', '95 mm'], ['材质', '3Cr13 不锈钢'], ['手柄', '可拆洗防滑'], ['适用', '厨房 / 剪骨']]
    },
    {
      id: 'kitchen-colander',
      name: '硅胶折叠沥水篮',
      cat: 'kitchen',
      price: 26.80,
      origPrice: null,
      stock: 903,
      tag: null,
      img: 'assets/img/kitchen-colander.png',
      desc: '食品级硅胶材质，可折叠收纳节省空间，侧边小孔便于沥干蔬果水分。',
      specs: [['尺寸', '展开 26 cm'], ['材质', '食品级硅胶'], ['耐温', '-40℃ ~ 220℃'], ['折叠', '可折叠']]
    },
    {
      id: 'kitchen-jars',
      name: '陶瓷调味罐三件套',
      cat: 'kitchen',
      price: 69.00,
      origPrice: null,
      stock: 188,
      tag: null,
      img: 'assets/img/kitchen-jars.png',
      desc: '高白泥陶瓷罐身配竹木旋盖，密封性好，适合存放盐、糖与各类调味料。',
      specs: [['规格', '3 件套'], ['容量', '120 / 180 / 240 ml'], ['材质', '高白泥陶瓷 + 竹木盖'], ['密封', '硅胶圈密封']]
    },

    /* ----------------------------- 办公文具 ----------------------------- */
    {
      id: 'office-clock',
      name: '桌面静音翻页钟',
      cat: 'office',
      price: 99.00,
      origPrice: null,
      stock: 165,
      tag: '新品',
      img: 'assets/img/office-clock.png',
      desc: '大字号翻页数字翻动噪音低，日期星期同步显示，夜间背光可调。',
      specs: [['显示', '日期 / 星期 / 时间'], ['背光', '夜间柔光可调'], ['尺寸', '12 × 6 × 8 cm'], ['供电', 'USB-C 充电']]
    },
    {
      id: 'office-pouch',
      name: '植鞣皮革笔袋',
      cat: 'office',
      price: 45.00,
      origPrice: null,
      stock: 297,
      tag: null,
      img: 'assets/img/office-pouch.png',
      desc: '意大利植鞣革皮随使用逐渐形成自然包浆，双层分区可分类收纳文具。',
      specs: [['材质', '植鞣牛皮'], ['尺寸', '20 × 6 × 4 cm'], ['内部', '双层分区'], ['五金', '黄铜拉链']]
    },
    {
      id: 'office-notebook',
      name: 'A5 方格软面笔记本',
      cat: 'office',
      price: 22.00,
      origPrice: null,
      stock: 1240,
      tag: null,
      img: 'assets/img/office-notebook.png',
      desc: '100g 米白道林纸书写顺滑不洇墨，5mm 方格内页，装订可 180° 平摊。',
      specs: [['规格', 'A5 / 5mm 方格'], ['页数', '120 页'], ['纸张', '100g 米白道林'], ['装订', '胶装可平摊']]
    },
    {
      id: 'office-sticky',
      name: '磁吸白板便签套装',
      cat: 'office',
      price: 18.90,
      origPrice: null,
      stock: 645,
      tag: null,
      img: 'assets/img/office-sticky.png',
      desc: '含磁吸白板贴片与 4 色便签本，配合桌面小夹板整理灵感与待办。',
      specs: [['组合', '白板贴 × 1 / 便签 × 4'], ['便签尺寸', '76 × 76 mm'], ['数量', '便签 4 × 50 张'], ['特点', '可反复擦写']]
    },
    {
      id: 'office-stapler',
      name: '铝合金便携订书机',
      cat: 'office',
      price: 39.00,
      origPrice: null,
      stock: 358,
      tag: null,
      img: 'assets/img/office-stapler.png',
      desc: '一体压铸铝合金机身，底部可回收余钉，收纳小巧适合随身携带。',
      specs: [['装钉量', '50 枚'], ['适用订钉', '24/6 mm'], ['材质', '铝合金'], ['特点', '底部余钉回收']]
    },

    /* ----------------------------- 服饰配件 ----------------------------- */
    {
      id: 'apparel-cap',
      name: '轻氧棉质棒球帽',
      cat: 'apparel',
      price: 59.00,
      origPrice: null,
      stock: 421,
      tag: null,
      img: 'assets/img/apparel-cap.png',
      desc: '水洗纯棉帽身柔软透气，可调节后扣头围，帽檐定型不塌。',
      specs: [['材质', '100% 水洗棉'], ['帽围', '54 – 60 cm 可调'], ['工艺', '水洗定型'], ['洗护', '手洗 / 轻柔机洗']]
    },
    {
      id: 'apparel-tote',
      name: '简约帆布托特包',
      cat: 'apparel',
      price: 79.00,
      origPrice: 99.00,
      stock: 508,
      tag: '热卖',
      img: 'assets/img/apparel-tote.png',
      desc: '12oz 加厚水洗帆布，内衬一层薄棉布，肩带加宽设计久背不勒肩。',
      specs: [['材质', '12oz 水洗帆布'], ['尺寸', '38 × 40 × 12 cm'], ['内衬', '薄棉布'], ['承重', '约 8 kg']]
    },
    {
      id: 'apparel-watch',
      name: '极简钛合金腕表',
      cat: 'apparel',
      price: 399.00,
      origPrice: null,
      stock: 62,
      tag: null,
      img: 'assets/img/apparel-watch.png',
      desc: '钛合金表壳轻盈耐汗敏，表带可调节刻度，配合简约读时界面。',
      specs: [['表壳', '钛合金'], ['表带', '可调节硅胶 / 织带'], ['防水', '5 ATM'], ['续航', '约 30 天']]
    },
    {
      id: 'apparel-socks',
      name: '精梳棉商务短袜 3 双装',
      cat: 'apparel',
      price: 39.00,
      origPrice: null,
      stock: 806,
      tag: null,
      img: 'assets/img/apparel-socks.png',
      desc: '精梳棉混纺纱线，袜口罗纹弹力贴合，商务深色系适合搭配西裤。',
      specs: [['规格', '3 双装'], ['材质', '精梳棉混纺'], ['尺码', '22 – 26 cm'], ['颜色', '深灰 / 黑 / 藏青']]
    },
    {
      id: 'apparel-scarf',
      name: '羊毛混纺长围巾',
      cat: 'apparel',
      price: 159.00,
      origPrice: null,
      stock: 134,
      tag: null,
      img: 'assets/img/apparel-scarf.png',
      desc: '羊毛混纺纱线编织，两面异色设计，边缘流苏收口整齐不脱线。',
      specs: [['材质', '羊毛混纺'], ['尺寸', '180 × 30 cm'], ['工艺', '双面提花'], ['洗护', '专业干洗']]
    },

    /* ----------------------------- 美妆个护 ----------------------------- */
    {
      id: 'beauty-cleanser',
      name: '氨基酸温和洁面乳',
      cat: 'beauty',
      price: 55.00,
      origPrice: null,
      stock: 733,
      tag: null,
      img: 'assets/img/beauty-cleanser.png',
      desc: '氨基酸表活体系，绵密泡沫带走多余油脂，洗后不紧绷。',
      specs: [['净含量', '120 g'], ['类型', '氨基酸洁面'], ['适用', '所有肤质'], ['备案', '演示备案号']]
    },
    {
      id: 'beauty-mask',
      name: '玻尿酸补水面膜 10 片装',
      cat: 'beauty',
      price: 79.00,
      origPrice: 99.00,
      stock: 456,
      tag: '热卖',
      img: 'assets/img/beauty-mask.png',
      desc: '三层复合膜布贴合面部轮廓，精华液充足，敷后肌肤清爽不粘腻。',
      specs: [['规格', '10 片 / 盒'], ['膜布', '天丝纤维'], ['核心成分', '玻尿酸'], ['适用', '任何肤质']]
    },
    {
      id: 'beauty-handcream',
      name: '天然植萃护手霜',
      cat: 'beauty',
      price: 32.00,
      origPrice: null,
      stock: 622,
      tag: null,
      img: 'assets/img/beauty-handcream.png',
      desc: '添加乳木果油与甜杏仁油，质地轻盈好推开，吸收后不留油膜。',
      specs: [['净含量', '60 ml'], ['核心成分', '乳木果油 / 甜杏仁油'], ['质地', '轻盈乳液'], ['包装', '铝管装']]
    },
    {
      id: 'beauty-toothbrush',
      name: '便携电动声波牙刷',
      cat: 'beauty',
      price: 219.00,
      origPrice: null,
      stock: 148,
      tag: '新品',
      img: 'assets/img/beauty-toothbrush.png',
      desc: '每分钟 38000 次声波震动，三档力度可调，旅行锁防止误触，续航约 30 天。',
      specs: [['震动频率', '38000 次 / 分钟'], ['档位', '三档'], ['续航', '约 30 天'], ['防水', 'IPX7']]
    },
    {
      id: 'beauty-towel',
      name: '竹纤维毛巾两条装',
      cat: 'beauty',
      price: 49.90,
      origPrice: null,
      stock: 377,
      tag: null,
      img: 'assets/img/beauty-towel.png',
      desc: '竹纤维纱线柔软吸水快，边缘包边缝制不易散边，两条装可分面使用。',
      specs: [['规格', '两条装'], ['尺寸', '34 × 80 cm'], ['材质', '竹纤维'], ['工艺', '双层包边']]
    }
  ]
};
