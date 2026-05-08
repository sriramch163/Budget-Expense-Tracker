// ── Dark Mode ──
(function () {
  const html = document.documentElement;
  const saved = localStorage.getItem('theme') || 'light';
  html.setAttribute('data-theme', saved);

  function syncIcons(theme) {
    document.querySelectorAll('#themeIcon, #themeIconDesktop').forEach(el => {
      el.className = theme === 'dark' ? 'fa fa-moon' : 'fa fa-sun';
    });
  }
  syncIcons(saved);

  function toggleTheme() {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    syncIcons(next);
    if (typeof updateChartsTheme === 'function') updateChartsTheme(next);
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
    document.getElementById('themeToggleDesktop')?.addEventListener('click', toggleTheme);
  });
})();

// ── Mobile Sidebar ──
function openSidebar() {
  document.getElementById('sidebar')?.classList.add('open');
  document.getElementById('sidebarOverlay')?.classList.add('open');
}
function closeSidebar() {
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('sidebarOverlay')?.classList.remove('open');
}
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('hamburger')?.addEventListener('click', openSidebar);
  document.getElementById('sidebarClose')?.addEventListener('click', closeSidebar);
});

// ── Quick-Add Modal ──
function openQuickAdd() {
  document.getElementById('quickAddBackdrop')?.classList.add('open');
  document.getElementById('quickAddModal')?.classList.add('open');
  const d = document.getElementById('qa-date-input');
  if (d && !d.value) d.value = new Date().toISOString().split('T')[0];
}
function closeQuickAdd() {
  document.getElementById('quickAddBackdrop')?.classList.remove('open');
  document.getElementById('quickAddModal')?.classList.remove('open');
}

// ── Auto-dismiss flash messages ──
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(el => setTimeout(() => el.remove(), 5000));
});

// ── Confetti ──
function launchConfetti() {
  const canvas = document.createElement('canvas');
  canvas.id = 'confetti-canvas';
  document.body.appendChild(canvas);
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  const ctx = canvas.getContext('2d');
  const pieces = Array.from({ length: 120 }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * -canvas.height,
    r: Math.random() * 8 + 4,
    d: Math.random() * 120 + 60,
    color: ['#7c3aed','#10b981','#f59e0b','#ef4444','#3b82f6','#ec4899'][Math.floor(Math.random()*6)],
    tilt: Math.random() * 10 - 10,
    tiltAngle: 0,
    tiltSpeed: Math.random() * 0.1 + 0.05
  }));
  let frame = 0;
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    pieces.forEach(p => {
      p.tiltAngle += p.tiltSpeed;
      p.y += (Math.cos(frame / p.d) + 1.5);
      p.x += Math.sin(frame / 30) * 0.5;
      p.tilt = Math.sin(p.tiltAngle) * 12;
      ctx.beginPath();
      ctx.lineWidth = p.r;
      ctx.strokeStyle = p.color;
      ctx.moveTo(p.x + p.tilt + p.r / 2, p.y);
      ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 2);
      ctx.stroke();
    });
    frame++;
    if (frame < 200) requestAnimationFrame(draw);
    else canvas.remove();
  }
  draw();
}

// Auto-launch confetti if goal just completed (flash message contains 🎉)
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert-success').forEach(el => {
    if (el.textContent.includes('🎉') || el.textContent.includes('completed') || el.textContent.includes('reached')) {
      launchConfetti();
    }
  });
});

// ── Animated number count-up ──
function animateNumber(el) {
  const raw = el.textContent.replace(/[^0-9.]/g, '');
  const target = parseFloat(raw);
  if (isNaN(target) || target === 0) return;
  const prefix = el.textContent.match(/^[^0-9]*/)?.[0] || '';
  const suffix = el.textContent.match(/[^0-9.]*$/)?.[0] || '';
  const isInt = !el.textContent.includes('.');
  const duration = Math.min(1200, Math.max(600, target / 10));
  const start = performance.now();
  function step(now) {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const val = target * ease;
    el.textContent = prefix + (isInt ? Math.round(val).toLocaleString('en-IN') : val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })) + suffix;
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

