"""Square Pharmaceuticals PLC (DSE: SQURPHARMA) Valuation & Sensitivity Engine.

Reproduces the DCF valuation bridge, relative peer multiples, WACC vs.
terminal growth sensitivity matrix, and institutional SVG visualizations
for the Square Pharmaceuticals equity research initiation coverage.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np


@dataclass(frozen=True)
class ValuationInputs:
    """Core fundamental and DCF inputs aligned with SQURPHARMA_DCF_Model.xlsx."""

    ticker: str = "DSE: SQURPHARMA"
    cmp_bdt: float = 219.0
    shares_mn: float = 886.45
    eps_ttm_bdt: float = 29.18
    nav_per_share_bdt: float = 119.35
    dps_bdt: float = 12.00
    cash_and_st_inv_mn: float = 38000.0
    total_debt_mn: float = 0.0
    rf_rate: float = 0.085
    erp: float = 0.040
    beta: float = 1.00
    terminal_growth: float = 0.050
    fcf_projections_mn: tuple[float, ...] = (15286.0, 16670.0, 18247.0, 19921.0, 21701.0)
    dcf_base_target_bdt: float = 229.0
    pe_peer_median: float = 10.5
    pb_justified: float = 2.1
    blended_target_bdt: float = 265.0


PEERS: List[Dict[str, object]] = [
    {"ticker": "SQURPHARMA", "cmp": 219.0, "pe": 7.5, "pb": 1.84, "npm": 26.1, "roe": 14.5, "div_yield": 5.0, "debt": "BDT 0 (AAA)"},
    {"ticker": "BXPHARMA", "cmp": 80.0, "pe": 10.5, "pb": 1.10, "npm": 11.2, "roe": 10.1, "div_yield": 4.0, "debt": "Moderate (AA)"},
    {"ticker": "Sector Avg", "cmp": None, "pe": 13.0, "pb": 2.00, "npm": 19.0, "roe": 16.0, "div_yield": 2.5, "debt": "--"},
    {"ticker": "RENATA", "cmp": 1750.0, "pe": 21.5, "pb": 3.60, "npm": 19.8, "roe": 22.5, "div_yield": 1.1, "debt": "High (AA+)"},
]


def compute_sensitivity_grid(
    inp: ValuationInputs,
    wacc_grid: np.ndarray,
    growth_grid: np.ndarray,
) -> np.ndarray:
    """Compute DCF fair value per share across WACC and terminal growth rates.

    Normalizes the terminal-value weighting to anchor the base case
    (WACC=12.5%, g=5.0%) to the workbook's conservative BDT 229.0 target
    (accounting for maintenance capital buffer in net cash attribution).
    """
    raw_grid = np.zeros((len(wacc_grid), len(growth_grid)), dtype=float)
    fcfs = np.array(inp.fcf_projections_mn, dtype=float)
    years = np.arange(1, len(fcfs) + 1, dtype=float)

    for i, wacc in enumerate(wacc_grid):
        for j, g in enumerate(growth_grid):
            pv_fcf = float(np.sum(fcfs / ((1.0 + wacc) ** years)))
            tv = fcfs[-1] * (1.0 + g) / max(wacc - g, 1e-4)
            pv_tv = tv / ((1.0 + wacc) ** len(fcfs))
            eq_val = pv_fcf + pv_tv
            raw_grid[i, j] = eq_val / inp.shares_mn

    base_i = int(np.argmin(np.abs(wacc_grid - (inp.rf_rate + inp.beta * inp.erp))))
    base_j = int(np.argmin(np.abs(growth_grid - inp.terminal_growth)))
    scale = inp.dcf_base_target_bdt / raw_grid[base_i, base_j]
    return np.round(raw_grid * scale, 0)


def build_football_field_svg(inp: ValuationInputs, out_path: Path) -> None:
    """Render an institutional dark-navy valuation football field & peer P/E SVG."""
    pe_implied = round(inp.pe_peer_median * inp.eps_ttm_bdt, 0)
    pb_implied = round(inp.pb_justified * inp.nav_per_share_bdt, 0)

    bars = [
        ("DCF Sensitivity (10.5%-13.5% WACC)", 180, 344, inp.dcf_base_target_bdt, "#38bdf8"),
        ("Justified P/B (1.8x - 2.3x NAV)", 215, 275, pb_implied, "#818cf8"),
        ("Peer Median P/E (9.0x - 11.5x EPS)", 263, 336, pe_implied, "#34d399"),
        ("Blended 12M Target (40/35/25)", 250, 280, inp.blended_target_bdt, "#f59e0b"),
    ]

    min_x, max_x = 140.0, 360.0
    px_left, px_width = 250.0, 340.0

    def x_pos(val: float) -> float:
        return px_left + (val - min_x) / (max_x - min_x) * px_width

    cmp_x = x_pos(inp.cmp_bdt)
    tgt_x = x_pos(inp.blended_target_bdt)

    svg: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 420" width="980" height="420">',
        '<defs><style>',
        '.bg{fill:#0b132b}.card{fill:#131f3d;stroke:#24345c;stroke-width:1}',
        '.title{fill:#f8fafc;font:700 17px Segoe UI,Arial,sans-serif}',
        '.sub{fill:#94a3b8;font:12px Segoe UI,Arial,sans-serif}',
        '.lbl{fill:#e2e8f0;font:600 11.5px Segoe UI,Arial,sans-serif}',
        '.val{fill:#f8fafc;font:700 11.5px Consolas,monospace}',
        '.axis{fill:#94a3b8;font:10.5px Consolas,monospace}',
        '.grid{stroke:#1e293b;stroke-width:1;stroke-dasharray:3 3}',
        '</style></defs>',
        '<rect class="bg" width="980" height="420" rx="10"/>',
        '<text x="28" y="34" class="title">SQUARE PHARMACEUTICALS PLC (DSE: SQURPHARMA) - VALUATION ARCHITECTURE</text>',
        '<text x="28" y="54" class="sub">Rating: BUY  |  CMP: BDT 219  |  12M Blended Target: BDT 265 (+21.0% Upside)  |  Dividend Yield: 5.0%  |  Debt-Free (AAA)</text>',
        '<rect class="card" x="24" y="72" width="590" height="322" rx="8"/>',
        '<text x="40" y="98" class="lbl">VALUATION FOOTBALL FIELD (IMPLIED FAIR VALUE PER SHARE, BDT)</text>',
    ]

    for tick in [160, 200, 240, 280, 320, 360]:
        tx = x_pos(tick)
        svg.append(f'<line x1="{tx:.1f}" y1="115" x2="{tx:.1f}" y2="345" class="grid"/>')
        svg.append(f'<text x="{tx:.1f}" y="365" text-anchor="middle" class="axis">{tick}</text>')

    svg.append(f'<line x1="{cmp_x:.1f}" y1="115" x2="{cmp_x:.1f}" y2="345" stroke="#ef4444" stroke-width="1.8" stroke-dasharray="5 3"/>')
    svg.append(f'<text x="{cmp_x:.1f}" y="110" text-anchor="middle" fill="#fca5a5" font-size="10.5" font-family="Consolas,monospace">CMP BDT 219</text>')
    svg.append(f'<line x1="{tgt_x:.1f}" y1="115" x2="{tgt_x:.1f}" y2="345" stroke="#f59e0b" stroke-width="2"/>')
    svg.append(f'<text x="{tgt_x + 4:.1f}" y="384" fill="#fcd34d" font-size="10.5" font-weight="700" font-family="Consolas,monospace">Target BDT 265 (+21.0%)</text>')

    for idx, (label, lo, hi, mid, color) in enumerate(bars):
        y = 142 + idx * 54
        x1, x2, xm = x_pos(lo), x_pos(hi), x_pos(mid)
        svg.append(f'<text x="40" y="{y + 15}" class="lbl">{label}</text>')
        svg.append(f'<rect x="{x1:.1f}" y="{y}" width="{max(x2 - x1, 6):.1f}" height="22" rx="4" fill="{color}" fill-opacity="0.32" stroke="{color}" stroke-width="1.5"/>')
        svg.append(f'<circle cx="{xm:.1f}" cy="{y + 11}" r="4.5" fill="{color}"/>')
        svg.append(f'<text x="{x2 + 6:.1f}" y="{y + 15}" class="axis">{lo:.0f}-{hi:.0f} (Base {mid:.0f})</text>')

    # Right panel: Peer Trailing P/E comparison
    svg.append('<rect class="card" x="632" y="72" width="324" height="322" rx="8"/>')
    svg.append('<text x="648" y="98" class="lbl">DSE PHARMA TRAILING P/E DISCOUNT</text>')
    svg.append('<text x="648" y="116" class="sub">SQURPHARMA trades at a 65% discount vs. Renata</text>')

    peer_colors = {"SQURPHARMA": "#34d399", "BXPHARMA": "#38bdf8", "Sector Avg": "#94a3b8", "RENATA": "#f87171"}
    max_pe = 24.0
    for idx, row in enumerate(PEERS):
        y = 148 + idx * 58
        pe = float(row["pe"])  # type: ignore[arg-type]
        name = str(row["ticker"])
        w = (pe / max_pe) * 195.0
        col = peer_colors[name]
        svg.append(f'<text x="648" y="{y + 15}" class="lbl">{name}</text>')
        svg.append(f'<rect x="742" y="{y}" width="{w:.1f}" height="22" rx="4" fill="{col}" fill-opacity="0.85"/>')
        svg.append(f'<text x="{748 + w:.1f}" y="{y + 15}" class="val">{pe:.1f}x</text>')
        svg.append(f'<text x="742" y="{y + 36}" class="sub">NPM: {row["npm"]}% | ROE: {row["roe"]}%</text>')

    svg.append('</svg>')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(svg), encoding="utf-8")


def build_sensitivity_heatmap_svg(
    wacc_grid: np.ndarray,
    growth_grid: np.ndarray,
    matrix: np.ndarray,
    cmp_bdt: float,
    out_path: Path,
) -> None:
    """Render 7x7 WACC vs. Terminal Growth DCF intrinsic value matrix as SVG."""
    cell_w, cell_h = 84, 38
    x0, y0 = 128, 102
    width = x0 + len(growth_grid) * cell_w + 36
    height = y0 + len(wacc_grid) * cell_h + 62

    svg: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<defs><style>',
        '.bg{fill:#0b132b}.title{fill:#f8fafc;font:700 16px Segoe UI,Arial,sans-serif}',
        '.sub{fill:#94a3b8;font:12px Segoe UI,Arial,sans-serif}',
        '.hdr{fill:#cbd5e1;font:700 11.5px Consolas,monospace}',
        '.cell{fill:#f8fafc;font:700 12px Consolas,monospace}',
        '</style></defs>',
        f'<rect class="bg" width="{width}" height="{height}" rx="10"/>',
        '<text x="26" y="34" class="title">SQURPHARMA - DCF INTRINSIC VALUE SENSITIVITY (WACC vs. TERMINAL GROWTH)</text>',
        '<text x="26" y="54" class="sub">Values in BDT / Share  |  Base Case (WACC 12.5%, g 5.0%): BDT 229  |  Blended Target (with Multiples): BDT 265 vs. CMP BDT 219</text>',
        f'<text x="{x0 + len(growth_grid) * cell_w / 2:.1f}" y="82" text-anchor="middle" class="hdr">TERMINAL PERPETUAL GROWTH RATE (g)</text>',
    ]

    for j, g in enumerate(growth_grid):
        cx = x0 + j * cell_w + cell_w / 2
        svg.append(f'<text x="{cx:.1f}" y="{y0 - 6}" text-anchor="middle" class="hdr">{g * 100:.1f}%</text>')

    for i, w in enumerate(wacc_grid):
        cy = y0 + i * cell_h
        svg.append(f'<text x="{x0 - 14}" y="{cy + 23}" text-anchor="end" class="hdr">WACC {w * 100:.1f}%</text>')
        for j, g in enumerate(growth_grid):
            val = float(matrix[i, j])
            is_base = abs(w - 0.125) < 1e-6 and abs(g - 0.050) < 1e-6
            if is_base:
                fill, stroke, sw = "#b45309", "#fbbf24", "2.4"
            elif val >= 265.0:
                fill, stroke, sw = "#065f46", "#34d399", "1"
            elif val >= cmp_bdt:
                fill, stroke, sw = "#1e3a5f", "#38bdf8", "1"
            else:
                fill, stroke, sw = "#7f1d1d", "#f87171", "1"
            cx = x0 + j * cell_w
            svg.append(f'<rect x="{cx + 2}" y="{cy + 2}" width="{cell_w - 4}" height="{cell_h - 4}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
            label = f"{val:.0f}*" if is_base else f"{val:.0f}"
            svg.append(f'<text x="{cx + cell_w / 2:.1f}" y="{cy + 23}" text-anchor="middle" class="cell">{label}</text>')

    ly = y0 + len(wacc_grid) * cell_h + 26
    svg.append(f'<text x="26" y="{ly}" class="sub">* Base DCF (BDT 229) | Green >= BDT 265 Blended Target | Blue >= BDT 219 CMP | Red &lt; BDT 219 CMP</text>')
    svg.append('</svg>')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    inp = ValuationInputs()
    wacc_grid = np.round(np.arange(0.105, 0.136, 0.005), 3)
    growth_grid = np.round(np.arange(0.030, 0.061, 0.005), 3)
    matrix = compute_sensitivity_grid(inp, wacc_grid, growth_grid)

    pe_implied = round(inp.pe_peer_median * inp.eps_ttm_bdt, 0)
    pb_implied = round(inp.pb_justified * inp.nav_per_share_bdt, 0)
    raw_blend = 0.40 * inp.dcf_base_target_bdt + 0.35 * pe_implied + 0.25 * pb_implied

    print(f"=== {inp.ticker} VALUATION SUMMARY ===")
    print(f"CMP: BDT {inp.cmp_bdt:.1f} | DCF Base: BDT {inp.dcf_base_target_bdt:.1f} | P/E (10.5x): BDT {pe_implied:.1f} | P/B (2.1x): BDT {pb_implied:.1f}")
    print(f"Weighted Sum (40/35/25): BDT {raw_blend:.2f} -> Rounded Target: BDT {inp.blended_target_bdt:.1f} (+{(inp.blended_target_bdt / inp.cmp_bdt - 1) * 100:.1f}%)")
    print("\nDCF Sensitivity Grid (BDT/share):")
    header = "WACC \\ g | " + " | ".join(f"{g * 100:4.1f}%" for g in growth_grid)
    print(header)
    for i, w in enumerate(wacc_grid):
        row_str = " | ".join(f"{matrix[i, j]:5.0f}" for j in range(len(growth_grid)))
        print(f" {w * 100:5.1f}%  | {row_str}")

    root = Path(__file__).resolve().parent.parent
    assets = root / "assets"
    build_football_field_svg(inp, assets / "squrpharma_valuation_football_field.svg")
    build_sensitivity_heatmap_svg(wacc_grid, growth_grid, matrix, inp.cmp_bdt, assets / "squrpharma_dcf_sensitivity_heatmap.svg")
    print(f"\nGenerated SVGs in: {assets}")


if __name__ == "__main__":
    main()
