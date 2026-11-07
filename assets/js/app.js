/* ==========================================================================
   青屿优选 — 目录交互脚本
   分类筛选与关键词搜索全部在浏览器内完成，不依赖任何后端或网络请求。
   商品数据来自同目录下的 data.js（window.CATALOG_DATA）。
   ========================================================================== */

(function () {
  'use strict';

  var data = window.CATALOG_DATA;
  if (!data || !Array.isArray(data.products)) {
    document.addEventListener('DOMContentLoaded', function () {
      var g = document.getElementById('groups');
      if (g) g.innerHTML = '<p style="padding:24px;color:#8a93a3">商品数据未加载，请检查 assets/js/data.js。</p>';
    });
    return;
  }

  var products = data.products;
  var categories = data.categories || [];
  var catMap = {};
  categories.forEach(function (c) { catMap[c.id] = c; });

  var state = { category: 'all', keyword: '' };
  var collapsed = {};   /* 记录被手动折叠的分组，重新渲染后保持状态 */
  var lastFocused = null;

  /* ---------------------------------------------------------------- 工具 */
  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function yuan(n) {
    var v = Number(n);
    return (isFinite(v) ? v : 0).toFixed(2);
  }

  function catName(id) {
    return catMap[id] ? catMap[id].name : '未分类';
  }

  function placeholderSrc() {
    var svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>" +
              "<rect width='64' height='64' fill='#eef2f8'/>" +
              "<text x='32' y='38' font-size='11' text-anchor='middle' " +
              "font-family='sans-serif' fill='#8a93a3'>暂无图</text></svg>";
    return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  }

  /* 给图片加一个加载失败兜底，避免缺图时版面塌陷 */
  function withFallback(img) {
    img.addEventListener('error', function handler() {
      img.removeEventListener('error', handler);
      img.src = placeholderSrc();
    });
    return img;
  }

  function makeImg(src, alt) {
    var img = new Image();
    img.src = src;
    img.alt = alt;
    img.loading = 'lazy';
    img.decoding = 'async';
    return withFallback(img);
  }

  /* ------------------------------------------------------------ 元素引用 */
  var el = {
    noticeList: document.getElementById('noticeList'),
    tabs: document.getElementById('tabs'),
    searchInput: document.getElementById('searchInput'),
    searchClear: document.getElementById('searchClear'),
    resultLine: document.getElementById('resultLine'),
    groups: document.getElementById('groups'),
    emptyState: document.getElementById('emptyState'),
    emptyTitle: document.getElementById('emptyTitle'),
    emptyDesc: document.getElementById('emptyDesc'),
    emptyReset: document.getElementById('emptyReset'),
    modal: document.getElementById('modal'),
    modalBody: document.getElementById('modalBody')
  };

  /* ------------------------------------------------------------ 公告渲染 */
  function renderNotice() {
    if (!el.noticeList || !data.site) return;
    var lines = data.site.notice || [];
    el.noticeList.innerHTML = lines.map(function (line) {
      return '<li>' + esc(line) + '</li>';
    }).join('');
  }

  /* ------------------------------------------------------------ 标签渲染 */
  function renderTabs() {
    if (!el.tabs) return;
    el.tabs.innerHTML = '';
    categories.forEach(function (cat) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'tab';
      btn.textContent = cat.name;
      btn.dataset.cat = cat.id;
      btn.setAttribute('role', 'tab');
      btn.setAttribute('aria-selected', cat.id === state.category ? 'true' : 'false');
      btn.addEventListener('click', function () {
        state.category = cat.id;
        render();
      });
      el.tabs.appendChild(btn);
    });
  }

  /* ------------------------------------------------------------ 搜索匹配 */
  function haystack(p) {
    return [
      p.name,
      catName(p.cat),
      p.desc || '',
      p.tag || '',
      (p.keywords || []).join(' ')
    ].join(' ').toLowerCase();
  }

  function matches(p, tokens) {
    if (!tokens.length) return true;
    var hay = haystack(p);
    for (var i = 0; i < tokens.length; i++) {
      if (hay.indexOf(tokens[i]) === -1) return false;
    }
    return true;
  }

  function tokens() {
    return state.keyword
      .toLowerCase()
      .split(/\s+/)
      .filter(function (t) { return t.length > 0; });
  }

  function filtered() {
    var tk = tokens();
    return products.filter(function (p) {
      if (state.category !== 'all' && p.cat !== state.category) return false;
      return matches(p, tk);
    });
  }

  /* ---------------------------------------------------------- 商品行渲染 */
  function tagClass(tag) {
    if (tag === '热卖') return 'chip chip-hot';
    if (tag === '新品') return 'chip chip-new';
    return 'chip chip-tag';
  }

  function productRow(p) {
    var row = document.createElement('article');
    row.className = 'product';
    row.dataset.id = p.id;

    var thumb = document.createElement('div');
    thumb.className = 'product-thumb';
    thumb.appendChild(makeImg(p.img, p.name));
    row.appendChild(thumb);

    var main = document.createElement('div');
    main.className = 'product-main';

    var name = document.createElement('h3');
    name.className = 'product-name';
    name.textContent = p.name;
    main.appendChild(name);

    // 简介：仅在桌面宽屏显示（CSS 控制），窄屏自动隐藏
    if (p.desc) {
      var desc = document.createElement('p');
      desc.className = 'product-desc';
      desc.textContent = p.desc;
      main.appendChild(desc);
    }

    var meta = document.createElement('div');
    meta.className = 'product-meta';
    meta.appendChild(chip('chip-cat', catName(p.cat)));
    if (p.tag) meta.appendChild(chip(tagClass(p.tag), p.tag));
    meta.appendChild(chip('chip-stock', '库存 ' + p.stock));
    main.appendChild(meta);

    row.appendChild(main);

    var price = document.createElement('div');
    price.className = 'product-price';
    price.innerHTML =
      '<div class="price-now"><span class="cur">¥</span>' + yuan(p.price) + '</div>' +
      (p.origPrice ? '<span class="price-old">¥' + yuan(p.origPrice) + '</span>' : '');
    row.appendChild(price);

    var action = document.createElement('div');
    action.className = 'product-action';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn-detail';
    btn.textContent = '查看详情';
    btn.addEventListener('click', function () { openDetail(p, btn); });
    action.appendChild(btn);
    row.appendChild(action);

    return row;
  }

  function chip(cls, text) {
    var s = document.createElement('span');
    s.className = cls;
    s.textContent = text;
    return s;
  }

  /* ---------------------------------------------------------- 分组渲染 */
  function groupList(list) {
    var buckets = [];
    var index = {};
    list.forEach(function (p) {
      if (!index.hasOwnProperty(p.cat)) {
        index[p.cat] = buckets.length;
        buckets.push({ id: p.cat, name: catName(p.cat), items: [] });
      }
      buckets[index[p.cat]].items.push(p);
    });

    var order = categories
      .filter(function (c) { return c.id !== 'all' && index.hasOwnProperty(c.id); })
      .map(function (c) { return c.id; });

    buckets.sort(function (a, b) {
      var ia = order.indexOf(a.id);
      var ib = order.indexOf(b.id);
      return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    });

    return buckets;
  }

  function renderGroups(list) {
    if (!el.groups) return;
    el.groups.innerHTML = '';

    groupList(list).forEach(function (grp) {
      var details = document.createElement('details');
      details.className = 'group';
      details.dataset.cat = grp.id;
      if (!collapsed[grp.id]) details.open = true;

      var summary = document.createElement('summary');
      summary.className = 'group-head';

      var title = document.createElement('span');
      title.className = 'group-title';
      title.textContent = grp.name;

      var count = document.createElement('span');
      count.className = 'group-count';
      count.textContent = grp.items.length + ' 件';

      var chevron = document.createElement('span');
      chevron.className = 'group-chevron';
      chevron.innerHTML = '<svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true">' +
        '<path d="m5 8 5 5 5-5" fill="none" stroke="currentColor" stroke-width="2" ' +
        'stroke-linecap="round" stroke-linejoin="round"/></svg>';

      summary.appendChild(title);
      summary.appendChild(count);
      summary.appendChild(chevron);
      details.appendChild(summary);

      var body = document.createElement('div');
      body.className = 'group-body';
      grp.items.forEach(function (p) { body.appendChild(productRow(p)); });
      details.appendChild(body);

      details.addEventListener('toggle', function () {
        collapsed[grp.id] = !details.open;
      });

      el.groups.appendChild(details);
    });
  }

  /* ------------------------------------------------------------ 结果统计 */
  function renderResultLine(list) {
    if (!el.resultLine) return;
    var total = list.length;
    var scope = state.category === 'all' ? '全部分类' : catName(state.category);
    var kw = state.keyword;

    if (kw) {
      el.resultLine.innerHTML =
        '在 <strong>' + esc(scope) + '</strong> 中找到 <strong>' + total + '</strong> 件与「' +
        esc(kw) + '」相关的商品';
    } else {
      el.resultLine.innerHTML =
        '<strong>' + esc(scope) + '</strong> · 共 <strong>' + total + '</strong> 件商品';
    }
  }

  /* ------------------------------------------------------------ 空状态 */
  function renderEmpty(list) {
    var empty = list.length === 0;
    if (!el.emptyState) return;
    el.emptyState.hidden = !empty;
    if (!empty) return;

    var kw = state.keyword;
    if (kw && state.category !== 'all') {
      el.emptyTitle.textContent = '「' + catName(state.category) + '」里没有找到「' + kw + '」';
      el.emptyDesc.textContent = '换个关键词，或切到「全部」分类再搜一次。';
    } else if (kw) {
      el.emptyTitle.textContent = '没有找到「' + kw + '」相关的商品';
      el.emptyDesc.textContent = '试试更短的关键词，例如「保温」「帆布」「陶瓷」。';
    } else {
      el.emptyTitle.textContent = '该分类暂时没有商品';
      el.emptyDesc.textContent = '切到「全部」分类浏览其他商品。';
    }
  }

  /* ------------------------------------------------------------ 主渲染 */
  function render() {
    var list = filtered();
    renderTabs();
    renderResultLine(list);
    renderGroups(list);
    renderEmpty(list);
    if (el.searchClear) el.searchClear.hidden = !state.keyword;
  }

  /* ------------------------------------------------------------ 详情弹层 */
  function openDetail(p, trigger) {
    if (!el.modal || !el.modalBody) return;
    lastFocused = trigger || document.activeElement;

    var html = '';
    html += '<div class="detail-top">';
    html += '<div class="detail-img" id="detailImg"></div>';
    html += '<div class="detail-info">';
    html += '<h2 class="detail-name" id="modalTitle">' + esc(p.name) + '</h2>';
    html += '<div class="detail-price"><span class="cur">¥</span>' + yuan(p.price);
    if (p.origPrice) html += '<span class="price-old">¥' + yuan(p.origPrice) + '</span>';
    html += '</div>';
    html += '<div class="product-meta">';
    html += '<span class="chip chip-cat">' + esc(catName(p.cat)) + '</span>';
    if (p.tag) html += '<span class="' + tagClass(p.tag) + '">' + esc(p.tag) + '</span>';
    html += '<span class="chip chip-stock">库存 ' + esc(p.stock) + '</span>';
    html += '</div>';
    html += '</div></div>';

    html += '<p class="detail-desc">' + esc(p.desc || '') + '</p>';

    if (p.specs && p.specs.length) {
      html += '<table class="spec-table"><tbody>';
      p.specs.forEach(function (pair) {
        html += '<tr><th scope="row">' + esc(pair[0]) + '</th><td>' + esc(pair[1]) + '</td></tr>';
      });
      html += '</tbody></table>';
    }

    html += '<p class="detail-foot">本页面为静态演示，不提供购买、支付或配送服务。' +
            '如需修改该商品，请编辑 <code>assets/js/data.js</code>。</p>';

    el.modalBody.innerHTML = html;
    el.modalBody.querySelector('#detailImg').appendChild(makeImg(p.img, p.name));

    el.modal.hidden = false;
    document.body.style.overflow = 'hidden';

    var closeBtn = el.modal.querySelector('.modal-close');
    if (closeBtn) closeBtn.focus();
  }

  function closeDetail() {
    if (!el.modal || el.modal.hidden) return;
    el.modal.hidden = true;
    el.modalBody.innerHTML = '';
    document.body.style.overflow = '';
    if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
    lastFocused = null;
  }

  /* ------------------------------------------------------------ 事件绑定 */
  function bind() {
    if (el.searchInput) {
      el.searchInput.addEventListener('input', function () {
        state.keyword = el.searchInput.value.trim();
        render();
      });
      el.searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && el.searchInput.value) {
          el.searchInput.value = '';
          state.keyword = '';
          render();
        }
      });
    }

    if (el.searchClear) {
      el.searchClear.addEventListener('click', function () {
        el.searchInput.value = '';
        state.keyword = '';
        render();
        el.searchInput.focus();
      });
    }

    if (el.emptyReset) {
      el.emptyReset.addEventListener('click', function () {
        state.category = 'all';
        state.keyword = '';
        if (el.searchInput) el.searchInput.value = '';
        render();
      });
    }

    if (el.modal) {
      el.modal.addEventListener('click', function (e) {
        if (e.target.hasAttribute('data-close')) closeDetail();
      });
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && el.modal && !el.modal.hidden) closeDetail();
    });
  }

  /* ------------------------------------------------------------ 启动 */
  renderNotice();
  bind();
  render();
})();
