"""DSE Tier-1 Commercial Banking Equity Research & Intrinsic Valuation Engine.

Values four leading Dhaka Stock Exchange (DSE) Private Commercial Banks:
  1. BRAC Bank PLC (DSE: BRACBANK)
  2. The City Bank PLC (DSE: CITYBANK)
  3. Eastern Bank PLC (DSE: EBL)
  4. Prime Bank PLC (DSE: PRIMEBANK)

Institutional Banking Valuation Framework (Equity-Basis):
  Because customer deposits represent core operating funding rather than non-operating
  corporate debt, EV/EBITDA and Unlevered FCFF are inapplicable to commercial banks.
  This engine implements a three-pillar intrinsic valuation blend:
    - 45% 5-Year Explicit Equity DCF (FCFE / Capital-Adjusted Distributable Cash Flow)
    - 35% Residual Income Model (Excess Return over CAPM Cost of Equity on BVPS)
    - 20% Conservative Forward Target P/E Multiple
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


@dataclass(frozen=True)
class BankInputs:
    """Grounded FY2025/9M-2026 baseline metrics and explicit 5-year assumptions."""

    ticker: str
    name: str
    cmp_bdt: float
    range_52w: str
    base_eps_bdt: float       # Forward normalized base EPS (FY2025/TTM)
    reported_fy25_eps: float  # Audited FY2025 EPS
    nav_per_share_bdt: float  # Consolidated/Latest Q3 2026 NAV per share
    roe_pct: float            # Consolidated/Audited ROE (%)
    npl_pct: float            # Latest reported NPL ratio (%)
    crar_pct: float           # Basel III CRAR (%)
    dividend_fy25: str
    credit_rating: str
    beta: float
    eps_cagr: float           # 5-year conservative explicit EPS growth
    payout_ratio: float       # Sustainable cash retention discipline
    target_pe: float
    thesis_tag: str
    thesis_bullets: Tuple[str, ...]
    risks: Tuple[Tuple[str, str], ...]


BANKS: List[BankInputs] = [
    BankInputs(
        ticker="BRACBANK",
        name="BRAC Bank PLC",
        cmp_bdt=66.0,
        range_52w="BDT 60.0 - 89.6",
        base_eps_bdt=9.12,
        reported_fy25_eps=9.12,
        nav_per_share_bdt=56.40,
        roe_pct=19.70,
        npl_pct=2.27,
        crar_pct=15.80,
        dividend_fy25="15% Cash + 15% Stock (30%)",
        credit_rating="AAA / ST-1",
        beta=0.90,
        eps_cagr=0.130,
        payout_ratio=0.50,
        target_pe=8.8,
        thesis_tag="SME Franchise & bKash Digital Ecosystem Compounder",
        thesis_bullets=(
            "Sector-leading SME lending franchise paired with rapid CASA deposit mobilization.",
            "Strategic majority stake in bKash provides high-growth fee and digital ecosystem optionality.",
            "Consolidated FY25 EPS rose to BDT 9.12 (9M 2026: BDT 7.70) with 19.7% ROE and 2.27% NPL.",
            "Trailing P/E of 7.2x underprices sustainable >19% ROE compounding and AAA/ST-1 credit quality.",
        ),
        risks=(
            ("SME Asset-Quality Sensitivity", "Sustained macro slowdown could pressure MSME repayment cycles; mitigated by granular ticket sizing and 2.27% NPL base."),
            ("Treasury Yield Compression", "Lower Bangladesh T-bill/bond yields may normalize non-interest investment income; mitigated by core SME net interest spread."),
        ),
    ),
    BankInputs(
        ticker="CITYBANK",
        name="The City Bank PLC",
        cmp_bdt=30.2,
        range_52w="BDT 23.7 - 33.9",
        base_eps_bdt=7.10,
        reported_fy25_eps=8.71,
        nav_per_share_bdt=41.51,
        roe_pct=19.50,
        npl_pct=2.79,
        crar_pct=16.05,
        dividend_fy25="15% Cash + 15% Stock (30%)",
        credit_rating="AAA / ST-1 (CRAB)",
        beta=0.95,
        eps_cagr=0.095,
        payout_ratio=0.46,
        target_pe=6.2,
        thesis_tag="Cards/Retail Dominance & Below-Book Deep Value (0.73x P/B)",
        thesis_bullets=(
            "Undisputed market leader in Bangladesh credit cards (American Express) and Citytouch digital banking.",
            "Trading at just 0.73x P/B (BDT 30.2 vs NAV BDT 41.51) despite ~19.5% ROE and AAA/ST-1 rating.",
            "Asset quality tightened sharply (FY25 NPL 2.50% vs 3.72% FY24; Q3 2026: 2.79%) with 16.05% CRAR.",
            "Fee-income and retail card float insulate spreads across shifting Bangladesh Bank policy rate cycles.",
        ),
        risks=(
            ("Unsecured Retail & Card Credit Risk", "Higher inflation can raise consumer delinquency; mitigated by payroll-anchored underwriting and 16.05% CRAR buffer."),
            ("FX & Trade Finance Volatility", "LC settlement bottlenecks affect commission income; mitigated by diversified corporate and digital remittance flows."),
        ),
    ),
    BankInputs(
        ticker="EBL",
        name="Eastern Bank PLC",
        cmp_bdt=24.7,
        range_52w="BDT 22.2 - 28.9",
        base_eps_bdt=5.47,
        reported_fy25_eps=5.23,
        nav_per_share_bdt=32.63,
        roe_pct=16.70,
        npl_pct=2.80,
        crar_pct=15.49,
        dividend_fy25="25% Cash + 3% Stock (28%)",
        credit_rating="AAA / ST-1 (CRAB)",
        beta=0.85,
        eps_cagr=0.090,
        payout_ratio=0.52,
        target_pe=6.0,
        thesis_tag="Tier-1 Corporate Asset Quality & ~10% Cash Dividend Cushion",
        thesis_bullets=(
            "Benchmark corporate underwriting discipline (FY25 NPL 2.24%, Q1 2026: 2.80%) far below sector average.",
            "Strong cash return to shareholders: 25% Cash + 3% Stock dividend (~10.1% cash yield at CMP BDT 24.7).",
            "Consistent earnings compounding (FY25 EPS BDT 5.23; TTM BDT 5.47; 9M 2026 EPS up +15.2% YoY to BDT 4.10).",
            "Trades at 4.5x TTM P/E and 0.76x P/B despite AAA/ST-1 (CRAB) stability and 15.49% CRAR.",
        ),
        risks=(
            ("Corporate Concentration Risk", "Exposure to large industrial groups creates lumpy credit tail risk; mitigated by conservative collateral coverage and AAA tier-1 borrowers."),
            ("Dividend Tax & Capital Retention", "Generous cash payouts slow organic tier-1 equity growth; mitigated by healthy 15.49% CRAR above the 12.50% minimum."),
        ),
    ),
    BankInputs(
        ticker="PRIMEBANK",
        name="Prime Bank PLC",
        cmp_bdt=32.4,
        range_52w="BDT 27.3 - 36.1",
        base_eps_bdt=7.67,
        reported_fy25_eps=7.67,
        nav_per_share_bdt=41.09,
        roe_pct=20.85,
        npl_pct=2.73,
        crar_pct=18.07,
        dividend_fy25="25% Cash + 5% Stock (30%)",
        credit_rating="AAA / ST-1",
        beta=0.88,
        eps_cagr=0.095,
        payout_ratio=0.50,
        target_pe=6.0,
        thesis_tag="Sector-Leading 18.07% CRAR Fortress & 20.85% ROE Value Play",
        thesis_bullets=(
            "Highest Basel III capital buffer among covered peers at 18.07% CRAR (+557 bps over Bangladesh Bank 12.5% floor).",
            "NPL ratio declined sharply from 4.22% to 2.73% (FY25) while delivering 20.85% ROE and BDT 7.67 EPS.",
            "Trades at 4.2x P/E and 0.79x P/B (CMP BDT 32.4 vs NAV BDT 41.09) with 25% Cash + 5% Stock dividend.",
            "Excess tier-1 capital capacity allows credit expansion without dilutive equity issuance.",
        ),
        risks=(
            ("Net Interest Margin Compression", "Deposit competition in Dhaka raises cost of funds; mitigated by treasury portfolio yields and corporate supply-chain lending."),
            ("Systemic Sector Contagion", "Sentiment overhang from weak DSE peer banks compresses sector P/B multiples; mitigated by 18.07% CRAR solvency shield."),
        ),
    ),
]


RF_RATE = 0.115          # 10-Year Bangladesh Treasury Bond benchmark yield
ERP = 0.045              # Emerging Market Equity Risk Premium
TERMINAL_G = 0.055       # Long-run nominal GDP-anchored banking terminal growth


def cost_of_equity(beta: float, rf: float = RF_RATE, erp: float = ERP) -> float:
    return rf + beta * erp


def run_bank_valuation(
    bank: BankInputs,
    ke_override: float | None = None,
    g_override: float | None = None,
) -> Dict[str, object]:
    """Compute 5-year explicit FCFE DCF, Residual Income, Target P/E, and Blended Target."""
    ke = ke_override if ke_override is not None else cost_of_equity(bank.beta)
    g = g_override if g_override is not None else TERMINAL_G

    years = ["FY26E", "FY27E", "FY28E", "FY29E", "FY30E"]
    eps_path: List[float] = []
    bvps_path: List[float] = []
    fcfe_path: List[float] = []
    ri_path: List[float] = []
    pv_fcfe_path: List[float] = []
    pv_ri_path: List[float] = []

    bv_prev = bank.nav_per_share_bdt
    for idx in range(1, 6):
        # Slight growth moderation in outer years for institutional conservatism
        step_g = bank.eps_cagr * (1.0 - 0.04 * (idx - 1))
        prev_eps = bank.base_eps_bdt if idx == 1 else eps_path[-1]
        eps_t = prev_eps * (1.0 + step_g)

        # Bank retains (1 - payout_ratio) * EPS to maintain Basel III CRAR >= 15%
        retained_t = eps_t * (1.0 - bank.payout_ratio)
        fcfe_t = eps_t - retained_t  # Distributable Free Cash Flow to Equity
        bv_t = bv_prev + retained_t

        # Residual Income = Net Earnings - Capital Charge on Beginning Equity
        ri_t = eps_t - ke * bv_prev

        disc = (1.0 + ke) ** idx
        eps_path.append(eps_t)
        bvps_path.append(bv_t)
        fcfe_path.append(fcfe_t)
        ri_path.append(ri_t)
        pv_fcfe_path.append(fcfe_t / disc)
        pv_ri_path.append(ri_t / disc)
        bv_prev = bv_t

    spread = max(ke - g, 0.03)
    roe_terminal = min(max(eps_path[-1] / max(bvps_path[-1], 1.0), g + 0.05), 0.22)
    terminal_payout = max(bank.payout_ratio, min(0.75, 1.0 - g / roe_terminal))
    tv_fcfe = (eps_path[-1] * (1.0 + g) * terminal_payout) / spread
    pv_tv_fcfe = tv_fcfe / ((1.0 + ke) ** 5)
    dcf_fcfe_val = float(sum(pv_fcfe_path) + pv_tv_fcfe)

    # Residual Income Terminal Value assuming gradual fade to 50% persistence
    tv_ri = (ri_path[-1] * 0.50) / spread
    pv_tv_ri = tv_ri / ((1.0 + ke) ** 5)
    ri_val = float(bank.nav_per_share_bdt + sum(pv_ri_path) + pv_tv_ri)

    pe_val = float(bank.target_pe * bank.base_eps_bdt)
    blended_target = round(0.45 * dcf_fcfe_val + 0.35 * ri_val + 0.20 * pe_val, 1)
    upside_pct = round((blended_target / bank.cmp_bdt - 1.0) * 100.0, 1)
    rating = "BUY" if upside_pct >= 12.0 else ("HOLD" if upside_pct >= -5.0 else "SELL")

    return {
        "ticker": bank.ticker,
        "name": bank.name,
        "rating": rating,
        "cmp": bank.cmp_bdt,
        "ke": ke,
        "g": g,
        "years": years,
        "eps_path": eps_path,
        "bvps_path": bvps_path,
        "fcfe_path": fcfe_path,
        "ri_path": ri_path,
        "pv_fcfe_sum": float(sum(pv_fcfe_path)),
        "pv_tv_fcfe": float(pv_tv_fcfe),
        "dcf_fcfe_val": round(dcf_fcfe_val, 1),
        "ri_val": round(ri_val, 1),
        "pe_val": round(pe_val, 1),
        "blended_target": blended_target,
        "upside_pct": upside_pct,
        "trailing_pe": round(bank.cmp_bdt / bank.reported_fy25_eps, 2),
        "trailing_pb": round(bank.cmp_bdt / bank.nav_per_share_bdt, 2),
    }


def compute_bank_sensitivity(bank: BankInputs) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """5x5 Blended Target Sensitivity across Cost of Equity (Ke) and Terminal Growth (g)."""
    base_ke = cost_of_equity(bank.beta)
    ke_grid = np.round(np.array([base_ke - 0.015, base_ke - 0.0075, base_ke, base_ke + 0.0075, base_ke + 0.015]), 4)
    g_grid = np.array([0.040, 0.0475, 0.055, 0.0625, 0.070])
    mat = np.zeros((len(ke_grid), len(g_grid)))
    for i, ke in enumerate(ke_grid):
        for j, g in enumerate(g_grid):
            mat[i, j] = float(run_bank_valuation(bank, ke_override=float(ke), g_override=float(g))["blended_target"])
    return ke_grid, g_grid, mat


def build_banks_upside_svg(results: List[Dict[str, object]], out_path: Path) -> None:
    """Render SVG comparing CMP vs Blended Target Price & P/B-ROE Dislocation."""
    svg: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 420" width="980" height="420">',
        '<defs><style>',
        '.bg{fill:#0b132b}.card{fill:#131f3d;stroke:#24345c;stroke-width:1}',
        '.title{fill:#f8fafc;font:700 17px Segoe UI,Arial,sans-serif}',
        '.sub{fill:#94a3b8;font:12px Segoe UI,Arial,sans-serif}',
        '.lbl{fill:#e2e8f0;font:700 11.5px Segoe UI,Arial,sans-serif}',
        '.ax{fill:#94a3b8;font:10.5px Consolas,monospace}',
        '.val{fill:#f8fafc;font:700 11px Consolas,monospace}',
        '.grid{stroke:#1e293b;stroke-width:1;stroke-dasharray:3 3}',
        '</style></defs>',
        '<rect class="bg" width="980" height="420" rx="10"/>',
        '<text x="26" y="32" class="title">DSE TIER-1 COMMERCIAL BANKS - INTRINSIC VALUATION &amp; UPSIDE SUMMARY</text>',
        '<text x="26" y="52" class="sub">Blended Valuation: 45% 5-Yr Equity DCF (FCFE) + 35% Residual Income + 20% Target P/E  |  CAPM Rf = 11.5%, ERP = 4.5%</text>',
        '<rect class="card" x="24" y="70" width="520" height="326" rx="8"/>',
        '<text x="40" y="94" class="lbl">1. CURRENT MARKET PRICE (BDT) vs. 12M BLENDED TARGET PRICE (BDT)</text>',
    ]

    max_p = 95.0
    for tick in [20, 40, 60, 80]:
        tx = 128.0 + (tick / max_p) * 330.0
        svg.append(f'<line x1="{tx:.1f}" y1="112" x2="{tx:.1f}" y2="352" class="grid"/>')
        svg.append(f'<text x="{tx:.1f}" y="370" text-anchor="middle" class="ax">{tick}</text>')

    for idx, res in enumerate(results):
        y = 128 + idx * 58
        cmp_p = float(res["cmp"])  # type: ignore[arg-type]
        tgt_p = float(res["blended_target"])  # type: ignore[arg-type]
        up = float(res["upside_pct"])  # type: ignore[arg-type]
        w_cmp = (cmp_p / max_p) * 330.0
        w_tgt = (tgt_p / max_p) * 330.0
        svg.append(f'<text x="40" y="{y + 18}" class="lbl">{res["ticker"]}</text>')
        svg.append(f'<rect x="128" y="{y}" width="{w_cmp:.1f}" height="15" rx="3" fill="#38bdf8"/>')
        svg.append(f'<text x="{134 + w_cmp:.1f}" y="{y + 12}" class="ax">CMP {cmp_p:.1f}</text>')
        svg.append(f'<rect x="128" y="{y + 19}" width="{w_tgt:.1f}" height="15" rx="3" fill="#34d399"/>')
        up_str = f"+{up:.1f}%" if up >= 0 else f"{up:.1f}%"
        svg.append(f'<text x="{134 + w_tgt:.1f}" y="{y + 31}" class="val">Target {tgt_p:.1f} ({up_str})</text>')

    # Right panel: P/B vs ROE Value Dislocation
    svg.append('<rect class="card" x="562" y="70" width="394" height="326" rx="8"/>')
    svg.append('<text x="578" y="94" class="lbl">2. BELOW-BOOK VALUE DISLOCATION (P/B vs. ROE %)</text>')
    svg.append('<text x="578" y="112" class="sub">High-ROE (16%-21%) Tier-1 banks trading near 0.7x-1.2x Book</text>')

    pb_colors = ["#34d399", "#38bdf8", "#818cf8", "#f59e0b"]
    for idx, (bank, res) in enumerate(zip(BANKS, results)):
        y = 140 + idx * 60
        pb = float(res["trailing_pb"])  # type: ignore[arg-type]
        w_pb = min((pb / 1.4) * 145.0, 145.0)
        w_roe = min((bank.roe_pct / 25.0) * 145.0, 145.0)
        col = pb_colors[idx]
        svg.append(f'<text x="578" y="{y + 13}" class="lbl">{bank.ticker}  (P/E {res["trailing_pe"]}x)</text>')
        svg.append(f'<rect x="578" y="{y + 20}" width="{w_pb:.1f}" height="12" rx="3" fill="{col}" fill-opacity="0.85"/>')
        svg.append(f'<text x="{584 + w_pb:.1f}" y="{y + 30}" class="ax">P/B {pb:.2f}x</text>')
        svg.append(f'<rect x="765" y="{y + 20}" width="{w_roe:.1f}" height="12" rx="3" fill="#10b981"/>')
        svg.append(f'<text x="{771 + w_roe:.1f}" y="{y + 30}" class="ax">ROE {bank.roe_pct:.1f}%</text>')

    svg.append('</svg>')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(svg), encoding="utf-8")


def build_banks_prudential_svg(out_path: Path) -> None:
    """Render Asset Quality (NPL %) & Capital Adequacy (Basel III CRAR %) chart."""
    svg: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 370" width="980" height="370">',
        '<defs><style>',
        '.bg{fill:#0b132b}.card{fill:#131f3d;stroke:#24345c;stroke-width:1}',
        '.title{fill:#f8fafc;font:700 17px Segoe UI,Arial,sans-serif}',
        '.sub{fill:#94a3b8;font:12px Segoe UI,Arial,sans-serif}',
        '.lbl{fill:#e2e8f0;font:700 11.5px Segoe UI,Arial,sans-serif}',
        '.ax{fill:#94a3b8;font:10.5px Consolas,monospace}',
        '.val{fill:#f8fafc;font:700 11px Consolas,monospace}',
        '</style></defs>',
        '<rect class="bg" width="980" height="370" rx="10"/>',
        '<text x="26" y="32" class="title">DSE TIER-1 BANKS - ASSET QUALITY (NPL %) &amp; CAPITAL ADEQUACY (BASEL III CRAR %)</text>',
        '<text x="26" y="52" class="sub">All 4 covered banks maintain &lt;2.9% NPL and hold 300-557 bps CRAR buffers above Bangladesh Bank 12.50% floor</text>',
        '<rect class="card" x="24" y="70" width="456" height="276" rx="8"/>',
        '<text x="40" y="94" class="lbl">1. NON-PERFORMING LOAN (NPL %) - LOWER IS STRONGER</text>',
        '<rect class="card" x="500" y="70" width="456" height="276" rx="8"/>',
        '<text x="516" y="94" class="lbl">2. BASEL III CRAR (%) vs. 12.50% REGULATORY MINIMUM</text>',
    ]

    # CRAR threshold line at 12.5%
    crar_max = 22.0
    min_x = 612.0 + (12.5 / crar_max) * 280.0
    svg.append(f'<line x1="{min_x:.1f}" y1="115" x2="{min_x:.1f}" y2="316" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="5 3"/>')
    svg.append(f'<text x="{min_x + 4:.1f}" y="124" fill="#fcd34d" font-size="10.5" font-family="Consolas,monospace">BB Floor 12.5%</text>')

    for idx, bank in enumerate(BANKS):
        y = 138 + idx * 46
        w_npl = (bank.npl_pct / 5.0) * 260.0
        svg.append(f'<text x="40" y="{y + 15}" class="lbl">{bank.ticker}</text>')
        svg.append(f'<rect x="138" y="{y}" width="{w_npl:.1f}" height="20" rx="4" fill="#38bdf8"/>')
        svg.append(f'<text x="{144 + w_npl:.1f}" y="{y + 15}" class="val">{bank.npl_pct:.2f}%</text>')

        w_crar = (bank.crar_pct / crar_max) * 280.0
        svg.append(f'<text x="516" y="{y + 15}" class="lbl">{bank.ticker}</text>')
        svg.append(f'<rect x="612" y="{y}" width="{w_crar:.1f}" height="20" rx="4" fill="#34d399"/>')
        svg.append(f'<text x="{618 + w_crar:.1f}" y="{y + 15}" class="val">{bank.crar_pct:.2f}%</text>')

    svg.append('</svg>')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    results = [run_bank_valuation(b) for b in BANKS]
    print("=== DSE TIER-1 COMMERCIAL BANK EQUITY RESEARCH SUMMARY ===")
    for b, r in zip(BANKS, results):
        up_str = f"{float(r['upside_pct']):+.1f}%"
        print(
            f"{b.ticker:10s} [{r['rating']:4s}] | CMP: {b.cmp_bdt:5.1f} | Ke: {float(r['ke']):5.2%} | "
            f"DCF(45%): {float(r['dcf_fcfe_val']):5.1f} | RI(35%): {float(r['ri_val']):5.1f} | "
            f"P/E(20%): {float(r['pe_val']):5.1f} | Target: {float(r['blended_target']):5.1f} "
            f"({up_str}) | NPL: {b.npl_pct:.2f}% | CRAR: {b.crar_pct:.2f}%"
        )
    root = Path(__file__).resolve().parent.parent
    assets = root / "assets"
    build_banks_upside_svg(results, assets / "dse_banks_valuation_upside.svg")
    build_banks_prudential_svg(assets / "dse_banks_asset_quality_crar.svg")
    print(f"Generated bank SVGs in: {assets}")


if __name__ == "__main__":
    main()
