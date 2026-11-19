/* Buildless, dependency-free policy case component. Works over file://. */
(() => {
  'use strict';
  function mount(root, options = {}) {
  if (!root) return null;
  if (root._policyCaseController) return root._policyCaseController;
  const listeners = [];
  const on = (node, event, handler) => { node.addEventListener(event, handler); listeners.push(() => node.removeEventListener(event, handler)); };
  if (options.assetBase) {
    const base = new URL(options.assetBase.endsWith('/') ? options.assetBase : options.assetBase + '/', document.baseURI);
    root.querySelectorAll('[src],[href],[data-zoom]').forEach(node => {
      ['src','href','data-zoom'].forEach(attr => {
        const value = node.getAttribute(attr);
        if (value && /^(assets|data)\//.test(value)) node.setAttribute(attr, new URL(value, base).href);
      });
    });
  }
  root.dataset.initialized = 'true';
  const tabs = [...root.querySelectorAll('[data-case]')];
  const panels = {innovation: root.querySelector('#pc-innovation'), economy: root.querySelector('#pc-economy')};
  function selectCase(name, focus = false) {
    if (!panels[name]) return;
    tabs.forEach(tab => {
      const active = tab.dataset.case === name;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
    Object.entries(panels).forEach(([key, panel]) => { panel.hidden = key !== name; });
    root.dispatchEvent(new CustomEvent('policycase:change', {bubbles: true, detail: {caseId: name}}));
  }
  tabs.forEach((tab, i) => {
    on(tab, 'click', () => selectCase(tab.dataset.case));
    on(tab, 'keydown', event => {
      let target;
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') target = (i + 1) % tabs.length;
      if (event.key === 'Home') target = 0;
      if (event.key === 'End') target = tabs.length - 1;
      if (target !== undefined) {event.preventDefault(); selectCase(tabs[target].dataset.case, true);}
    });
  });
  root.querySelectorAll('[data-open-case]').forEach(button => on(button, 'click', () => {
    selectCase(button.dataset.openCase, true);
    root.querySelector('.pc-case-tabs').scrollIntoView({block:'start',behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
  }));
  const numbers = n => new Intl.NumberFormat('zh-CN').format(n);
  const percent = n => (n * 100).toFixed(2) + '%';
  const safe = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const galleryTabs = [...root.querySelectorAll('[data-gallery]')];
  function selectGallery(name, focus = false) {
    galleryTabs.forEach(tab => {
      const active = tab.dataset.gallery === name;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      root.querySelector('#' + tab.getAttribute('aria-controls')).hidden = !active;
      if (active && focus) tab.focus();
    });
  }
  galleryTabs.forEach((tab, index) => {
    on(tab, 'click', () => selectGallery(tab.dataset.gallery));
    on(tab, 'keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % galleryTabs.length;
      if (event.key === 'ArrowLeft') next = (index - 1 + galleryTabs.length) % galleryTabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = galleryTabs.length - 1;
      if (next !== undefined) { event.preventDefault(); selectGallery(galleryTabs[next].dataset.gallery, true); }
    });
  });
  const regional = (options.data || window.PolicyCaseData)?.regional;
  if (regional?.regions?.length) {
    root.querySelector('#pc-region-rows').innerHTML = regional.regions.map(row => `<tr><th scope="row">${safe(row.region)}</th><td>${numbers(row.sampleCityCount)} 城</td><td><b>${numbers(row.citiesWithPolicy2025)} 城</b><small>${percent(row.citiesWithPolicy2025Share)}</small></td><td><b>${numbers(row.policyCumulative2025)} 篇</b><small>${percent(row.policyCumulative2025Share)}</small><span class="pc-table-share" aria-hidden="true"><i style="width:${row.policyCumulative2025Share * 100}%"></i></span></td><td><b>${numbers(row.patents2025)} 件</b><small>${percent(row.patents2025Share)}</small><span class="pc-table-share pc-table-share-blue" aria-hidden="true"><i style="width:${row.patents2025Share * 100}%"></i></span></td></tr>`).join('');
    const east = regional.regions.find(row => row.region === '东部');
    root.querySelector('#pc-region-reading').innerHTML = `<div><h4>政策与专利均呈空间集中</h4><p>东部占样本累计政策的 <b>${percent(east.policyCumulative2025Share)}</b>，占 2025 年度专利的 <b>${percent(east.patents2025Share)}</b>。该地区 ${east.sampleCityCount} 个样本城市中，${east.citiesWithPolicy2025} 城已有政策记录。</p></div>`;
    const regionByProvince = Object.fromEntries(regional.regions.flatMap(row => row.provinces.map(province => [province, row.region])));
    root.querySelector('#pc-province-rows').innerHTML = regional.provinces.map(row => `<tr><th scope="row">${safe(row.province)}</th><td>${safe(regionByProvince[row.province])}</td><td>${numbers(row.sampleCityCount)}</td><td>${numbers(row.citiesWithPolicy2025)}</td><td>${numbers(row.policyCumulative2025)}</td><td>${numbers(row.patents2025)}</td><td>${numbers(row.patents2013to2025)}</td></tr>`).join('');
    root.querySelector('#pc-region-mapping').innerHTML = `<dl>${regional.regions.map(row => `<div><dt>${safe(row.region)}</dt><dd>${safe(row.provinces.join('、'))}</dd></div>`).join('')}</dl>`;
  }
  function renderProvinces(metric) {
    if (!regional?.rankings) return;
    const field = metric === 'patent' ? 'patents2025' : 'policyCumulative2025';
    const unit = metric === 'patent' ? '件' : '篇';
    const rows = regional.rankings[field].slice(0, 6);
    root.querySelector('#pc-province-chart').innerHTML = rows.map(row => `<div class="pc-province-bar"><div><span>${safe(row.province)}</span><b>${numbers(row.value)} ${unit}<small>${percent(row.share)}</small></b></div><span class="pc-province-track ${metric === 'patent' ? 'pc-province-blue' : ''}" role="img" aria-label="${safe(row.province)} ${numbers(row.value)}${unit}，占样本${percent(row.share)}"><i style="width:${row.value / rows[0].value * 100}%"></i></span></div>`).join('');
    const concentration = regional.concentration[field].top5;
    root.querySelector('#pc-province-note').textContent = `前五合计 ${numbers(concentration.count)} ${unit}，占样本 ${percent(concentration.share)}。`;
    root.querySelectorAll('[data-region-metric]').forEach(button => {const active=button.dataset.regionMetric === metric;button.classList.toggle('is-active',active);button.setAttribute('aria-pressed',String(active));});
  }
  root.querySelectorAll('[data-region-metric]').forEach(button => on(button, 'click', () => renderProvinces(button.dataset.regionMetric)));
  renderProvinces('policy');
  const dialog=root.querySelector('.pc-lightbox');
  let previousFocus;
  root.querySelectorAll('[data-zoom]').forEach(button=>on(button, 'click',()=>{
    const source=new URL(button.dataset.zoom,document.baseURI).href;
    previousFocus=button;
    dialog.querySelector('img').src=source;
    dialog.querySelector('img').alt=button.dataset.caption;
    dialog.querySelector('h2').textContent=button.dataset.caption;
    dialog.querySelector('a').href=source;
    dialog.showModal();
  }));
  on(dialog.querySelector('[data-close-dialog]'), 'click',()=>dialog.close());
  on(dialog, 'click',event=>{if(event.target===dialog){const box=dialog.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)dialog.close();}});
  on(dialog, 'close',()=>previousFocus?.focus());
  const links=[...root.querySelectorAll('.pc-section-nav a')];
  links.forEach(link=>on(link, 'click',event=>{
    const section=root.querySelector(link.getAttribute('href'));
    if(!section)return;
    event.preventDefault();
    section.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  }));
  let observer;
  if ('IntersectionObserver' in window) {
    observer=new IntersectionObserver(entries=>{
      const visible=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);
      if(visible[0])links.forEach(link=>{const active=link.hash===`#${visible[0].target.id}`;link.classList.toggle('is-active',active);if(active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});
    },{rootMargin:'-160px 0px -55% 0px',threshold:0});
    links.forEach(link=>observer.observe(root.querySelector(link.hash)));
  }
  const controller = {selectCase, destroy() {
    if (dialog.open) dialog.close();
    observer?.disconnect();
    listeners.forEach(remove => remove());
    delete root._policyCaseController;
    delete root.dataset.initialized;
  }};
  root._policyCaseController = controller;
  return controller;
  }
  window.PolicyCases = {mount};
  mount(document.querySelector('.policy-case-app'));
})();
