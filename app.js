/* Seahawks vs. el Universo — chart + stats rendering */
(function () {
  "use strict";

  const games = DATA.games;
  const corr = DATA.correlations;
  const summary = DATA.summary;

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  const labels = games.map((g) => {
    const d = new Date(g.date + "T00:00:00");
    return d.toLocaleDateString("es-CL", { month: "short", day: "numeric", year: "2-digit" });
  });

  // ---- season boundary annotations (vertical-ish separation via gridlines) --
  const seasonStartIdx = [];
  let prevSeason = null;
  games.forEach((g, i) => {
    if (g.season !== prevSeason) {
      seasonStartIdx.push(i);
      prevSeason = g.season;
    }
  });

  function fmtNum(n, opts) {
    return new Intl.NumberFormat("es-CL", opts || {}).format(n);
  }

  // ---------------------------------------------------------------------
  // Record tiles
  // ---------------------------------------------------------------------
  const recordRow = document.getElementById("record-row");
  Object.keys(DATA.records)
    .sort()
    .forEach((season) => {
      const r = DATA.records[season];
      const tile = document.createElement("div");
      tile.className = "record-tile";
      tile.innerHTML = `<div class="yr">${season}</div><div class="rec">${r.w}-${r.l}</div>`;
      recordRow.appendChild(tile);
    });

  // ---------------------------------------------------------------------
  // Chart helpers
  // ---------------------------------------------------------------------
  const sharedScales = {
    x: {
      grid: { display: false },
      ticks: {
        color: cssVar("--text-muted"),
        maxRotation: 0,
        autoSkip: true,
        font: { size: 10 },
      },
      border: { color: cssVar("--baseline") },
    },
  };

  function baseOptions(yExtra) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: cssVar("--surface-1"),
          titleColor: cssVar("--text-primary"),
          bodyColor: cssVar("--text-secondary"),
          borderColor: cssVar("--border"),
          borderWidth: 1,
          padding: 8,
          titleFont: { size: 11 },
          bodyFont: { size: 12 },
        },
      },
      scales: {
        x: sharedScales.x,
        y: Object.assign(
          {
            grid: { color: cssVar("--gridline") },
            ticks: { color: cssVar("--text-muted"), font: { size: 10 } },
            border: { display: false },
          },
          yExtra || {}
        ),
      },
    };
  }

  function marginChart(canvasId, colorWin, colorLoss) {
    const ctx = document.getElementById(canvasId);
    const margins = games.map((g) => g.margin);
    const colors = margins.map((m) => (m >= 0 ? colorWin : colorLoss));
    return new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Margen",
            data: margins,
            backgroundColor: colors,
            borderRadius: 4,
            borderSkipped: false,
            barPercentage: 0.9,
            categoryPercentage: 0.9,
          },
        ],
      },
      options: Object.assign(baseOptions({ grace: "10%" }), {
        plugins: Object.assign({}, baseOptions().plugins, {
          tooltip: Object.assign({}, baseOptions().plugins.tooltip, {
            callbacks: {
              title: (items) => {
                const g = games[items[0].dataIndex];
                return `${g.date} · ${g.result === "W" ? "Victoria" : "Derrota"} ${g.pf}-${g.pa}`;
              },
              label: (item) => {
                const g = games[item.dataIndex];
                return `vs ${g.opponent}`;
              },
            },
          }),
        }),
      }),
    });
  }

  function metricLineChart(canvasId, field, color, fmt) {
    const ctx = document.getElementById(canvasId);
    const values = games.map((g) => g[field]);
    return new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: field,
            data: values,
            borderColor: color,
            backgroundColor: color,
            borderWidth: 2,
            pointRadius: 2,
            pointHoverRadius: 5,
            tension: 0,
            fill: false,
          },
        ],
      },
      options: Object.assign(baseOptions({ grace: "8%" }), {
        plugins: Object.assign({}, baseOptions().plugins, {
          tooltip: Object.assign({}, baseOptions().plugins.tooltip, {
            callbacks: {
              title: (items) => games[items[0].dataIndex].date,
              label: (item) => fmt(item.raw),
            },
          }),
        }),
      }),
    });
  }

  function safeChart(fn) {
    try {
      if (typeof Chart === "undefined") throw new Error("Chart.js no cargó");
      fn();
    } catch (e) {
      console.warn("No se pudo dibujar un gráfico:", e);
    }
  }

  safeChart(() => marginChart("chart-snow-margin", cssVar("--series-win"), cssVar("--series-loss")));
  safeChart(() =>
    metricLineChart("chart-snow-metric", "snow_km2", cssVar("--series-snow"), (v) =>
      `${fmtNum(v / 1e6, { maximumFractionDigits: 1 })} M km²`
    )
  );

  safeChart(() => marginChart("chart-btc-margin", cssVar("--series-win"), cssVar("--series-loss")));
  safeChart(() =>
    metricLineChart("chart-btc-metric", "btc_usd", cssVar("--series-btc"), (v) =>
      `$${fmtNum(v, { maximumFractionDigits: 0 })}`
    )
  );

  safeChart(() => marginChart("chart-launch-margin", cssVar("--series-win"), cssVar("--series-loss")));
  safeChart(() =>
    metricLineChart("chart-launch-metric", "launches", cssVar("--series-launch"), (v) =>
      `${v} lanzamientos`
    )
  );

  safeChart(() => marginChart("chart-moon-margin", cssVar("--series-win"), cssVar("--series-loss")));
  safeChart(() =>
    metricLineChart("chart-moon-metric", "moon_pct", cssVar("--series-moon"), (v) => `${v}% iluminada`)
  );

  // ---------------------------------------------------------------------
  // Stat cards + verdicts
  // ---------------------------------------------------------------------
  function renderStats(id, metricKey, fmt, label) {
    const c = corr[metricKey];
    const s = summary[metricKey];
    const el = document.getElementById(id);
    el.innerHTML = `
      <div class="stat-card">
        <div class="k">Correlación con victoria (r)</div>
        <div class="v">${c.r_win.toFixed(3)}</div>
      </div>
      <div class="stat-card">
        <div class="k">Correlación con margen de puntos (r)</div>
        <div class="v">${c.r_margin.toFixed(3)}</div>
      </div>
      <div class="stat-card">
        <div class="k">Promedio en meses/partidos con victoria</div>
        <div class="v">${fmt(s.avg_on_win)}</div>
      </div>
      <div class="stat-card">
        <div class="k">Promedio en meses/partidos con derrota</div>
        <div class="v">${fmt(s.avg_on_loss)}</div>
      </div>
    `;
  }

  function verdictFor(r) {
    const abs = Math.abs(r);
    if (abs < 0.08) return "básicamente cero — el universo no tiene idea de que existimos";
    if (abs < 0.2) return "ruido con pretensiones de patrón";
    return "la casualidad más decidida de esta página (sigue siendo casualidad)";
  }

  renderStats("stat-snow", "snow_km2", (v) => `${fmtNum(v / 1e6, { maximumFractionDigits: 1 })} M km²`, "nieve");
  document.getElementById("verdict-snow").innerHTML =
    `<strong>Veredicto:</strong> r = ${corr.snow_km2.r_win.toFixed(3)} con victorias — ${verdictFor(
      corr.snow_km2.r_win
    )}. La nieve del hemisferio norte le cae literalmente igual si Seattle gana o pierde.`;

  renderStats("stat-btc", "btc_usd", (v) => `$${fmtNum(v, { maximumFractionDigits: 0 })}`, "bitcoin");
  document.getElementById("verdict-btc").innerHTML =
    `<strong>Veredicto:</strong> en meses donde los Seahawks ganaron, bitcoin promedió
    $${fmtNum(summary.btc_usd.avg_on_win, { maximumFractionDigits: 0 })}; en meses de derrota,
    $${fmtNum(summary.btc_usd.avg_on_loss, { maximumFractionDigits: 0 })}. r = ${corr.btc_usd.r_margin.toFixed(
      3
    )} con el margen — ${verdictFor(corr.btc_usd.r_margin)}. Antes de que alguien arme una estrategia de trading con esto: no.`;

  renderStats("stat-launch", "launches", (v) => `${fmtNum(v, { maximumFractionDigits: 1 })}`, "lanzamientos");
  document.getElementById("verdict-launch").innerHTML =
    `<strong>Veredicto:</strong> r = ${corr.launches.r_win.toFixed(3)} con victorias — ${verdictFor(
      corr.launches.r_win
    )}. Es la correlación más alta de las cuatro. La NASA y SpaceX lo niegan.`;

  renderStats("stat-moon", "moon_pct", (v) => `${fmtNum(v, { maximumFractionDigits: 1 })}%`, "luna");
  document.getElementById("verdict-moon").innerHTML =
    `<strong>Veredicto:</strong> r = ${corr.moon_pct.r_win.toFixed(3)} con victorias — ${verdictFor(
      corr.moon_pct.r_win
    )}. Ni la luna llena nos tiene fe.`;

  // ---------------------------------------------------------------------
  // Ranking (sorted by |r_win| descending)
  // ---------------------------------------------------------------------
  const names = {
    snow_km2: "❄️ Nieve del hemisferio norte",
    btc_usd: "₿ Precio del bitcoin",
    launches: "🚀 Lanzamientos de cohetes",
    moon_pct: "🌕 Iluminación lunar",
  };
  const ranked = Object.keys(corr)
    .map((k) => ({ k, r: corr[k].r_win }))
    .sort((a, b) => Math.abs(b.r) - Math.abs(a.r));
  const rankingList = document.getElementById("ranking-list");
  ranked.forEach((item, i) => {
    const li = document.createElement("li");
    li.innerHTML = `<span class="r">#${i + 1}</span> — ${names[item.k]}: r = ${item.r.toFixed(
      3
    )} con el resultado del partido.`;
    rankingList.appendChild(li);
  });

  // ---------------------------------------------------------------------
  // Full table
  // ---------------------------------------------------------------------
  const tbody = document.querySelector("#full-table tbody");
  games.forEach((g) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${g.season}</td>
      <td>${g.week}</td>
      <td>${g.date}</td>
      <td>${g.opponent}</td>
      <td>${g.result === "W" ? '<span class="w-pill">W</span>' : '<span class="l-pill">L</span>'}</td>
      <td>${g.pf}-${g.pa}</td>
      <td>${fmtNum(g.snow_km2 / 1e6, { maximumFractionDigits: 1 })}</td>
      <td>$${fmtNum(g.btc_usd, { maximumFractionDigits: 0 })}</td>
      <td>${g.launches}</td>
      <td>${g.moon_pct}%</td>
    `;
    tbody.appendChild(tr);
  });
})();
