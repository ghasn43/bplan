"""Render the app's Financial Analysis charts to PNG images for the reports.

The Financial Analysis service already produces chart-ready data (the same data
the React/Recharts dashboard consumes). This module re-draws those charts with
matplotlib so they can be embedded in the Word and PDF reports — no figures are
re-computed here.
"""
from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")  # headless backend — must be set before pyplot import
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

PALETTE = ["#2563eb", "#059669", "#d97706", "#0d9488", "#64748b", "#b45309",
           "#7c3aed", "#dc2626", "#0891b2", "#94a3b8", "#9333ea", "#16a34a"]
GRID = "#e2e8f0"
TEXT = "#334155"
MUTED = "#64748b"


def _fmt(unit):
    if unit == "percent":
        return FuncFormatter(lambda v, _: f"{v:,.0f}%")
    if unit == "ratio":
        return FuncFormatter(lambda v, _: f"{v:,.1f}x")

    def money(v, _):
        a = abs(v)
        if a >= 1e9:
            return f"{v / 1e9:,.1f}B"
        if a >= 1e6:
            return f"{v / 1e6:,.1f}M"
        if a >= 1e3:
            return f"{v / 1e3:,.0f}K"
        return f"{v:,.0f}"

    return FuncFormatter(money)


def _xkey(data):
    if not data:
        return None
    return "period" if "period" in data[0] else "name" if "name" in data[0] else None


def _color(series, i):
    return getattr(series, "color", None) or PALETTE[i % len(PALETTE)]


def _style_axes(ax, unit, rotate=False):
    ax.yaxis.set_major_formatter(_fmt(unit))
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    if rotate:
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(25)
            lbl.set_horizontalalignment("right")


def _legend(ax, fig):
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        fig.legend(handles, labels, loc="lower center", ncol=min(len(labels), 4),
                   frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.04))


def _new_fig():
    fig, ax = plt.subplots(figsize=(7.4, 3.3), dpi=150)
    return fig, ax


def _save(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return buf.getvalue()


# --------------------------------------------------------------------------
# per chart-type renderers
# --------------------------------------------------------------------------
def _draw_line(ax, chart, area=False):
    xk = _xkey(chart.data)
    x = [str(r.get(xk, "")) for r in chart.data]
    for i, s in enumerate(chart.series):
        y = [r.get(s.key, 0) or 0 for r in chart.data]
        c = _color(s, i)
        ax.plot(x, y, marker="o", markersize=3.5, linewidth=2, color=c, label=s.label)
        if area:
            ax.fill_between(range(len(x)), y, alpha=0.12, color=c)


def _draw_bar(ax, chart):
    xk = _xkey(chart.data)
    x = [str(r.get(xk, "")) for r in chart.data]
    s = chart.series[0] if chart.series else None
    key = s.key if s else "value"
    y = [r.get(key, 0) or 0 for r in chart.data]
    ax.bar(x, y, color=PALETTE[0], width=0.6, label=(s.label if s else None))
    return len(x) > 4


def _draw_grouped(ax, chart):
    xk = _xkey(chart.data)
    x = list(range(len(chart.data)))
    labels = [str(r.get(xk, "")) for r in chart.data]
    n = max(len(chart.series), 1)
    w = 0.8 / n
    for i, s in enumerate(chart.series):
        y = [r.get(s.key, 0) or 0 for r in chart.data]
        ax.bar([p + (i - (n - 1) / 2) * w for p in x], y, width=w, color=_color(s, i), label=s.label)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)


def _draw_stacked(ax, chart):
    xk = _xkey(chart.data)
    x = [str(r.get(xk, "")) for r in chart.data]
    pos = [0.0] * len(chart.data)
    neg = [0.0] * len(chart.data)
    for i, s in enumerate(chart.series):
        y = [r.get(s.key, 0) or 0 for r in chart.data]
        base = [pos[j] if y[j] >= 0 else neg[j] for j in range(len(y))]
        ax.bar(x, y, bottom=base, color=_color(s, i), width=0.6, label=s.label)
        for j in range(len(y)):
            if y[j] >= 0:
                pos[j] += y[j]
            else:
                neg[j] += y[j]


def _draw_combo(ax, chart):
    xk = _xkey(chart.data)
    x = list(range(len(chart.data)))
    labels = [str(r.get(xk, "")) for r in chart.data]
    bars = [s for s in chart.series if (s.type or "bar") == "bar"]
    lines = [s for s in chart.series if s.type == "line"]
    n = max(len(bars), 1)
    w = 0.8 / n
    for i, s in enumerate(bars):
        y = [r.get(s.key, 0) or 0 for r in chart.data]
        ax.bar([p + (i - (n - 1) / 2) * w for p in x], y, width=w, color=_color(s, i), label=s.label)
    for j, s in enumerate(lines):
        y = [r.get(s.key, 0) or 0 for r in chart.data]
        ax.plot(x, y, marker="o", markersize=3.5, linewidth=2,
                color=s.color or "#1e293b", label=s.label)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)