document.addEventListener('DOMContentLoaded', () => {
  // Count-up for stat values and balance
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateNumber(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });
  document.querySelectorAll('.stat-value, .balance-hero-value, .balance-stat-value, .salary-banner-value').forEach(el => observer.observe(el));

  // Ripple + magnetic effect on all buttons
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const rect = this.getBoundingClientRect();
      const ripple = document.createElement('span');
      const size = Math.max(rect.width, rect.height);
      ripple.style.cssText = `position:absolute;width:${size}px;height:${size}px;border-radius:50%;background:rgba(255,255,255,.35);transform:scale(0);left:${e.clientX - rect.left - size/2}px;top:${e.clientY - rect.top - size/2}px;pointer-events:none;animation:ripple .5s ease-out forwards`;
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });

    // Magnetic pull toward cursor
    btn.addEventListener('mousemove', function(e) {
      const rect = this.getBoundingClientRect();
      const dx = (e.clientX - rect.left - rect.width  / 2) * 0.22;
      const dy = (e.clientY - rect.top  - rect.height / 2) * 0.22;
      this.style.transform = `translate(${dx}px, ${dy}px) scale(1.04)`;
    });
    btn.addEventListener('mouseleave', function() {
      this.style.transform = '';
    });
  });

  // Stagger chart card entrance
  document.querySelectorAll('.chart-card').forEach((el, i) => {
    el.style.animationDelay = `${0.15 + i * 0.1}s`;
  });

  // Animate progress bars on scroll
  const barObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        const target = bar.style.width;
        bar.style.width = '0';
        requestAnimationFrame(() => {
          bar.style.transition = 'width .9s cubic-bezier(.4,0,.2,1)';
          bar.style.width = target;
        });
        barObserver.unobserve(bar);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.goal-progress-fill, .alert-progress-bar').forEach(el => barObserver.observe(el));

  // Pie chart slice hover tooltip enhancement
  document.querySelectorAll('#pieChart').forEach(canvas => {
    canvas.addEventListener('mousemove', () => { canvas.style.cursor = 'pointer'; });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });
});

