/**
 * Real-Time Trading Command Center Client
 * Handles SSE live telemetry, table filtering, and execution controls.
 */

let globalState = null;
let searchQuery = "";
let signalFilter = "ALL";

document.addEventListener("DOMContentLoaded", () => {
    initSSE();
    bindEvents();
});

function initSSE() {
    const eventSource = new EventSource("/api/stream");

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            globalState = data;
            renderDashboard(data);
        } catch (e) {
            console.error("Failed to parse SSE packet:", e);
        }
    };

    eventSource.onerror = (err) => {
        console.warn("SSE connection interrupted, falling back to HTTP poll...", err);
        eventSource.close();
        setTimeout(pollFallback, 2000);
    };
}

async function pollFallback() {
    try {
        const res = await fetch("/api/state");
        if (res.ok) {
            const data = await res.json();
            globalState = data;
            renderDashboard(data);
        }
    } catch (e) {
        console.error("Poll failed:", e);
    }
    setTimeout(pollFallback, 3000);
}

function bindEvents() {
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            searchQuery = e.target.value.trim().toUpperCase();
            if (globalState) renderMarketsTable(globalState.markets);
        });
    }

    const filterSelect = document.getElementById("signal-filter");
    if (filterSelect) {
        filterSelect.addEventListener("change", (e) => {
            signalFilter = e.target.value;
            if (globalState) renderMarketsTable(globalState.markets);
        });
    }

    const btnScan = document.getElementById("btn-scan");
    if (btnScan) {
        btnScan.addEventListener("click", async () => {
            btnScan.classList.add("opacity-50", "pointer-events-none");
            try {
                await fetch("/api/scan", { method: "POST" });
            } finally {
                setTimeout(() => btnScan.classList.remove("opacity-50", "pointer-events-none"), 1000);
            }
        });
    }

    const btnToggle = document.getElementById("btn-toggle");
    if (btnToggle) {
        btnToggle.addEventListener("click", async () => {
            await fetch("/api/toggle_pause", { method: "POST" });
        });
    }

    const btnCloseAll = document.getElementById("btn-close-all");
    if (btnCloseAll) {
        btnCloseAll.addEventListener("click", async () => {
            if (confirm("Are you sure you want to immediately close ALL open positions at market price?")) {
                await fetch("/api/close_all", { method: "POST" });
            }
        });
    }
}