def _draw_pie(fig, ax, chart, donut=False):
    items = [(str(r.get("name", "")), abs(r.get("value", 0) or 0)) for r in chart.data]
    items = [it for it in items if it[1] > 0]
    if not items:
        return False
    labels, values = zip(*items)
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(values))]
    wedge = dict(width=0.42, edgecolor="white") if donut else dict(edgecolor="white")
    ax.pie(values, labels=None, colors=colors, startangle=90, counterclock=False,
           wedgeprops=wedge, autopct=lambda p: f"{p:.0f}%", pctdistance=0.78 if donut else 0.6,
           textprops={"fontsize": 7.5, "color": "white", "weight": "bold"})
    ax.set_aspect("equal")
    ax.legend(labels, loc="center left", bbox_to_anchor=(0.98, 0.5), frameon=False, fontsize=8)
    return True


def _draw_waterfall(ax, chart, unit):
    names = [str(r.get("name", "")) for r in chart.data]
    vals = [r.get("value", 0) or 0 for r in chart.data]
    kinds = [r.get("kind", "") for r in chart.data]
    running = 0.0
    for i, (v, k) in enumerate(zip(vals, kinds)):
        if k == "total":
            ax.bar(i, v, color="#1e293b", width=0.6)
            running = v
        else:
            color = "#059669" if v >= 0 else "#dc2626"
            ax.bar(i, v, bottom=running, color=color, width=0.6)
            running += v
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=25, ha="right")


# --------------------------------------------------------------------------
# public API
# --------------------------------------------------------------------------
def render_chart_png(chart, currency: str) -> bytes | None:
    """Render a FinancialAnalysisChart to PNG bytes, or None on failure."""
    try:
        ct = chart.chart_type
        unit = chart.unit
        if ct in ("donut", "pie"):
            fig, ax = plt.subplots(figsize=(6.6, 3.3), dpi=150)
            ok = _draw_pie(fig, ax, chart, donut=(ct == "donut"))
            ax.set_title(chart.title, fontsize=11, color=TEXT, weight="bold", loc="left", pad=10)
            if not ok:
                plt.close(fig)
                return None
            return _save(fig)

        fig, ax = _new_fig()
        rotate = False
        if ct == "line":
            _draw_line(ax, chart)
        elif ct == "area":
            _draw_line(ax, chart, area=True)
        elif ct == "bar":
            rotate = _draw_bar(ax, chart)
        elif ct == "grouped_bar":
            _draw_grouped(ax, chart)
        elif ct == "stacked_bar":
            _draw_stacked(ax, chart)
        elif ct == "combo":
            _draw_combo(ax, chart)
        elif ct == "waterfall":
            _draw_waterfall(ax, chart, unit)
        else:
            _draw_line(ax, chart)

        _style_axes(ax, unit, rotate=rotate or ct == "waterfall")
        ax.axhline(0, color="#cbd5e1", linewidth=0.8)
        ax.set_title(chart.title, fontsize=11, color=TEXT, weight="bold", loc="left", pad=10)
        if ct != "waterfall":
            _legend(ax, fig)
        return _save(fig)
    except Exception:
        plt.close("all")
        return None


def render_report_charts(chart_specs, currency: str) -> list[dict]:
    """Render a list of chart specs, returning rendered images with metadata."""
    out = []
    for ch in chart_specs:
        png = render_chart_png(ch, currency)
        if png:
            out.append({"key": ch.key, "title": ch.title, "description": ch.description,
                        "insight": ch.insight, "png": png})
    return out


def render_scenario_charts(metrics, periods, currency: str) -> list[dict]:
    """Render scenario-comparison metrics (base/conservative/optimistic) as grouped bars."""
    out = []
    scen_color = {"base": "#2563eb", "conservative": "#dc2626", "optimistic": "#059669"}
    for m in metrics:
        try:
            fig, ax = _new_fig()
            x = list(range(len(periods)))
            n = max(len(m.series), 1)
            w = 0.8 / n
            for i, s in enumerate(m.series):
                ax.bar([p + (i - (n - 1) / 2) * w for p in x], s.values, width=w,
                       color=scen_color.get(s.scenario, PALETTE[i]), label=s.label)
            ax.set_xticks(x)
            ax.set_xticklabels([str(p) for p in periods])
            _style_axes(ax, m.format)
            ax.axhline(0, color="#cbd5e1", linewidth=0.8)
            ax.set_title(m.label, fontsize=11, color=TEXT, weight="bold", loc="left", pad=10)
            _legend(ax, fig)
            out.append({"key": m.key, "title": m.label, "description": None, "insight": None, "png": _save(fig)})
        except Exception:
            plt.close("all")
    return out