// ── Dashboard charts ──
if (typeof pieLabels !== 'undefined') {
  const rupee = v => '₹' + Number(v).toLocaleString('en-IN', { minimumFractionDigits: 0 });

  const T = {
    dark:  { grid: 'rgba(255,255,255,.08)', pieBorder: '#1a1a2e', tick: '#94a3b8', line: '#60a5fa', lineBg: 'rgba(96,165,250,.3)',  lineBgEnd: 'rgba(96,165,250,.02)',  income: 'rgba(96,165,250,.8)',  incomeBorder: '#60a5fa', tooltipBg: '#1a1a2e', tooltipTitle: '#60a5fa' },
    light: { grid: '#e2e8f0',              pieBorder: '#ffffff',  tick: '#64748b', line: '#10b981', lineBg: 'rgba(16,185,129,.3)', lineBgEnd: 'rgba(16,185,129,.02)', income: 'rgba(16,185,129,.8)', incomeBorder: '#10b981', tooltipBg: '#1e1b4b', tooltipTitle: '#a78bfa' }
  };
  const theme = () => T[document.documentElement.getAttribute('data-theme')] || T.light;

  const fallback = ['#7c3aed','#10b981','#f59e0b','#ef4444','#3b82f6','#ec4899','#14b8a6','#f97316'];
  const pieColors_ = pieColors.length ? pieColors : fallback;

  let pieChart, lineChart, barChart;

  const pieCtx = document.getElementById('pieChart');
  if (pieCtx && pieValues.length) {
    const dateFrom = pieCtx.dataset.dateFrom;
    const dateTo   = pieCtx.dataset.dateTo;
    pieChart = new Chart(pieCtx, {
      type: 'doughnut',
      data: {
        labels: pieLabels,
        datasets: [{ data: pieValues, backgroundColor: pieColors_, borderWidth: 3, borderColor: theme().pieBorder, hoverOffset: 14 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        animation: { animateRotate: true, animateScale: true, duration: 900, easing: 'easeOutQuart' },
        onClick(_, elements) {
          if (!elements.length) return;
          const idx = elements[0].index;
          const catId = pieCatIds[idx];
          if (!catId) return;
          window.location.href = `/expenses?category_id=${catId}&date_from=${dateFrom}&date_to=${dateTo}`;
        },
        plugins: {
          legend: { position: 'bottom', labels: { padding: 14, font: { size: 12, weight: '600' }, usePointStyle: true, color: theme().tick } },
          tooltip: { backgroundColor: theme().tooltipBg, titleColor: theme().tooltipTitle, bodyColor: '#e2e8f0', padding: 12, cornerRadius: 10, displayColors: true,
            callbacks: { label: ctx => `  ${ctx.label}: ${rupee(ctx.parsed)}` } }
        },
        cutout: '68%'
      }
    });
    pieCtx.style.cursor = 'pointer';
  }

  // ── Crosshair plugin (shared by line & bar) ──
  const crosshairPlugin = {
    id: 'crosshair',
    afterDraw(chart) {
      if (!chart._crosshair) return;
      const { x, y } = chart._crosshair;
      const { left, top, right, bottom } = chart.chartArea;
      const ctx2 = chart.ctx;
      ctx2.save();
      ctx2.setLineDash([5, 4]);
      ctx2.lineWidth = 1;
      ctx2.strokeStyle = 'rgba(167,139,250,0.55)';
      // vertical line
      ctx2.beginPath(); ctx2.moveTo(x, top); ctx2.lineTo(x, bottom); ctx2.stroke();
      // horizontal line
      ctx2.beginPath(); ctx2.moveTo(left, y); ctx2.lineTo(right, y); ctx2.stroke();
      // dot at intersection
      ctx2.setLineDash([]);
      ctx2.beginPath();
      ctx2.arc(x, y, 4, 0, Math.PI * 2);
      ctx2.fillStyle = 'rgba(167,139,250,0.8)';
      ctx2.fill();
      ctx2.restore();
    }
  };

  function attachCrosshair(canvas, chartRef) {
    canvas.addEventListener('mousemove', e => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const chart = chartRef();
      if (!chart) return;
      const { left, top, right, bottom } = chart.chartArea;
      if (mx >= left && mx <= right && my >= top && my <= bottom) {
        chart._crosshair = { x: mx, y: my };
      } else {
        chart._crosshair = null;
      }
      chart.draw();
    });
    canvas.addEventListener('mouseleave', () => {
      const chart = chartRef();
      if (!chart) return;
      chart._crosshair = null;
      chart.draw();
    });
  }

  const lineCtx = document.getElementById('lineChart');
  if (lineCtx && lineValues.some(v => v > 0)) {
    lineChart = new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: lineLabels,
        datasets: [{
          label: 'Daily Spend', data: lineValues,
          borderColor: theme().line,
          backgroundColor: ctx => {
            const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 220);
            g.addColorStop(0, theme().lineBg); g.addColorStop(1, theme().lineBgEnd);
            return g;
          },
          borderWidth: 2.5, pointBackgroundColor: theme().line,
          pointRadius: 4, pointHoverRadius: 8,
          pointHoverBackgroundColor: '#fff', pointHoverBorderWidth: 3,
          fill: true, tension: 0.4
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        animation: { duration: 1000, easing: 'easeOutQuart' },
        plugins: { legend: { display: false }, crosshair: {},
          tooltip: { backgroundColor: theme().tooltipBg, titleColor: theme().tooltipTitle, bodyColor: '#e2e8f0', padding: 12, cornerRadius: 10, displayColors: true,
            callbacks: { label: ctx => `  ${rupee(ctx.parsed.y)}` } } },
        scales: {
          y: { beginAtZero: true, ticks: { callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v), font: { size: 11 }, color: theme().tick }, grid: { color: theme().grid } },
          x: { grid: { display: false }, ticks: { font: { size: 10 }, maxTicksLimit: 10, color: theme().tick } }
        }
      },
      plugins: [crosshairPlugin]
    });
    attachCrosshair(lineCtx, () => lineChart);
  }

  const barCtx = document.getElementById('barChart');
  if (barCtx) {
    barChart = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: trendLabels,
        datasets: [
          { label: 'Income',   data: trendIncome,   backgroundColor: theme().income,          borderColor: theme().incomeBorder, borderWidth: 0, borderRadius: 8, borderSkipped: false },
          { label: 'Expenses', data: trendExpenses, backgroundColor: 'rgba(239,68,68,.75)', borderColor: '#ef4444',            borderWidth: 0, borderRadius: 8, borderSkipped: false }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        animation: { duration: 1000, easing: 'easeOutBounce', delay: ctx => ctx.dataIndex * 80 },
        plugins: { legend: { display: false }, crosshair: {},
          tooltip: { backgroundColor: theme().tooltipBg, titleColor: theme().tooltipTitle, bodyColor: '#e2e8f0', padding: 12, cornerRadius: 10, displayColors: true,
            callbacks: { label: ctx => `  ${ctx.dataset.label}: ${rupee(ctx.parsed.y)}` } } },
        scales: {
          y: { beginAtZero: true, ticks: { callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v), font: { size: 11 }, color: theme().tick }, grid: { color: theme().grid } },
          x: { grid: { display: false }, ticks: { font: { size: 11 }, color: theme().tick } }
        }
      },
      plugins: [crosshairPlugin]
    });
    attachCrosshair(barCtx, () => barChart);
  }

  // Live-update all charts when theme toggles
  window.updateChartsTheme = function () {
    const t = theme();

    if (pieChart) {
      pieChart.data.datasets[0].borderColor = t.pieBorder;
      pieChart.options.plugins.legend.labels.color = t.tick;
      pieChart.options.plugins.tooltip.backgroundColor = t.tooltipBg;
      pieChart.options.plugins.tooltip.titleColor = t.tooltipTitle;
      pieChart.update();
    }

    if (lineChart) {
      lineChart.data.datasets[0].borderColor = t.line;
      lineChart.data.datasets[0].pointBackgroundColor = t.line;
      // force gradient to re-evaluate with new theme colours
      lineChart.data.datasets[0].backgroundColor = ctx => {
        const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 220);
        g.addColorStop(0, t.lineBg); g.addColorStop(1, t.lineBgEnd);
        return g;
      };
      lineChart.options.plugins.tooltip.backgroundColor = t.tooltipBg;
      lineChart.options.plugins.tooltip.titleColor = t.tooltipTitle;
      lineChart.options.scales.y.ticks.color = t.tick;
      lineChart.options.scales.y.grid.color  = t.grid;
      lineChart.options.scales.x.ticks.color = t.tick;
      lineChart.update();
    }

    if (barChart) {
      barChart.data.datasets[0].backgroundColor = t.income;
      barChart.data.datasets[0].borderColor      = t.incomeBorder;
      barChart.options.plugins.tooltip.backgroundColor = t.tooltipBg;
      barChart.options.plugins.tooltip.titleColor = t.tooltipTitle;
      barChart.options.scales.y.ticks.color = t.tick;
      barChart.options.scales.y.grid.color  = t.grid;
      barChart.options.scales.x.ticks.color = t.tick;
      barChart.update();
    }
  };
}