function renderDashboard(state) {
    if (!state) return;

    // Header updates
    const statusBadge = document.getElementById("status-badge");
    const isRunning = state.status === "RUNNING";
    if (statusBadge) {
        statusBadge.className = isRunning
            ? "px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5"
            : "px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-1.5";
        statusBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full ${isRunning ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}"></span> ${state.status}`;
    }

    const btnToggle = document.getElementById("btn-toggle");
    if (btnToggle) {
        btnToggle.innerHTML = isRunning
            ? `<i data-lucide="pause" class="w-3.5 h-3.5"></i> Pause`
            : `<i data-lucide="play" class="w-3.5 h-3.5"></i> Resume`;
    }

    const marketsCount = document.getElementById("active-markets-count");
    if (marketsCount) marketsCount.textContent = `${state.total_markets_scanned || 0} Markets`;

    const feedName = document.getElementById("feed-name");
    if (feedName) feedName.textContent = state.feed_type || "Feed";

    const latencyTag = document.getElementById("latency-tag");
    if (latencyTag) latencyTag.textContent = `⚡ ${state.last_scan_duration_ms || 0} ms`;

    // Account KPIs
    const acc = state.account || {};
    const kpiEquity = document.getElementById("kpi-equity");
    if (kpiEquity) kpiEquity.textContent = `$${(acc.total_equity || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    const kpiCash = document.getElementById("kpi-cash");
    if (kpiCash) kpiCash.textContent = `$${(acc.cash_balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    const kpiUnrealized = document.getElementById("kpi-unrealized");
    if (kpiUnrealized) {
        const u = acc.unrealized_pnl || 0;
        kpiUnrealized.textContent = `${u >= 0 ? "+" : ""}$${u.toFixed(2)}`;
        kpiUnrealized.className = `text-xl font-bold font-mono mt-1 ${u >= 0 ? "text-emerald-400" : "text-rose-400"}`;
    }

    const kpiRealized = document.getElementById("kpi-realized");
    if (kpiRealized) {
        const r = acc.realized_pnl || 0;
        kpiRealized.textContent = `${r >= 0 ? "+" : ""}$${r.toFixed(2)}`;
        kpiRealized.className = `text-xl font-bold font-mono mt-1 ${r >= 0 ? "text-emerald-400" : "text-rose-400"}`;
    }

    const kpiWinRate = document.getElementById("kpi-winrate");
    if (kpiWinRate) kpiWinRate.textContent = `${(acc.win_rate_pct || 0).toFixed(1)}%`;

    const kpiWinLoss = document.getElementById("kpi-win-loss");
    if (kpiWinLoss) kpiWinLoss.textContent = `${acc.winning_trades || 0}W / ${acc.losing_trades || 0}L`;

    const kpiProfitFactor = document.getElementById("kpi-profit-factor");
    if (kpiProfitFactor) kpiProfitFactor.textContent = (acc.profit_factor || 0).toFixed(2);

    const openBadge = document.getElementById("open-positions-badge");
    if (openBadge) openBadge.textContent = `${(state.open_positions || []).length} / ${state.settings?.max_open_positions || 5}`;

    // Render Sub-Views
    renderMarketsTable(state.markets || []);
    renderPositions(state.open_positions || []);
    renderSignals(state.recent_signals || []);
    renderTrades(state.recent_trades || []);

    if (window.lucide) window.lucide.createIcons();
}

function renderMarketsTable(markets) {
    const tbody = document.getElementById("market-table-body");
    if (!tbody) return;

    let filtered = markets;
    if (searchQuery) {
        filtered = filtered.filter(m => m.symbol.toUpperCase().includes(searchQuery));
    }
    if (signalFilter !== "ALL") {
        filtered = filtered.filter(m => m.action === signalFilter);
    }

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="p-8 text-center text-slate-500 font-sans">No matching markets found.</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(m => {
        const changeClass = m.change_24h_pct >= 0 ? "text-emerald-400" : "text-rose-400";
        const changeSign = m.change_24h_pct >= 0 ? "+" : "";

        // RSI color coding
        let rsiClass = "text-slate-300";
        if (m.rsi <= 30) rsiClass = "text-cyan-400 font-bold";
        else if (m.rsi >= 70) rsiClass = "text-rose-400 font-bold";

        // Action Badge
        let actionBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-400">NEUTRAL</span>`;
        if (m.action === "BUY") {
            actionBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 animate-pulse">BUY</span>`;
        } else if (m.action === "SELL") {
            actionBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30">SELL</span>`;
        }

        // Confluence score visualization (-100 to +100)
        const score = m.confluence_score || 0;
        const scoreColor = score > 0 ? "text-emerald-400" : (score < 0 ? "text-rose-400" : "text-slate-400");
        const scoreSign = score > 0 ? "+" : "";

        // Trend badge
        let trendBadge = `<span class="text-slate-400 text-[11px]">${m.trend_bias}</span>`;
        if (m.trend_bias.includes("BULL")) trendBadge = `<span class="text-emerald-400 text-[11px]">▲ ${m.trend_bias}</span>`;
        else if (m.trend_bias.includes("BEAR")) trendBadge = `<span class="text-rose-400 text-[11px]">▼ ${m.trend_bias}</span>`;

        return `
            <tr class="hover:bg-slate-800/40 transition-colors">
                <td class="p-3 font-bold text-white flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full ${m.confluence_score > 50 ? 'bg-emerald-400' : 'bg-slate-600'}"></span>
                    ${m.symbol}
                </td>
                <td class="p-3 text-right font-medium text-slate-100">$${formatPrice(m.price)}</td>
                <td class="p-3 text-right ${changeClass} font-semibold">${changeSign}${m.change_24h_pct.toFixed(2)}%</td>
                <td class="p-3 text-center ${rsiClass}">${m.rsi.toFixed(1)}</td>
                <td class="p-3 text-center ${m.macd_hist >= 0 ? 'text-emerald-400' : 'text-rose-400'}">${m.macd_hist.toFixed(4)}</td>
                <td class="p-3 text-center">${trendBadge}</td>
                <td class="p-3 text-center ${m.volume_ratio >= 1.5 ? 'text-amber-400 font-bold' : 'text-slate-400'}">${m.volume_ratio.toFixed(1)}x</td>
                <td class="p-3 text-center font-bold ${scoreColor}">${scoreSign}${score.toFixed(0)}</td>
                <td class="p-3 text-center">${actionBadge}</td>
            </tr>
        `;
    }).join("");
}

function renderPositions(positions) {
    const list = document.getElementById("positions-list");
    if (!list) return;

    if (!positions || positions.length === 0) {
        list.innerHTML = `<div class="text-center py-6 text-xs text-slate-500 font-sans">No active open positions.</div>`;
        return;
    }

    list.innerHTML = positions.map(p => {
        const pnlClass = p.unrealized_pnl >= 0 ? "text-emerald-400" : "text-rose-400";
        const pnlSign = p.unrealized_pnl >= 0 ? "+" : "";

        return `
            <div class="p-3 rounded-lg bg-[#0b0e14] border border-slate-800 flex flex-col space-y-2">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2 font-mono">
                        <span class="font-bold text-white">${p.symbol}</span>
                        <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${p.side === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">
                            ${p.side === 'BUY' ? 'LONG' : 'SHORT'}
                        </span>
                        <span class="text-[11px] text-slate-400">Qty: ${p.quantity}</span>
                    </div>
                    <div class="font-mono font-bold ${pnlClass} text-sm">
                        ${pnlSign}$${p.unrealized_pnl.toFixed(2)} (${pnlSign}${p.unrealized_pnl_pct.toFixed(2)}%)
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-2 text-[11px] font-mono text-slate-400 bg-slate-900/60 p-2 rounded">
                    <div>Entry: <span class="text-slate-200">$${formatPrice(p.entry_price)}</span></div>
                    <div>SL: <span class="text-rose-400">$${formatPrice(p.stop_loss)}</span></div>
                    <div>TP: <span class="text-emerald-400">$${formatPrice(p.take_profit)}</span></div>
                </div>

                <div class="flex items-center justify-between pt-1">
                    <span class="text-[10px] text-slate-500 font-mono">${p.trailing_stop_active ? '⚡ Trailing Active' : 'Fixed Stop'}</span>
                    <button onclick="closePosition('${p.position_id}')" class="px-2 py-1 text-[11px] font-medium bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 rounded transition-colors">
                        Close Position
                    </button>
                </div>
            </div>
        `;
    }).join("");
}

function renderSignals(signals) {
    const container = document.getElementById("signals-stream");
    if (!container) return;

    if (!signals || signals.length === 0) {
        container.innerHTML = `<div class="text-center py-6 text-slate-500 font-sans">Awaiting high-probability signals...</div>`;
        return;
    }

    container.innerHTML = signals.slice(0, 10).map(s => {
        const isBuy = s.direction === "BUY";
        const badgeColor = isBuy ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" : "bg-rose-500/20 text-rose-400 border-rose-500/30";
        const timeAgo = formatTimeAgo(s.timestamp);

        return `
            <div class="p-2.5 rounded-lg bg-[#0b0e14] border border-slate-800 space-y-1">
                <div class="flex items-center justify-between font-mono">
                    <div class="flex items-center gap-1.5">
                        <span class="font-bold text-white">${s.symbol}</span>
                        <span class="px-1.5 py-0.2 rounded text-[10px] font-bold border ${badgeColor}">${s.direction}</span>
                        <span class="text-[10px] font-bold ${isBuy ? 'text-emerald-400' : 'text-rose-400'}">${s.confluence_score > 0 ? '+' : ''}${s.confluence_score}</span>
                    </div>
                    <span class="text-[10px] text-slate-500">${timeAgo}</span>
                </div>
                <div class="text-[11px] text-slate-400 font-sans">
                    ${(s.reasons || []).slice(0, 2).join(" • ")}
                </div>
            </div>
        `;
    }).join("");
}

function renderTrades(trades) {
    const container = document.getElementById("trades-list");
    if (!container) return;

    if (!trades || trades.length === 0) {
        container.innerHTML = `<div class="text-center py-4 text-slate-500 font-sans">No trades closed yet.</div>`;
        return;
    }

    container.innerHTML = trades.slice(0, 8).map(t => {
        const pnlClass = t.realized_pnl >= 0 ? "text-emerald-400" : "text-rose-400";
        const sign = t.realized_pnl >= 0 ? "+" : "";

        return `
            <div class="p-2 rounded bg-[#0b0e14] border border-slate-800/80 flex items-center justify-between font-mono text-xs">
                <div>
                    <span class="font-bold text-white">${t.symbol}</span>
                    <span class="text-[10px] text-slate-400 ml-1">(${t.exit_reason})</span>
                </div>
                <div class="font-bold ${pnlClass}">
                    ${sign}$${t.realized_pnl.toFixed(2)} (${sign}${t.pnl_pct.toFixed(2)}%)
                </div>
            </div>
        `;
    }).join("");
}

async function closePosition(positionId) {
    try {
        await fetch("/api/close_position", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ position_id: positionId })
        });
    } catch (e) {
        console.error("Close position error:", e);
    }
}

function formatPrice(val) {
    if (val === undefined || val === null) return "0.00";
    if (val < 0.0001) return val.toFixed(7);
    if (val < 1.0) return val.toFixed(4);
    return val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatTimeAgo(epochSec) {
    if (!epochSec) return "";
    const elapsed = Math.floor(Date.now() / 1000 - epochSec);
    if (elapsed < 60) return `${elapsed}s ago`;
    if (elapsed < 3600) return `${Math.floor(elapsed / 60)}m ago`;
    return `${Math.floor(elapsed / 3600)}h ago`;
}