// ── Dashboard widget drag-and-drop ──
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('dashboardWidgets');
  if (!container || typeof Sortable === 'undefined') return;

  const STORAGE_KEY = 'dashboard_widget_order';

  function applyOrder(order) {
    order.forEach(id => {
      const el = container.querySelector(`[data-widget-id="${id}"]`);
      if (el) container.appendChild(el);
    });
  }

  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    try { applyOrder(JSON.parse(saved)); } catch (_) {}
  }

  Sortable.create(container, {
    animation: 180,
    handle: '.widget-drag-handle',
    ghostClass: 'widget-ghost',
    chosenClass: 'widget-chosen',
    onEnd() {
      const order = [...container.querySelectorAll('[data-widget-id]')].map(el => el.dataset.widgetId);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
    }
  });

  container.querySelectorAll('.dashboard-widget').forEach(w => {
    const handle = document.createElement('div');
    handle.className = 'widget-drag-handle';
    handle.innerHTML = '<i class="fa fa-grip-lines"></i>';
    handle.title = 'Drag to reorder';
    w.prepend(handle);
  });
});

// ── Mobile search overlay ──
function openMobileSearch() {
  document.getElementById('mobileSearchOverlay')?.classList.add('open');
  setTimeout(() => document.getElementById('mobileSearchInput')?.focus(), 50);
}
function closeMobileSearch() {
  document.getElementById('mobileSearchOverlay')?.classList.remove('open');
}
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('mobileSearchToggle')?.addEventListener('click', openMobileSearch);
});
