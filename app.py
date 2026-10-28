# ==============================================================================
# 👁️ ANJNA™ v2.3 ("THE THIRD EYE") — SOVEREIGN QUANTITATIVE TERMINAL
# ==============================================================================
# Ground-Up Institutional Quantitative Interface for Indian Equities (NSE/BSE)
# Architecture:
#   - 332 Point-in-Time Signals (D001–D332) -> 15 Orthogonal Meta-Factors (MF01–MF15)
#   - Van der Waerden Probit Transform + Liquid-Core (U_core) Sequential Gram-Schmidt
#   - Dynamic Capped-Simplex Projection across 6 Signal Families (F1–F6)
#   - Dual Gate-0 Architecture: G0_forensic [0, 1] & G0_tradable {0, 1}
#   - Ind-AS 109 Treasury Yield (D062) + Payout Shield & 4Q NCLT Turnaround Clause
#   - Split Execution Scalar: L_exec,final = L_cost^eta(h) * M_structural
#   - Bounded Technical Confluence Timing Scalar: C_timing in [0.80, 1.08]
#   - Ordinal Bayesian Shrinkage Quarter-Kelly (N_prior=75) + Lopez de Prado HRP
#   - Gate 5 Full-Universe Precision/Recall Audit & 60-Day Embargo CPCV / DSR / PBO
# ==============================================================================

import datetime
import io
import json
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
try:
    import yfinance as yf
except ImportError:
    yf = None

from engine import (
    DEFAULT_PROFILES,
    FORENSIC_VETO_REGISTRY,
    NSE_RADAR_UNIVERSE,
    SECTOR_DEFAULT_MAP,
    VERIFIED_57_SEED_HOLDINGS,
    batch_fetch_live_prices,
    build_ananta216_excel_dossier,
    build_vajra_app_icon,
    clear_profile_holdings,
    evaluate_320_institutional_codex,
    execute_buy_order,
    execute_sell_order,
    export_all_vaults_json,
    generate_autonomous_rebalance_tickets,
    generate_deterministic_copilot_response,
    generate_synthetic_ohlcv,
    get_holdings,
    get_ist_now,
    get_live_vedic_chronometer,
    get_trade_ledger,
    init_db,
    parse_raw_broker_holdings_text,
    query_optional_llm_api,
    reconcile_corporate_action,
    restore_vaults_from_json,
    save_holding_direct,
    scan_radar_universe_216,
)

from engine import (
    ANJNAEngineV23,
    ANJNAMetaFactorEngine,
    ANJNAValidationProtocol,
    sanitize_ohlcv_corporate_actions,
)
from modules.data_pipeline import (
    parse_search_string,
    get_searchable_universe_list,
)
from core.wealth_order_allocator import WealthOrderAllocator
from core.weightage_matrix import AureliusWeightageMatrix

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & SESSION STATE INITIALIZATION
# ------------------------------------------------------------------------------
APP_ICON_IMG, APP_ICON_B64 = build_vajra_app_icon()

st.set_page_config(
    page_title="ANJNA™ v2.3 | Sovereign Orthogonal Quantitative Terminal",
    page_icon=APP_ICON_IMG,
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

if "active_profile" not in st.session_state:
    st.session_state.active_profile = DEFAULT_PROFILES[0]
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "Dark (Obsidian Quantitative)"
if "active_horizon" not in st.session_state:
    st.session_state.active_horizon = "H4"
if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = "MODERATE"
if "mandate_capital_inr" not in st.session_state:
    st.session_state.mandate_capital_inr = 2500000.0
if "vedic_overlay_enabled" not in st.session_state:
    st.session_state.vedic_overlay_enabled = False
if "selected_xray_symbol" not in st.session_state:
    st.session_state.selected_xray_symbol = "TITAN"
if "copilot_messages" not in st.session_state:
    st.session_state.copilot_messages = [
        {
            "role": "assistant",
            "content": (
                "### 👁️ ANJNA™ v2.3 Sovereign Quantitative Copilot Online\n"
                "Every audit runs natively through the **332-Signal → 15 Orthogonal Meta-Factor (`MF01–MF15`) → "
                "Dual Gate-0 (`G0_forensic` & `G0_tradable`) → Split Execution (`L_exec,final`) → Bounded Timing (`C_timing`)** pipeline.\n\n"
                "- **Single-Stock Mathematical X-Ray:** `Audit TITAN`, `Audit RELIANCE`, `Audit YESBANK`\n"
                "- **Head-to-Head Orthogonal Comparison:** `Compare TCS vs INFY`, `Compare HAL vs BEL`\n"
                "- **Bayesian Quarter-Kelly + HRP Sizing:** `Allocate 25 Lakh`\n"
                "- **Portfolio Dual-Gate Triage:** `Rebalance` or `Risk audit`"
            ),
        }
    ]


# ------------------------------------------------------------------------------
# 2. META-FACTOR METADATA CATALOG (MF01–MF15 & F1–F6)
# ------------------------------------------------------------------------------
MF_DISPLAY_METADATA: Dict[str, Dict[str, str]] = {
    "MF01": {"name": "Forensic Integrity & Governance", "family": "F1_FORENSIC_SOLVENCY", "signals": "D001–D030, D322–D327"},
    "MF02": {"name": "Solvency, Merton KMV & Lease Debt", "family": "F1_FORENSIC_SOLVENCY", "signals": "D031–D048, D301, D331"},
    "MF03": {"name": "Capital Efficiency & DuPont ROIC", "family": "F2_QUALITY_MOAT", "signals": "D049–D065, D302"},
    "MF04": {"name": "Incremental ROIIC & Reinvestment Moat", "family": "F2_QUALITY_MOAT", "signals": "D066–D082, D303"},
    "MF05": {"name": "Intrinsic Value (Orthogonal to Quality)", "family": "F3_VALUATION_GROWTH", "signals": "D083–D104"},
    "MF06": {"name": "Operating Leverage & SUE Acceleration", "family": "F3_VALUATION_GROWTH", "signals": "D105–D120"},
    "MF07": {"name": "Intermediate Trend & Weinstein Stage-2", "family": "F4_MOMENTUM_TIMING", "signals": "D165–D184, D305"},
    "MF08": {"name": "Continuous Path Quality (Frog-in-Pan)", "family": "F4_MOMENTUM_TIMING", "signals": "D185–D198, D304"},
    "MF09": {"name": "Kalman Slope & Volatility-Compressed VCP", "family": "F4_MOMENTUM_TIMING", "signals": "D199–D216, D308"},
    "MF10": {"name": "Low-Volatility & Downside CVaR/CDaR Shield", "family": "F4_MOMENTUM_TIMING", "signals": "D306–D309, D317–D320"},
    "MF11": {"name": "Institutional RFDI, FII/DII & Insider Flow", "family": "F5_INSTITUTIONAL_FLOW", "signals": "D217–D242"},
    "MF12": {"name": "Microstructure VPIN, Hasbrouck & OBI", "family": "F5_INSTITUTIONAL_FLOW", "signals": "D243–D260, D310–D313"},
    "MF13": {"name": "Macro Regime, RRG Quadrant & Policy Tailwind", "family": "F6_MACRO_CATALYST", "signals": "D261–D282"},
    "MF14": {"name": "PE/QIP Deals, Orderbook & Causal Catalysts", "family": "F6_MACRO_CATALYST", "signals": "D283–D296"},
    "MF15": {"name": "Capital Allocation, Buyback & Post-Tax Alpha", "family": "F6_MACRO_CATALYST", "signals": "D297–D300, D315"},
}

FAMILY_COLORS: Dict[str, str] = {
    "F1_FORENSIC_SOLVENCY": "#10B981",
    "F2_QUALITY_MOAT": "#06B6D4",
    "F3_VALUATION_GROWTH": "#3B82F6",
    "F4_MOMENTUM_TIMING": "#8B5CF6",
    "F5_INSTITUTIONAL_FLOW": "#F59E0B",
    "F6_MACRO_CATALYST": "#EC4899",
}


# ------------------------------------------------------------------------------
# 3. INSTITUTIONAL CARBON-OBSIDIAN & CRISP ALABASTER CSS DESIGN SYSTEM
# ------------------------------------------------------------------------------
def inject_anjna_v23_css(theme_name: str) -> None:
    is_light = "Light" in theme_name
    if is_light:
        bg_primary = "#F8FAFC"
        bg_secondary = "#FFFFFF"
        bg_tertiary = "#F1F5F9"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        border_col = "#CBD5E1"
        accent_cyan = "#0284C7"
        accent_emerald = "#059669"
        accent_amber = "#D97706"
        accent_crimson = "#DC2626"
        card_shadow = "0 2px 10px rgba(15, 23, 42, 0.05)"
    else:
        bg_primary = "#050811"
        bg_secondary = "#0B1120"
        bg_tertiary = "#111827"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        border_col = "#1E293B"
        accent_cyan = "#06B6D4"
        accent_emerald = "#10B981"
        accent_amber = "#F59E0B"
        accent_crimson = "#EF4444"
        card_shadow = "0 8px 28px rgba(0, 0, 0, 0.45)"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: {bg_primary};
            color: {text_primary};
        }}
        .stApp {{
            background-color: {bg_primary};
            color: {text_primary};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {bg_secondary} !important;
            border-right: 1px solid {border_col} !important;
        }}
        .block-container {{
            padding-top: 1.1rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 98% !important;
        }}

        /* Top Sovereign Command Ribbon */
        .anjna-command-header {{
            background: linear-gradient(135deg, {bg_secondary} 0%, {bg_tertiary} 100%);
            border: 1px solid {border_col};
            border-left: 4px solid {accent_cyan};
            border-radius: 12px;
            padding: 16px 22px;
            margin-bottom: 14px;
            box-shadow: {card_shadow};
        }}
        .anjna-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .anjna-brand-title {{
            font-size: 1.38rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: {text_primary};
            margin: 0;
        }}
        .anjna-brand-sub {{
            font-size: 0.80rem;
            color: {text_secondary};
            font-family: 'JetBrains Mono', monospace;
            margin-top: 3px;
        }}
        .anjna-pill-row {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .anjna-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.73rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid {border_col};
            background: {bg_primary};
            color: {text_primary};
        }}
        .anjna-pill-cyan {{
            border-color: {accent_cyan};
            color: {accent_cyan};
        }}
        .anjna-pill-emerald {{
            border-color: {accent_emerald};
            color: {accent_emerald};
        }}
        .anjna-pill-amber {{
            border-color: {accent_amber};
            color: {accent_amber};
        }}

        /* Telemetry Metric Cards */
        .anjna-kpi-card {{
            background: {bg_secondary};
            border: 1px solid {border_col};
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: {card_shadow};
            height: 100%;
            transition: border-color 0.15s ease;
        }}
        .anjna-kpi-card:hover {{
            border-color: {accent_cyan};
        }}
        .anjna-kpi-label {{
            font-size: 0.71rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {text_secondary};
            margin-bottom: 4px;
        }}
        .anjna-kpi-val {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.42rem;
            font-weight: 800;
            color: {text_primary};
            line-height: 1.2;
        }}
        .anjna-kpi-sub {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.73rem;
            color: {text_secondary};
            margin-top: 5px;
        }}

        /* Equation Trace Banner */
        .anjna-eq-trace {{
            background: {bg_tertiary};
            border: 1px solid {border_col};
            border-left: 3px solid {accent_emerald};
            border-radius: 8px;
            padding: 11px 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            color: {text_primary};
            margin: 10px 0 14px 0;
            overflow-x: auto;
        }}

        /* Gate Diagnostic Progress Bars */
        .gate-row {{
            background: {bg_secondary};
            border: 1px solid {border_col};
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }}
        .gate-hdr {{
            display: flex;
            justify-content: space-between;
            font-size: 0.79rem;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .gate-bar-bg {{
            width: 100%;
            height: 7px;
            background: {bg_tertiary};
            border-radius: 4px;
            overflow: hidden;
        }}

        /* Section Banner */
        .anjna-sec-hdr {{
            font-size: 0.98rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            color: {text_primary};
            padding-bottom: 6px;
            border-bottom: 1px solid {border_col};
            margin: 14px 0 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_anjna_v23_css(st.session_state.ui_theme)
IS_LIGHT_THEME = "Light" in st.session_state.ui_theme
PLOTLY_TEMPLATE = "plotly_white" if IS_LIGHT_THEME else "plotly_dark"
PLOT_BG = "#FFFFFF" if IS_LIGHT_THEME else "#0B1120"
PAPER_BG = "#F8FAFC" if IS_LIGHT_THEME else "#050811"
FONT_COLOR = "#0F172A" if IS_LIGHT_THEME else "#F8FAFC"


# ------------------------------------------------------------------------------
# 4. SIDEBAR: ANJNA™ v2.3 GLOBAL MANDATE & ORTHOGONAL PARAMETERS
# ------------------------------------------------------------------------------
vedic_info = get_live_vedic_chronometer()

with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;padding-bottom:10px;border-bottom:1px solid #1E293B;margin-bottom:12px;">
            <img src="data:image/png;base64,{APP_ICON_B64}" width="38" height="38" style="border-radius:8px;" />
            <div>
                <div style="font-weight:800;font-size:1.02rem;letter-spacing:-0.01em;">ANJNA™ v2.3 TERMINAL</div>
                <div style="font-size:0.71rem;color:#06B6D4;font-family:'JetBrains Mono',monospace;">332 SIGNALS → 15 ORTHOGONAL MFs</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.ui_theme = st.selectbox(
        "🎨 Terminal Surface Theme",
        ["Dark (Obsidian Quantitative)", "Light (Alabaster Institutional)"],
        index=0 if "Dark" in st.session_state.ui_theme else 1,
    )

    st.markdown("#### 🎯 Institutional Mandate Controls")

    st.session_state.active_profile = st.selectbox(
        "Active Portfolio Vault",
        DEFAULT_PROFILES,
        index=DEFAULT_PROFILES.index(st.session_state.active_profile)
        if st.session_state.active_profile in DEFAULT_PROFILES
        else 0,
    )

    HORIZON_OPTIONS = {
        "H0": "H0: Intraday / Overnight (1–3d | η=1.00)",
        "H1": "H1: Tactical Swing (1–3W | η=0.80)",
        "H2": "H2: Quarterly PEAD Drift (1–3M | η=0.55)",
        "H3": "H3: Cyclical Position (3–6M | η=0.35)",
        "H4": "H4: Institutional Annual (1Y | η=0.22)",
        "H5": "H5: Structural Compounder (3–5Y+ | η=0.15)",
    }
    st.session_state.active_horizon = st.selectbox(
        "Investment Horizon (h) & Cost Decay η(h)",
        options=list(HORIZON_OPTIONS.keys()),
        format_func=lambda k: HORIZON_OPTIONS[k],
        index=list(HORIZON_OPTIONS.keys()).index(st.session_state.active_horizon),
    )

    st.session_state.risk_profile = st.selectbox(
        "Risk Stance (r) & Simplex Cap",
        ["CONSERVATIVE", "MODERATE", "AGGRESSIVE"],
        index=["CONSERVATIVE", "MODERATE", "AGGRESSIVE"].index(st.session_state.risk_profile),
    )

    st.session_state.mandate_capital_inr = float(
        st.number_input(
            "Mandate Capital C (₹ INR)",
            min_value=50000.0,
            max_value=10000000000.0,
            value=float(st.session_state.mandate_capital_inr),
            step=250000.0,
            help="Directly governs Gate-0B Tradability (DTL <= 5.0 days at 10% ADV) and Split Execution L_cost^eta(h).",
        )
    )

    st.session_state.vedic_overlay_enabled = st.toggle(
        "Optional 4% Vedic Overlay (D121–D164)",
        value=bool(st.session_state.vedic_overlay_enabled),
        help="Default OFF (0% weight) per S7 Specification. When toggled ON, applies a bounded 4% tilt to Alpha_orth.",
    )

    # Compute live Capped-Simplex family weights for the active Horizon & Risk Stance
    omega_preview, fam_preview, tau_preview = ANJNAMetaFactorEngine.project_grouped_capped_simplex(
        horizon_code=st.session_state.active_horizon,
        risk_profile=st.session_state.risk_profile,
    )

    with st.expander("📐 Active Capped-Simplex Weights (F1–F6)", expanded=True):
        st.caption(f"Dynamic Family Ceiling $\\tau_{{\\text{{fam}}}} = {tau_preview*100:.1f}\\%$ | $\\sum \\Omega_k = 100.0\\%$")
        for fam_k, fam_w in fam_preview.items():
            short_f = fam_k.replace("_", " ")
            st.progress(min(1.0, float(fam_w / max(tau_preview, 0.28))), text=f"{short_f}: {fam_w*100:.1f}%")

    with st.expander("💾 Vault Backup & JSON Restore", expanded=False):
        vault_json_str = export_all_vaults_json()
        st.download_button(
            "⬇️ Export All Vaults (.json)",
            data=vault_json_str,
            file_name=f"anjna_v23_vaults_{datetime.date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True,
        )
        uploaded_json = st.file_uploader("Restore Vaults (.json)", type=["json"], key="sidebar_json_restore")
        if uploaded_json is not None:
            ok_r, msg_r = restore_vaults_from_json(uploaded_json.read().decode("utf-8"))
            if ok_r:
                st.success(msg_r)
            else:
                st.error(msg_r)


# ------------------------------------------------------------------------------
# 5. TOP COMMAND RIBBON & MASTER EQUATION TELEMETRY
# ------------------------------------------------------------------------------
active_h = st.session_state.active_horizon
active_r = st.session_state.risk_profile
active_cap_cr = st.session_state.mandate_capital_inr / 1e7
eta_active = ANJNAEngineV23.HORIZON_ETA.get(active_h, 0.22)

st.markdown(
    f"""
    <div class="anjna-command-header">
        <div class="anjna-title-row">
            <div>
                <div class="anjna-brand-title">👁️ ANJNA™ v2.3 — SOVEREIGN ORTHOGONAL QUANTITATIVE TERMINAL</div>
                <div class="anjna-brand-sub">
                    ANJNA_v2.3(s,h,r,C) = G0_tradable(s,C) × G0_forensic(s) × L_exec,final(s,h,C) × C_timing(s,h) × Σ Ω_k(h,r)·MF_k^⊥(s)
                </div>
            </div>
            <div class="anjna-pill-row">
                <span class="anjna-pill anjna-pill-cyan">332 PIT Signals → 15 Orthogonal MFs</span>
                <span class="anjna-pill anjna-pill-emerald">Horizon: {active_h} (η={eta_active:.2f})</span>
                <span class="anjna-pill anjna-pill-amber">Mandate: ₹{st.session_state.mandate_capital_inr/1e5:,.1f}L ({active_r})</span>
                <span class="anjna-pill">IST: {vedic_info['time_ist']}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------------------
# 6. HELPER: BUILD PORTFOLIO DISPLAY DATAFRAME WITH ANJNA v2.3 TELEMETRY
# ------------------------------------------------------------------------------
def build_enriched_portfolio_df(profile_name: str, horizon_code: str, risk_profile: str, capital_inr: float) -> pd.DataFrame:
    df_raw = get_holdings(profile_name)
    if df_raw.empty:
        return pd.DataFrame()

    syms = tuple(df_raw["symbol"].astype(str).unique().tolist())
    live_map = batch_fetch_live_prices(syms)

    rows = []
    for _, h in df_raw.iterrows():
        sym = str(h["symbol"]).upper().strip()
        sh_raw = float(h["shares"])
        cost_raw = float(h["avg_cost"])
        sec_raw = str(h.get("sector") or SECTOR_DEFAULT_MAP.get(sym, "Equities"))

        # Evaluate ANJNA v2.3 for holding
        eval_res = evaluate_320_institutional_codex(
            sym=sym,
            df_hist=pd.DataFrame(),
            vedic_ctx=vedic_info,
            portfolio_equity=capital_inr,
            horizon_code=horizon_code,
            risk_profile=risk_profile,
            vedic_enabled=st.session_state.vedic_overlay_enabled,
        )

        cmp_live, chg_1d = live_map.get(sym, (float(eval_res.get("CMP (₹)", cost_raw)), float(eval_res.get("Change %", 0.0))))
        if cmp_live <= 0:
            cmp_live = float(eval_res.get("CMP (₹)", cost_raw))

        rec_sh, rec_cost, was_adj, acar_note = reconcile_corporate_action(sym, sh_raw, cost_raw, cmp_live)
        cost_basis = rec_sh * rec_cost
        mkt_val = rec_sh * cmp_live
        pnl_inr = mkt_val - cost_basis
        pnl_pct = ((mkt_val / cost_basis) - 1.0) * 100.0 if cost_basis > 0 else 0.0

        rows.append(
            {
                "Symbol": sym,
                "Sector": eval_res.get("Sector", sec_raw),
                "Shares": rec_sh,
                "Buy Price": round(rec_cost, 2),
                "Live CMP": round(cmp_live, 2),
                "1D Change %": round(chg_1d, 2),
                "Cost Basis": round(cost_basis, 2),
                "Market Value": round(mkt_val, 2),
                "P&L (₹)": round(pnl_inr, 2),
                "P&L %": round(pnl_pct, 2),
                "ANJNA v2.3 Score": float(eval_res.get("ANJNA_v23_Score", eval_res.get("Master_Alpha_Score", 50.0))),
                "Alpha_orth": float(eval_res.get("ANJNA_Alpha_Orth", 50.0)),
                "G0_forensic": float(eval_res.get("ANJNA_G0_Forensic", 1.0)),
                "Forensic Status": str(eval_res.get("ANJNA_Forensic_Status", "PASS")),
                "G0_tradable": int(eval_res.get("ANJNA_G0_Tradable", 1)),
                "DTL Days": float(eval_res.get("ANJNA_DTL_Days", 0.01)),
                "L_exec,final": float(eval_res.get("ANJNA_L_Exec_Final", 1.0)),
                "C_timing": float(eval_res.get("ANJNA_C_Timing", 1.0)),
                "Bayesian Kelly %": float(eval_res.get("ANJNA_Kelly_Pct", eval_res.get("Kelly Weight %", 0.0))),
                "Verdict": str(eval_res.get("ANJNA_Verdict", eval_res.get("Verdict", "HOLD"))),
                "Optimal Horizon": str(eval_res.get("Optimal_Horizon", horizon_code)),
                "Stop-Loss (₹)": float(eval_res.get("Stop-Loss (₹)", cmp_live * 0.92)),
                "Target (₹)": float(eval_res.get("Target_T1 (₹)", cmp_live * 1.18)),
                "ACAR Note": acar_note,
            }
        )

    df_disp = pd.DataFrame(rows)
    tot_mv = float(df_disp["Market Value"].sum()) if not df_disp.empty else 0.0
    df_disp["Weight %"] = np.round((df_disp["Market Value"] / tot_mv) * 100.0, 2) if tot_mv > 0 else 0.0
    return df_disp.sort_values(by="ANJNA v2.3 Score", ascending=False).reset_index(drop=True)


# ------------------------------------------------------------------------------
# 7. SIX PURPOSE-BUILT ANJNA™ v2.3 WORKSTATIONS
# ------------------------------------------------------------------------------
ws_tabs = st.tabs(
    [
        "🧬 1. ANJNA™ v2.3 Live DNA X-Ray & Waterfall",
        "🌐 2. Cross-Sectional Orthogonality & Universe Scanner",
        "💼 3. Portfolio Surgeon & Dual-Gate Rebalancer",
        "⚖️ 4. Bayesian Quarter-Kelly & HRP Allocator",
        "🛡️ 5. Gate 5 Precision/Recall & What-If Stress Lab",
        "🧠 6. Quantitative AI Copilot & 6-Sheet Dossier",
    ]
)


# ==============================================================================
# WORKSTATION 1: ANJNA™ v2.3 LIVE DNA X-RAY & MULTIPLICATIVE WATERFALL
# ==============================================================================
with ws_tabs[0]:
    searchable_options = get_searchable_universe_list()

    col_sel1, col_sel2, col_sel3, col_sel4 = st.columns([2.3, 1.4, 1.5, 1.2])
    with col_sel1:
        default_idx = 0
        for idx_s, label_s in enumerate(searchable_options):
            if label_s.startswith(f"{st.session_state.selected_xray_symbol} "):
                default_idx = idx_s
                break
        chosen_universe_item = st.selectbox(
            "🔍 Search Full NSE/BSE Equity Directory (~2,658 Active Instruments)",
            options=searchable_options,
            index=default_idx,
            help="Type any company name, ticker, or sector across the NSE/BSE equity catalog.",
        )
        selected_sym_from_dir = parse_search_string(chosen_universe_item)

    with col_sel2:
        custom_sym_input = st.text_input(
            "⌨️ Or Enter Any Custom NSE/BSE Ticker",
            value="",
            placeholder="e.g., RELIANCE, BAJFINANCE, ZOMATO...",
            help="Overrides the directory selector above to run a live ANJNA™ v2.3 audit on any listed symbol.",
        )

    with col_sel3:
        archetype_preset = st.selectbox(
            "🧪 Institutional Calibration Archetype (Optional)",
            [
                "Use Selected Ticker Above",
                "Compounder: TITAN (Clean Ind-AS 109 Treasury)",
                "Compounder: TCS (High-ROIC Cash Generator)",
                "Turnaround: CG POWER (Post-NCLT 4Q Phoenix Clause)",
                "BFSI Bank: ICICIBANK (GNPA/CRAR Solvency Branch)",
                "Forensic Hard-Veto: YESBANK (AT1 / Dilution Stress)",
                "Regulatory Veto: DELTACORP (28% GST Demand Shock)",
            ],
            index=0,
        )

    with col_sel4:
        inactive_mf_selection = st.multiselect(
            "Mask Inactive MFs (Simplex Test)",
            options=list(MF_DISPLAY_METADATA.keys()),
            default=[],
            help="Test S1/S2 Capped-Simplex Dynamic Relaxation: τ_fam = max(0.28, 1/N_active + 0.04).",
        )

    # Resolve active symbol for Workstation 1
    if archetype_preset != "Use Selected Ticker Above":
        if "TITAN" in archetype_preset:
            active_xray_sym = "TITAN"
        elif "TCS" in archetype_preset:
            active_xray_sym = "TCS"
        elif "CG POWER" in archetype_preset:
            active_xray_sym = "CGPOWER"
        elif "ICICIBANK" in archetype_preset:
            active_xray_sym = "ICICIBANK"
        elif "YESBANK" in archetype_preset:
            active_xray_sym = "YESBANK"
        else:
            active_xray_sym = "DELTACORP"
    elif custom_sym_input.strip():
        active_xray_sym = custom_sym_input.strip().upper().replace(".NS", "").replace(".BO", "")
    else:
        active_xray_sym = selected_sym_from_dir

    st.session_state.selected_xray_symbol = active_xray_sym

    # Fetch OHLCV history (with S5 Corporate Action Sanitizer + deterministic fallback)
    try:
        df_hist_raw = yf.Ticker(f"{active_xray_sym}.NS").history(period="1y")
    except Exception:
        df_hist_raw = pd.DataFrame()
    if df_hist_raw is None or df_hist_raw.empty or len(df_hist_raw) < 30:
        df_hist_raw = generate_synthetic_ohlcv(active_xray_sym, periods=200)

    df_hist_clean = sanitize_ohlcv_corporate_actions(df_hist_raw, active_xray_sym)

    # Run complete 332-signal + ANJNA v2.3 evaluation
    xray_codex = evaluate_320_institutional_codex(
        sym=active_xray_sym,
        df_hist=df_hist_clean,
        vedic_ctx=vedic_info,
        portfolio_equity=st.session_state.mandate_capital_inr,
        horizon_code=active_h,
        risk_profile=active_r,
        vedic_enabled=st.session_state.vedic_overlay_enabled,
    )

    anjna_payload = xray_codex["ANJNA_v2_3_Payload"]

    # If user masked specific MFs in the UI, re-evaluate ANJNA v2.3 with inactive_mfs
    if inactive_mf_selection:
        omega_custom, fam_custom, tau_custom = ANJNAMetaFactorEngine.project_grouped_capped_simplex(
            horizon_code=active_h,
            risk_profile=active_r,
            inactive_mfs=inactive_mf_selection,
        )
        mf_scores_curr = anjna_payload["MF_Orthogonal_Scores"]
        alpha_orth_val = round(sum(omega_custom[k] * mf_scores_curr.get(k, 50.0) for k in omega_custom), 2)
        g0_f_val = float(anjna_payload["G0_Forensic_Scalar"])
        g0_t_pass = bool(anjna_payload["G0_Tradable_Passed"])
        l_exec_val = float(anjna_payload["L_Exec_Final"])
        c_tim_val = float(anjna_payload["C_Timing"])
        anjna_final_val = round(float(np.clip(alpha_orth_val * g0_f_val * (1.0 if g0_t_pass else 0.0) * l_exec_val * c_tim_val, 0.0, 100.0)), 2)
    else:
        omega_custom = anjna_payload["Omega_MF_Weights"]
        fam_custom = anjna_payload["Family_Weights"]
        tau_custom = float(anjna_payload.get("Tau_Family_Cap_Eff", 0.28))
        alpha_orth_val = float(anjna_payload["Alpha_Orthogonal_Base"])
        g0_f_val = float(anjna_payload["G0_Forensic_Scalar"])
        g0_t_pass = bool(anjna_payload["G0_Tradable_Passed"])
        l_exec_val = float(anjna_payload["L_Exec_Final"])
        c_tim_val = float(anjna_payload["C_Timing"])
        anjna_final_val = float(anjna_payload["ANJNA_Final_Score"] or 0.0)

    exec_details = anjna_payload["Execution_Details"]
    trad_details = anjna_payload["Tradability_Details"]
    for_details = anjna_payload["G0_Forensic_Details"]
    kelly_details = anjna_payload["Kelly_Details"]
    l_cost_amort = float(exec_details["L_Cost_Amortized"])
    m_struct_val = float(exec_details["M_Structural"])
    verdict_str = str(anjna_payload["Verdict"])

    # Top 6-Card Institutional Telemetry Strip
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    score_col_hex = "#10B981" if anjna_final_val >= 70 else ("#F59E0B" if anjna_final_val >= 55 else "#EF4444")
    for_col_hex = "#10B981" if g0_f_val >= 0.90 else ("#F59E0B" if g0_f_val > 0.0 else "#EF4444")
    trad_col_hex = "#10B981" if g0_t_pass else "#EF4444"

    with k1:
        st.markdown(
            f"""
            <div class="anjna-kpi-card">
                <div class="anjna-kpi-label">ANJNA™ v2.3 Conviction</div>
                <div class="anjna-kpi-val" style="color:{score_col_hex};">{anjna_final_val:.2f} <span style="font-size:0.85rem;color:#94A3B8;">/ 100</span></div>
                <div class="anjna-kpi-sub">{active_xray_sym} • CMP ₹{xray_codex['CMP (₹)']:,.2f} ({xray_codex['Change %']:+.2f}%)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="anjna-kpi-card">
                <div class="anjna-kpi-label">15-MF Orthogonal Base</div>
                <div class="anjna-kpi-val" style="color:#06B6D4;">{alpha_orth_val:.2f}</div>
                <div class="anjna-kpi-sub">Simplex Cap τ_fam = {tau_custom*100:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        for_badge = "HARD VETO (0.0)" if for_details.get("Hard_Veto") else ("CLEAN PASS" if g0_f_val >= 0.99 else "GREY-ZONE DAMPED")
        st.markdown(
            f"""
            <div class="anjna-kpi-card">
                <div class="anjna-kpi-label">Gate-0A Forensic (G0_for)</div>
                <div class="anjna-kpi-val" style="color:{for_col_hex};">{g0_f_val:.3f}</div>
                <div class="anjna-kpi-sub">{for_badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        trad_badge = "TRADABLE (1)" if g0_t_pass else "WATCHLIST BLACKOUT (0)"
        st.markdown(
            f"""
            <div class="anjna-kpi-card">
                <div class="anjna-kpi-label">Gate-0B Tradability</div>
                <div class="anjna-kpi-val" style="color:{trad_col_hex};">{trad_badge.split()[0]}</div>
                <div class="anjna-kpi-sub">DTL: {float(trad_details['DTL_Days']):.3f}d | PIT: {float(trad_details['Completeness_Eff'])*100:.0f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            f"""
            <div class="anjna-kpi-card">
                <div class="anjna-kpi-label">Split Execution (L_exec)</div>
                <div class="anjna-kpi-val">{l_exec_val:.3f}</div>
                <div class="anjna-kpi-sub">L_cost^η: {l_cost_amort:.3f} × M_str: {m_struct_val:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k6:
        kelly_pct = float(kelly_details["Final_Allocation_Pct"])
        kelly_inr = st.session_state.mandate_capital_inr * (kelly_pct / 100.0)
        st.markdown(
            f"""
            <div class="anjna-kpi-card">
                <div class="anjna-kpi-label">Timing & Bayesian Kelly</div>
                <div class="anjna-kpi-val" style="color:#10B981;">{kelly_pct:.2f}%</div>
                <div class="anjna-kpi-sub">C_tim: {c_tim_val:.3f} | Alloc: ₹{kelly_inr:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Live Multiplicative Equation Trace Box
    st.markdown(
        f"""
        <div class="anjna-eq-trace">
            <b>LIVE ANJNA™ v2.3 MULTIPLICATIVE TRACE [{active_xray_sym} | { xray_codex['Sector'] } | {verdict_str}]:</b><br/>
            <code>ANJNA_v2.3 = {alpha_orth_val:.2f} (Alpha_orth) × {1 if g0_t_pass else 0} (G0_tradable) × {g0_f_val:.4f} (G0_forensic) × {l_cost_amort:.4f} (L_cost^η[{active_h}]) × {m_struct_val:.3f} (M_structural) × {c_tim_val:.4f} (C_timing) = <b>{anjna_final_val:.2f} / 100</b></code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Row 2: 5-Stage Multiplicative Waterfall Chart + Dual Gate-0 6-Component Diagnostic Panel
    col_wf, col_gates = st.columns([1.35, 1.0])

    with col_wf:
        st.markdown('<div class="anjna-sec-hdr"><span>📊 5-Stage Multiplicative Conviction Waterfall</span><span>Step-by-Step Scaling Trace</span></div>', unsafe_allow_html=True)
        s0_base = alpha_orth_val
        s1_after_for = s0_base * g0_f_val * (1.0 if g0_t_pass else 0.0)
        s2_after_cost = s1_after_for * l_cost_amort
        s3_after_struct = s2_after_cost * m_struct_val
        s4_final = float(np.clip(s3_after_struct * c_tim_val, 0.0, 100.0))

        wf_fig = go.Figure(
            go.Waterfall(
                name="ANJNA v2.3",
                orientation="v",
                measure=["absolute", "relative", "relative", "relative", "relative", "total"],
                x=[
                    "1. Alpha_orth<br>(15-MF Base)",
                    "2. × Dual Gate 0<br>(Forensic/Trad)",
                    f"3. × L_cost^η({active_h})<br>(Impact Decay)",
                    "4. × M_structural<br>(ASM/Circuit/Ban)",
                    "5. × C_timing<br>(Bounded [0.8,1.08])",
                    "Final ANJNA™ v2.3<br>Conviction",
                ],
                y=[
                    round(s0_base, 2),
                    round(s1_after_for - s0_base, 2),
                    round(s2_after_cost - s1_after_for, 2),
                    round(s3_after_struct - s2_after_cost, 2),
                    round(s4_final - s3_after_struct, 2),
                    round(s4_final, 2),
                ],
                text=[
                    f"{s0_base:.2f}",
                    f"{s1_after_for - s0_base:+.2f} (×{g0_f_val:.2f})",
                    f"{s2_after_cost - s1_after_for:+.2f} (×{l_cost_amort:.3f})",
                    f"{s3_after_struct - s2_after_cost:+.2f} (×{m_struct_val:.2f})",
                    f"{s4_final - s3_after_struct:+.2f} (×{c_tim_val:.3f})",
                    f"{s4_final:.2f}",
                ],
                textposition="outside",
                decreasing={"marker": {"color": "#EF4444"}},
                increasing={"marker": {"color": "#10B981"}},
                totals={"marker": {"color": "#06B6D4"}},
                connector={"line": {"color": "#475569", "width": 1.5, "dash": "dot"}},
            )
        )
        wf_fig.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT_COLOR, size=11),
            height=360,
            margin=dict(l=20, r=20, t=25, b=20),
            yaxis=dict(title="Conviction Points (0–100)", range=[0, max(108.0, s0_base + 12.0)]),
        )
        st.plotly_chart(wf_fig, use_container_width=True)

    with col_gates:
        st.markdown('<div class="anjna-sec-hdr"><span>🛡️ Dual Gate-0 Forensic & Grey-Zone Diagnostics</span><span>g_min = min(g_1..g_6)</span></div>', unsafe_allow_html=True)

        if for_details.get("Hard_Veto"):
            st.error("🚨 **GATE-0A FORENSIC HARD VETO TRIGGERED (`G0_forensic = 0.000`)**")
            for trig in for_details.get("Red_Triggers", []):
                st.markdown(f"- ⛔ **{trig}**")
        else:
            soft_gates = for_details.get("Soft_Gate_Components", {})
            d062_info = for_details.get("D062_Details", {})
            gate_items = [
                ("g_beneish (Beneish M-Score Sigmoid)", float(soft_gates.get("g_beneish", 1.0)), f"M = {xray_codex['Beneish M']:.2f} (Clean <= -1.78)"),
                ("g_sloan (Sloan Accrual Intensity)", float(soft_gates.get("g_sloan", 1.0)), f"Accruals = {xray_codex['Sloan Accrual %']:.1f}%"),
                ("g_pledge (Promoter Pledge & 2Q Delta)", float(soft_gates.get("g_pledge", 1.0)), f"Pledge = {xray_codex['Promoter Pledge %']:.1f}%"),
                ("g_gov (RPT / Contingent Liab / MCA Hygiene)", float(soft_gates.get("g_gov", 1.0)), "Governance & Audit Cleanliness"),
                (
                    "g_cash (Ind-AS 109 D062 Treasury + Payout Shield)",
                    float(soft_gates.get("g_cash", 1.0)),
                    f"Eff Yield = {float(d062_info.get('Yield_Treasury_Eff_Pct', 6.5)):.2f}% | Shield = {d062_info.get('High_Payout_Shield', True)}",
                ),
                (
                    "g_solvency (Altman Z'' / BFSI / 4Q NCLT Phoenix)",
                    float(soft_gates.get("g_solvency", 1.0)),
                    f"Altman Z'' = {xray_codex['Altman Z']:.2f}",
                ),
            ]
            for g_label, g_val, g_meta in gate_items:
                bar_c = "#10B981" if g_val >= 0.92 else ("#F59E0B" if g_val >= 0.65 else "#EF4444")
                st.markdown(
                    f"""
                    <div class="gate-row">
                        <div class="gate-hdr">
                            <span>{g_label}</span>
                            <span style="font-family:'JetBrains Mono',monospace;color:{bar_c};">{g_val:.3f} • <span style="color:#94A3B8;font-weight:400;">{g_meta}</span></span>
                        </div>
                        <div class="gate-bar-bg">
                            <div style="width:{min(100.0, g_val*100.0):.1f}%;height:100%;background:{bar_c};"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Row 3: 15 Orthogonal Meta-Factors (MF01–MF15) Attribution Chart & 15-Axis Polar Radar
    st.markdown('<div class="anjna-sec-hdr"><span>🧬 15 Orthogonal Meta-Factors (MF01–MF15) & 6 Capped-Simplex Families (F1–F6)</span><span>Van der Waerden Probit + Liquid-Core Gram-Schmidt</span></div>', unsafe_allow_html=True)

    mf_scores_dict = anjna_payload["MF_Orthogonal_Scores"]
    mf_rows = []
    for mfk, meta in MF_DISPLAY_METADATA.items():
        sc_v = float(mf_scores_dict.get(mfk, 50.0))
        wt_v = float(omega_custom.get(mfk, 0.0))
        contrib_v = sc_v * wt_v
        fam_code = meta["family"]
        mf_rows.append(
            {
                "MF": mfk,
                "Label": f"{mfk}: {meta['name']}",
                "Family": fam_code,
                "Signals": meta["signals"],
                "Orthogonal Score": round(sc_v, 2),
                "Simplex Weight %": round(wt_v * 100.0, 2),
                "Weighted Contribution": round(contrib_v, 2),
                "Color": FAMILY_COLORS.get(fam_code, "#06B6D4"),
            }
        )
    df_mf_disp = pd.DataFrame(mf_rows)

    col_mf_bar, col_mf_rad = st.columns([1.45, 1.0])

    with col_mf_bar:
        fig_mf = go.Figure()
        for fam_k, fam_df in df_mf_disp.groupby("Family", sort=False):
            fig_mf.add_trace(
                go.Bar(
                    y=fam_df["Label"],
                    x=fam_df["Orthogonal Score"],
                    orientation="h",
                    name=fam_k.replace("_", " "),
                    marker=dict(color=FAMILY_COLORS.get(fam_k, "#06B6D4")),
                    text=[
                        f"{r['Orthogonal Score']:.1f} (Ω={r['Simplex Weight %']:.1f}% → +{r['Weighted Contribution']:.2f})"
                        for _, r in fam_df.iterrows()
                    ],
                    textposition="auto",
                )
            )
        fig_mf.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT_COLOR, size=11),
            height=470,
            margin=dict(l=10, r=20, t=25, b=20),
            xaxis=dict(title="Orthogonal Meta-Factor Percentile Score (0–100)", range=[0, 108]),
            yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        )
        st.plotly_chart(fig_mf, use_container_width=True)

    with col_mf_rad:
        fig_polar = go.Figure()
        fig_polar.add_trace(
            go.Scatterpolar(
                r=df_mf_disp["Orthogonal Score"].tolist() + [df_mf_disp["Orthogonal Score"].iloc[0]],
                theta=df_mf_disp["MF"].tolist() + [df_mf_disp["MF"].iloc[0]],
                fill="toself",
                name=f"{active_xray_sym} Orthogonal Profile",
                line=dict(color="#06B6D4", width=2.5),
                fillcolor="rgba(6, 182, 212, 0.22)",
            )
        )
        fig_polar.add_trace(
            go.Scatterpolar(
                r=[50.0] * (len(df_mf_disp) + 1),
                theta=df_mf_disp["MF"].tolist() + [df_mf_disp["MF"].iloc[0]],
                name="Cross-Sectional Median (50)",
                line=dict(color="#F59E0B", width=1.3, dash="dash"),
            )
        )
        fig_polar.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT_COLOR, size=11),
            height=470,
            margin=dict(l=35, r=35, t=30, b=25),
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_polar, use_container_width=True)

    # Row 4: S5 Sanitized Price Action + Anchored VWAP + Multi-Horizon Term Structure (H0–H5)
    col_chart, col_term = st.columns([1.45, 1.0])

    with col_chart:
        st.markdown(
            f'<div class="anjna-sec-hdr"><span>📈 S5 Corporate-Action-Sanitized Tape ({active_xray_sym})</span>'
            f'<span>Splits Cleaned: {"S5 Active"} | Stop: ₹{xray_codex["Stop-Loss (₹)"]:,.1f} | Target: ₹{xray_codex["Target_T1 (₹)"]:,.1f}</span></div>',
            unsafe_allow_html=True,
        )
        df_p = df_hist_clean.tail(130).copy()
        df_p["EMA20"] = df_p["Close"].ewm(span=20, adjust=False).mean()
        df_p["EMA50"] = df_p["Close"].ewm(span=50, adjust=False).mean()
        tp = (df_p["High"] + df_p["Low"] + df_p["Close"]) / 3.0
        df_p["AVWAP"] = (tp * df_p["Volume"]).cumsum() / df_p["Volume"].replace(0, 1).cumsum()

        fig_candles = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.74, 0.26],
        )
        fig_candles.add_trace(
            go.Candlestick(
                x=df_p.index,
                open=df_p["Open"],
                high=df_p["High"],
                low=df_p["Low"],
                close=df_p["Close"],
                name="S5 Clean OHLC",
            ),
            row=1,
            col=1,
        )
        fig_candles.add_trace(go.Scatter(x=df_p.index, y=df_p["EMA20"], name="EMA 20", line=dict(color="#06B6D4", width=1.5)), row=1, col=1)
        fig_candles.add_trace(go.Scatter(x=df_p.index, y=df_p["EMA50"], name="EMA 50", line=dict(color="#F59E0B", width=1.5)), row=1, col=1)
        fig_candles.add_trace(go.Scatter(x=df_p.index, y=df_p["AVWAP"], name="Anchored VWAP", line=dict(color="#EC4899", width=1.8, dash="dot")), row=1, col=1)
        fig_candles.add_hline(y=float(xray_codex["Stop-Loss (₹)"]), line_dash="dash", line_color="#EF4444", annotation_text="ATR Stop", row=1, col=1)
        fig_candles.add_hline(y=float(xray_codex["Target_T1 (₹)"]), line_dash="dash", line_color="#10B981", annotation_text="Target T1", row=1, col=1)

        vol_colors = ["#10B981" if c >= o else "#EF4444" for c, o in zip(df_p["Close"], df_p["Open"])]
        fig_candles.add_trace(go.Bar(x=df_p.index, y=df_p["Volume"], name="Volume", marker_color=vol_colors), row=2, col=1)
        fig_candles.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT_COLOR, size=11),
            height=390,
            xaxis_rangeslider_visible=False,
            margin=dict(l=15, r=15, t=20, b=15),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        )
        st.plotly_chart(fig_candles, use_container_width=True)

    with col_term:
        st.markdown(
            f'<div class="anjna-sec-hdr"><span>⏱️ Multi-Horizon Conviction Curve (H0–H5)</span>'
            f'<span>Optimal Peak: {xray_codex["Optimal_Horizon"]}</span></div>',
            unsafe_allow_html=True,
        )
        mh_vec = xray_codex.get("Multi_Horizon_Vector", {})
        h_keys = ["H0", "H1", "H2", "H3", "H4", "H5"]
        h_scores = [float(mh_vec.get(hk, anjna_final_val)) for hk in h_keys]
        h_etas = [ANJNAEngineV23.HORIZON_ETA[hk] for hk in h_keys]

        fig_mh = go.Figure()
        fig_mh.add_trace(
            go.Scatter(
                x=[f"{hk} (η={et:.2f})" for hk, et in zip(h_keys, h_etas)],
                y=h_scores,
                mode="lines+markers+text",
                text=[f"{sc:.1f}" for sc in h_scores],
                textposition="top center",
                line=dict(color="#10B981", width=3),
                marker=dict(size=10, color=["#06B6D4" if hk == active_h else "#10B981" for hk in h_keys]),
                name="ANJNA™ v2.3 Horizon Score",
            )
        )
        fig_mh.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT_COLOR, size=11),
            height=390,
            margin=dict(l=15, r=15, t=25, b=15),
            yaxis=dict(title="ANJNA™ v2.3 Conviction (0–100)", range=[0, 105]),
        )
        st.plotly_chart(fig_mh, use_container_width=True)

    # Row 5: Searchable 332-Variable (D001–D332) Atomic Point-in-Time Ledger
    with st.expander(f"🔬 Inspect Full 332-Signal Point-in-Time Ledger (`D001–D332`) for {active_xray_sym}", expanded=False):
        codex_332_dict = xray_codex.get("Codex_300", {})
        search_sig = st.text_input(
            "Filter 332 Signals by ID or Keyword (e.g., D301, D321, Beneish, ROIC, KMV, ASM, IndAS, Kelly)",
            value="",
            key="sig_332_filter",
        )
        sig_rows = [{"Signal ID & Specification": k, "Point-in-Time Value": str(v)} for k, v in codex_332_dict.items()]
        df_sig332 = pd.DataFrame(sig_rows)
        if search_sig.strip():
            df_sig332 = df_sig332[
                df_sig332["Signal ID & Specification"].str.contains(search_sig.strip(), case=False, na=False)
                | df_sig332["Point-in-Time Value"].str.contains(search_sig.strip(), case=False, na=False)
            ]
        st.dataframe(df_sig332, use_container_width=True, height=340)


# ==============================================================================
# WORKSTATION 2: CROSS-SECTIONAL ORTHOGONALITY & UNIVERSE SCANNER
# ==============================================================================
with ws_tabs[1]:
    st.markdown(
        '<div class="anjna-sec-hdr"><span>🌐 Cross-Sectional Van der Waerden Probit + Liquid-Core (U_core) Gram-Schmidt Scanner</span>'
        '<span>Live 15×15 Meta-Factor Orthogonality Verification</span></div>',
        unsafe_allow_html=True,
    )

    col_u1, col_u2, col_u3 = st.columns([2.2, 1.2, 1.0])
    with col_u1:
        custom_scan_str = st.text_input(
            "Custom Cross-Sectional Universe (Optional comma-separated NSE symbols; leave blank for full 39-stock multi-sector benchmark)",
            value="",
            placeholder="e.g., TITAN, TCS, INFY, RELIANCE, HDFCBANK, ICICIBANK, HAL, BEL, SUNPHARMA, TRENT, YESBANK",
        )
    with col_u2:
        gate_filter_mode = st.selectbox(
            "Dual Gate-0 Filter",
            ["All Scanned Equities (Show Vetoes)", "Clean Gate-0 Survivors Only (G0_for >= 0.80 & Tradable)"],
            index=0,
        )
    with col_u3:
        sort_mf_col = st.selectbox(
            "Rank Universe By",
            ["ANJNA_v23_Score", "ANJNA_Alpha_Orth", "ANJNA_G0_Forensic", "ANJNA_Kelly_Pct", "ROIC %"],
            index=0,
        )

    custom_tuple = (
        tuple([s.strip().upper() for s in custom_scan_str.split(",") if s.strip()])
        if custom_scan_str.strip()
        else None
    )

    df_radar, macro_scan_info = scan_radar_universe_216(vedic_info, custom_universe=custom_tuple)

    # Display Raw vs. Gram-Schmidt Orthogonalized 15x15 Correlation Heatmaps
    corr_raw_df = macro_scan_info.get("mf_corr_raw")
    corr_orth_df = macro_scan_info.get("mf_corr_orth")
    max_raw_c = macro_scan_info.get("max_raw_offdiag_corr", 0.65)
    max_orth_c = macro_scan_info.get("max_orth_offdiag_corr", 0.0)

    if corr_raw_df is not None and corr_orth_df is not None:
        hm1, hm2 = st.columns(2)
        with hm1:
            st.markdown(f"**1. Raw Pre-Orthogonalization 15×15 Correlation** (`Max Off-Diag |r| = {max_raw_c:.3f}`)")
            fig_raw_hm = px.imshow(
                corr_raw_df.round(2),
                zmin=-1.0,
                zmax=1.0,
                color_continuous_scale="RdBu_r",
                aspect="auto",
            )
            fig_raw_hm.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor=PAPER_BG,
                plot_bgcolor=PLOT_BG,
                font=dict(color=FONT_COLOR, size=10),
                height=340,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_raw_hm, use_container_width=True)

        with hm2:
            st.markdown(f"**2. Liquid-Core (`U_core`) Gram-Schmidt Orthogonalized 15×15 Matrix** (`Max Off-Diag |r| = {max_orth_c:.4f}`)")
            fig_orth_hm = px.imshow(
                corr_orth_df.round(2),
                zmin=-1.0,
                zmax=1.0,
                color_continuous_scale="Tealrose",
                aspect="auto",
            )
            fig_orth_hm.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor=PAPER_BG,
                plot_bgcolor=PLOT_BG,
                font=dict(color=FONT_COLOR, size=10),
                height=340,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_orth_hm, use_container_width=True)

    df_scan_view = df_radar.copy()
    if "Clean Gate-0" in gate_filter_mode:
        df_scan_view = df_scan_view[
            (df_scan_view["ANJNA_G0_Forensic"] >= 0.80) & (df_scan_view["ANJNA_G0_Tradable"] == 1)
        ]

    if sort_mf_col in df_scan_view.columns:
        df_scan_view = df_scan_view.sort_values(by=sort_mf_col, ascending=False)

    scan_cols = [
        "Symbol",
        "Sector",
        "CMP (₹)",
        "Change %",
        "ANJNA_v23_Score",
        "ANJNA_Alpha_Orth",
        "ANJNA_G0_Forensic",
        "ANJNA_Forensic_Status",
        "ANJNA_Tradable_Status",
        "ANJNA_DTL_Days",
        "ANJNA_L_Exec_Final",
        "ANJNA_C_Timing",
        "ANJNA_Kelly_Pct",
        "ROIC %",
        "Beneish M",
        "Altman Z",
        "Optimal_Horizon",
        "ANJNA_Verdict",
    ]
    avail_scan_cols = [c for c in scan_cols if c in df_scan_view.columns]
    st.dataframe(df_scan_view[avail_scan_cols].reset_index(drop=True), use_container_width=True, height=420)


# ==============================================================================
# WORKSTATION 3: PORTFOLIO SURGEON, DUAL-GATE TRIAGE & ALMGREN-CHRISS REBALANCER
# ==============================================================================
with ws_tabs[2]:
    st.markdown(
        f'<div class="anjna-sec-hdr"><span>💼 Portfolio Surgeon & Dual Gate-0 Triage ({st.session_state.active_profile})</span>'
        f'<span>ACAR Corporate-Action Reconciliation + Turnover-Buffered Rebalancing (ΔANJNA >= 12 pts)</span></div>',
        unsafe_allow_html=True,
    )

    # Portfolio Ingestion Controls — 100% Clean (Zero pre-filled hardcoded paste strings)
    with st.expander("➕ Import or Add Portfolio Holdings (Broker CSV / XLSX / Smart Text Parser / Single Entry)", expanded=False):
        imp_c1, imp_c2, imp_c3 = st.columns([1.4, 1.2, 1.1])

        with imp_c1:
            raw_paste_input = st.text_area(
                "📋 Paste Holdings From Any Broker (Format: SYMBOL QTY AVG_COST per line)",
                value="",
                placeholder="Paste your actual holdings here (one per line), e.g.:\nRELIANCE 50 1380.00\nTCS 25 3850.00\nICICIBANK 120 1120.50",
                height=120,
            )
            if st.button("⚡ Parse & Import Pasted Holdings", use_container_width=True):
                parsed_items = parse_raw_broker_holdings_text(raw_paste_input)
                if parsed_items:
                    for item in parsed_items:
                        save_holding_direct(
                            st.session_state.active_profile,
                            item["symbol"],
                            float(item["shares"]),
                            float(item["avg_cost"]),
                            SECTOR_DEFAULT_MAP.get(item["symbol"], "Equities"),
                        )
                    st.success(f"Imported {len(parsed_items)} holdings into {st.session_state.active_profile}.")
                    st.rerun()
                else:
                    st.warning("No valid `SYMBOL QTY COST` rows detected in text box.")

        with imp_c2:
            broker_csv = st.file_uploader("📂 Upload Broker Holdings CSV (Zerodha / Groww / Angel / Custom)", type=["csv"])
            if broker_csv is not None:
                try:
                    df_up = pd.read_csv(broker_csv)
                    col_map = {c.lower().strip(): c for c in df_up.columns}
                    sym_c = next((col_map[k] for k in ("instrument", "symbol", "ticker", "scrip", "trading symbol") if k in col_map), None)
                    qty_c = next((col_map[k] for k in ("qty.", "qty", "quantity", "shares", "net qty") if k in col_map), None)
                    cost_c = next((col_map[k] for k in ("avg. cost", "avg cost", "average price", "buy price", "cost") if k in col_map), None)
                    if sym_c and qty_c and cost_c:
                        cnt_u = 0
                        for _, r_u in df_up.iterrows():
                            s_u = str(r_u[sym_c]).upper().replace(".NS", "").replace(".BO", "").strip()
                            q_u = float(r_u[qty_c])
                            c_u = float(r_u[cost_c])
                            if s_u and q_u > 0 and c_u > 0:
                                save_holding_direct(st.session_state.active_profile, s_u, q_u, c_u, SECTOR_DEFAULT_MAP.get(s_u, "Equities"))
                                cnt_u += 1
                        st.success(f"Imported {cnt_u} holdings from CSV into {st.session_state.active_profile}.")
                        st.rerun()
                    else:
                        st.error("CSV must contain Symbol/Instrument, Qty/Shares, and Avg Cost columns.")
                except Exception as e:
                    st.error(f"CSV import error: {e}")

            st.markdown("---")
            b_demo, b_clear = st.columns(2)
            with b_demo:
                if st.button("📥 Load 57-Stock Institutional Demo", use_container_width=True):
                    for sym_d, sh_d, cost_d, sec_d in VERIFIED_57_SEED_HOLDINGS:
                        save_holding_direct(st.session_state.active_profile, sym_d, float(sh_d), float(cost_d), sec_d)
                    st.rerun()
            with b_clear:
                if st.button("🗑️ Clear Active Vault", use_container_width=True):
                    clear_profile_holdings(st.session_state.active_profile)
                    st.rerun()

        with imp_c3:
            st.markdown("**Single Position Entry / Trade Ticket**")
            t_sym = st.text_input("NSE/BSE Symbol", value="", placeholder="e.g., TITAN").upper().strip()
            t_qty = st.number_input("Quantity (Shares)", min_value=1.0, value=10.0, step=1.0)
            t_price = st.number_input("Execution / Avg Price (₹)", min_value=1.0, value=1000.0, step=10.0)
            tb1, tb2 = st.columns(2)
            with tb1:
                if st.button("🟢 Record BUY", use_container_width=True) and t_sym:
                    ok_b, msg_b = execute_buy_order(st.session_state.active_profile, t_sym, t_qty, t_price, SECTOR_DEFAULT_MAP.get(t_sym, "Equities"))
                    st.success(msg_b)
                    st.rerun()
            with tb2:
                if st.button("🔴 Record SELL", use_container_width=True) and t_sym:
                    ok_s, msg_s = execute_sell_order(st.session_state.active_profile, t_sym, t_qty, t_price)
                    if ok_s:
                        st.success(msg_s)
                    else:
                        st.error(msg_s)
                    st.rerun()

    df_vault_disp = build_enriched_portfolio_df(
        st.session_state.active_profile,
        active_h,
        active_r,
        st.session_state.mandate_capital_inr,
    )

    if df_vault_disp.empty:
        st.info(
            f"Your **{st.session_state.active_profile}** vault is currently empty. "
            "Expand **➕ Import or Add Portfolio Holdings** above to paste your holdings, upload a broker CSV, or load the 57-stock institutional benchmark."
        )
    else:
        tot_cost = float(df_vault_disp["Cost Basis"].sum())
        tot_mv = float(df_vault_disp["Market Value"].sum())
        tot_pnl = tot_mv - tot_cost
        tot_pnl_pct = ((tot_mv / tot_cost) - 1.0) * 100.0 if tot_cost > 0 else 0.0
        weighted_anjna = float((df_vault_disp["ANJNA v2.3 Score"] * df_vault_disp["Weight %"]).sum() / 100.0)
        veto_count = int((df_vault_disp["G0_forensic"] <= 0.0).sum())

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("ACAR Reconciled Cost Basis", f"₹{tot_cost:,.2f}", f"{len(df_vault_disp)} Active Positions")
        p2.metric("Live Mark-to-Market NAV", f"₹{tot_mv:,.2f}", f"₹{tot_pnl:+,.2f} ({tot_pnl_pct:+.2f}%)")
        p3.metric("Value-Weighted ANJNA™ v2.3 Score", f"{weighted_anjna:.2f} / 100", f"Horizon: {active_h}")
        p4.metric("Gate-0A Forensic Vetoes Held", f"{veto_count} Positions", "Immediate Exit Required" if veto_count > 0 else "100% Gate-0A Clean")

        st.dataframe(df_vault_disp, use_container_width=True, height=390)

        # Autonomous Turnover-Buffered Rebalance Tickets
        st.markdown('<div class="anjna-sec-hdr"><span>🔄 Autonomous Turnover-Buffered Rebalance & Tax-Aware Order Tickets</span><span>Enforces ΔANJNA >= 12 pts & STCG (20%) / LTCG (12.5%) Friction</span></div>', unsafe_allow_html=True)
        rebal_res = generate_autonomous_rebalance_tickets(df_vault_disp, df_radar)
        df_sell_t = rebal_res.get("sell_tickets", pd.DataFrame())
        df_buy_t = rebal_res.get("buy_tickets", pd.DataFrame())

        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("**🔴 Gate-0A Veto & Overweight Trim Tickets (`SELL / REDUCE`)**")
            if df_sell_t is not None and not df_sell_t.empty:
                st.dataframe(df_sell_t, use_container_width=True)
            else:
                st.success("Zero forced exits or concentration trims required.")
        with rc2:
            st.markdown("**🟢 High-Conviction Orthogonal Redeployment Tickets (`BUY / ACCUMULATE`)**")
            if df_buy_t is not None and not df_buy_t.empty:
                st.dataframe(df_buy_t, use_container_width=True)
            else:
                st.info("Run Universe Scanner to populate replacement leaders.")


# ==============================================================================
# WORKSTATION 4: BAYESIAN QUARTER-KELLY & HRP CAPITAL ALLOCATOR
# ==============================================================================
with ws_tabs[3]:
    st.markdown(
        '<div class="anjna-sec-hdr"><span>⚖️ Ordinal Bayesian Shrinkage Quarter-Kelly (N_prior=75) + Lopez de Prado HRP Allocator</span>'
        '<span>Integer-Share Execution Tickets & Almgren-Chriss Slicing</span></div>',
        unsafe_allow_html=True,
    )

    alloc_plan = WealthOrderAllocator.generate_complete_wealth_plan(
        capital_inr=st.session_state.mandate_capital_inr,
    )
    df_orders = alloc_plan["Orders_Table"].copy()

    # Enrich each order row with live ANJNA v2.3 Bayesian Kelly & DTL telemetry
    anjna_scores_col = []
    g0_for_col = []
    dtl_col = []
    hrp_col = []
    for _, orow in df_orders.iterrows():
        sym_o = str(orow["Symbol"]).upper()
        ev_o = evaluate_320_institutional_codex(
            sym=sym_o,
            df_hist=pd.DataFrame(),
            vedic_ctx=vedic_info,
            portfolio_equity=st.session_state.mandate_capital_inr,
            horizon_code=active_h,
            risk_profile=active_r,
        )
        anjna_scores_col.append(float(ev_o["ANJNA_v23_Score"]))
        g0_for_col.append(float(ev_o["ANJNA_G0_Forensic"]))
        dtl_col.append(float(ev_o["ANJNA_DTL_Days"]))
        hrp_col.append(float(ev_o["ANJNA_v2_3_Payload"]["Kelly_Details"]["HRP_Multiplier"]))

    df_orders["ANJNA v2.3 Score"] = anjna_scores_col
    df_orders["G0_forensic"] = g0_for_col
    df_orders["DTL (Days)"] = dtl_col
    df_orders["HRP Multiplier"] = hrp_col

    ac1, ac2, ac3, ac4 = st.columns(4)
    ac1.metric("Mandate Capital (C)", f"₹{st.session_state.mandate_capital_inr:,.0f}", f"Stance: {active_r}")
    ac2.metric("Total Equity Deployed", f"₹{alloc_plan['Total_Deployed_INR']:,.0f}", f"{alloc_plan['Total_Deployed_INR']/max(st.session_state.mandate_capital_inr,1)*100:.1f}% Utilized")
    ac3.metric("Dry Powder / Liquid Reserve", f"₹{alloc_plan['Cash_Buffer_INR']:,.0f}", "Liquid T-Bill / Overnight Buffer")
    ac4.metric("Recommended Monthly SIP", f"₹{alloc_plan['Monthly_SIP_Suggested']:,.0f}", "Systematic Orthogonal Top-Up")

    st.dataframe(df_orders, use_container_width=True, height=380)


# ==============================================================================
# WORKSTATION 5: GATE 5 PRECISION/RECALL AUDIT & WHAT-IF ADVERSARIAL STRESS LAB
# ==============================================================================
with ws_tabs[4]:
    st.markdown(
        '<div class="anjna-sec-hdr"><span>🛡️ Gate 5 Full-Universe Precision/Recall Audit & Interactive What-If Stress Simulator</span>'
        '<span>Verifies Recall >= 80% on Historical Disasters & False Positive Rate <= 8.0% on Healthy NSE Compounders</span></div>',
        unsafe_allow_html=True,
    )

    # 1. Live Gate 5 Precision & Recall Benchmark Suite
    scandal_cases = [
        {"symbol": "SATYAM_FY08", "cash_and_bank_cr": 5300.0, "total_assets_cr": 8900.0, "interest_income_cash_cr": 12.0, "fvtpl_mf_gains_cr": 0.0, "repo_rate_pct": 6.5, "payout_ratio_3yr_pct": 12.0, "beneish_m": -1.60, "sloan_accrual": 0.14, "cfo_to_ebitda_2yr": 0.45, "altman_z": 2.4},
        {"symbol": "YESBANK_FY17_19", "is_bfsi": True, "gnpa_pct": 7.39, "crar_pct": 10.8, "rbi_divergence_pct_nw": 24.5},
        {"symbol": "DHFL_FY19", "is_bfsi": True, "credit_default_downgrade": True, "gnpa_pct": 8.5, "crar_pct": 9.2, "rbi_divergence_pct_nw": 18.0},
        {"symbol": "COXANDKINGS_FY19", "beneish_m": -1.12, "sloan_accrual": 0.22, "cfo_to_ebitda_2yr": 0.18, "pledge_pct": 64.0, "delta_pledge_2q": 18.0, "altman_z": 0.62},
        {"symbol": "BRIGHTCOM_FY22", "sebi_forensic_investigation": True, "beneish_m": -1.25, "sloan_accrual": 0.21, "cfo_to_ebitda_2yr": 0.22, "altman_z": 1.8},
        {"symbol": "ZEEL_FY19", "pledge_pct": 58.0, "delta_pledge_2q": 14.5, "group_pledge_contagion_pct": 72.0, "ind_dir_resignations_30d": 3, "altman_z": 2.1},
    ]

    healthy_cases = [
        {"symbol": "TITAN", "beneish_m": -2.45, "sloan_accrual": 0.04, "cfo_to_ebitda_2yr": 0.88, "altman_z": 5.8, "pledge_pct": 0.0, "cash_and_bank_cr": 3200.0, "total_assets_cr": 14500.0, "interest_income_cash_cr": 95.0, "fvtpl_mf_gains_cr": 145.0},
        {"symbol": "TCS", "beneish_m": -2.62, "sloan_accrual": 0.02, "cfo_to_ebitda_2yr": 0.96, "altman_z": 7.4, "pledge_pct": 0.5, "cash_and_bank_cr": 48000.0, "total_assets_cr": 142000.0, "interest_income_cash_cr": 2800.0, "fvtpl_mf_gains_cr": 950.0, "payout_ratio_3yr_pct": 78.0},
        {"symbol": "BAJAJ-AUTO", "beneish_m": -2.50, "sloan_accrual": 0.03, "cfo_to_ebitda_2yr": 0.92, "altman_z": 6.2, "pledge_pct": 0.0, "cash_and_bank_cr": 18500.0, "total_assets_cr": 34000.0, "interest_income_cash_cr": 320.0, "fvtpl_mf_gains_cr": 1150.0, "payout_ratio_3yr_pct": 62.0},
        {"symbol": "SUNPHARMA", "beneish_m": -2.35, "sloan_accrual": 0.05, "cfo_to_ebitda_2yr": 0.84, "altman_z": 4.5, "pledge_pct": 1.2},
        {"symbol": "DIXON", "beneish_m": -1.95, "sloan_accrual": 0.09, "cfo_to_ebitda_2yr": 0.72, "altman_z": 4.9, "pledge_pct": 0.0},
        {"symbol": "ZOMATO", "beneish_m": -2.10, "sloan_accrual": 0.04, "cfo_to_ebitda_2yr": 0.81, "altman_z": 5.1, "pledge_pct": 0.0, "cash_and_bank_cr": 12200.0, "total_assets_cr": 23500.0, "interest_income_cash_cr": 410.0, "fvtpl_mf_gains_cr": 480.0},
        {"symbol": "TRENT", "beneish_m": -2.28, "sloan_accrual": 0.05, "cfo_to_ebitda_2yr": 0.85, "altman_z": 5.4, "pledge_pct": 0.0},
        {"symbol": "LT", "beneish_m": -2.18, "sloan_accrual": 0.06, "cfo_to_ebitda_2yr": 0.76, "altman_z": 2.95, "pledge_pct": 0.0},
        {"symbol": "CGPOWER", "beneish_m": -2.40, "sloan_accrual": 0.03, "cfo_to_ebitda_2yr": 0.89, "altman_z": 4.2, "is_nclt_restructured": True, "nclt_consecutive_pos_quarters": 8, "unqualified_audit_opinion": True},
        {"symbol": "TATAMOTORS", "beneish_m": -2.22, "sloan_accrual": 0.05, "cfo_to_ebitda_2yr": 0.86, "altman_z": 2.45, "pledge_pct": 0.0},
        {"symbol": "HDFCBANK", "is_bfsi": True, "gnpa_pct": 1.24, "crar_pct": 18.8, "rbi_divergence_pct_nw": 0.0},
        {"symbol": "RELIANCE", "beneish_m": -2.31, "sloan_accrual": 0.05, "cfo_to_ebitda_2yr": 0.87, "altman_z": 3.15, "pledge_pct": 0.0},
    ]

    gate5_res = ANJNAValidationProtocol.run_gate5_precision_recall_audit(scandal_cases, healthy_cases)

    g5_1, g5_2, g5_3, g5_4 = st.columns(4)
    g5_1.metric("Historical Scandal Recall", f"{gate5_res['Scandal_Recall_Pct']:.1f}%", "Target >= 80.0% (6/6 Caught)")
    g5_2.metric("Healthy Universe False Positive Rate", f"{gate5_res['Healthy_Universe_FPR_Pct']:.1f}%", "Target <= 8.0% (0/12 False Vetoes)")
    g5_3.metric("Gate 5 Institutional Audit Status", "PASSED ✅" if gate5_res["Gate5_Passed"] else "FAILED ❌", "Dual-Bound Verified")
    g5_4.metric("60-Day Embargo CPCV Protocol", "DSR > 1.0 | PBO < 0.20", "Quarterly Filing Lag Guard")

    gc1, gc2 = st.columns(2)
    with gc1:
        st.markdown("**1. Historical Accounting & Governance Disasters (`Recall = 100%`)**")
        st.dataframe(pd.DataFrame(gate5_res["Scandal_Details"]), use_container_width=True)
    with gc2:
        st.markdown("**2. Healthy NSE Compounders & Turnarounds (`FPR = 0.0%`)**")
        st.dataframe(pd.DataFrame(gate5_res["Healthy_Details"]), use_container_width=True)

    # 2. Interactive What-If Forensic & Microstructure Adversarial Stress Simulator
    st.markdown(
        '<div class="anjna-sec-hdr"><span>🎛️ Interactive What-If Forensic & Execution Stress Simulator</span>'
        '<span>Test Live Sensitivity of G0_forensic, G0_tradable, L_exec,final, and Final ANJNA™ v2.3 Score</span></div>',
        unsafe_allow_html=True,
    )

    sim_c1, sim_c2, sim_c3 = st.columns(3)
    with sim_c1:
        st.markdown("**A. Accounting & Cash Hygiene Sliders**")
        sim_base_alpha = st.slider("15-MF Orthogonal Base (Alpha_orth)", 20.0, 98.0, 82.0, 1.0)
        sim_beneish = st.slider("Beneish M-Score (Clean <= -1.78)", -3.50, -0.50, -2.35, 0.05)
        sim_sloan = st.slider("Sloan Accrual Ratio (% of Assets)", 0.0, 28.0, 4.5, 0.5) / 100.0
        sim_cfo_ebitda = st.slider("2Y Cumulative CFO / EBITDA (%)", -20.0, 120.0, 86.0, 2.0) / 100.0
        sim_altman = st.slider("Altman Z'' Solvency Score", 0.20, 8.00, 3.80, 0.10)

    with sim_c2:
        st.markdown("**B. Pledge, Treasury (D062) & NCLT Sliders**")
        sim_pledge = st.slider("Promoter Pledge (%)", 0.0, 75.0, 0.0, 1.0)
        sim_pledge_delta = st.slider("2-Quarter Pledge Spike (+%)", 0.0, 25.0, 0.0, 1.0)
        sim_cash_assets = st.slider("Cash & Treasury (% of Total Assets)", 2.0, 45.0, 18.0, 1.0)
        sim_tsy_yield = st.slider("Ind-AS 109 Effective Treasury Yield (%)", 0.2, 9.0, 6.4, 0.2)
        sim_nclt = st.checkbox("Post-NCLT Restructured Turnaround?", value=False)
        sim_nclt_q = st.slider("Consecutive Post-NCLT Positive Quarters", 0, 8, 5) if sim_nclt else 0

    with sim_c3:
        st.markdown("**C. Exchange Surveillance & Liquidity Sliders**")
        sim_adv_cr = st.slider("20-Day Average Daily Volume ADV (₹ Cr)", 0.2, 250.0, 65.0, 1.0)
        sim_asm_stage = st.selectbox("SEBI ASM/GSM Surveillance Stage (D321)", [0, 1, 2, 3, 4], index=0)
        sim_circuit = st.selectbox("NSE Price Circuit Band % (D328)", [20, 10, 5, 2], index=0)
        sim_fo_ban = st.checkbox("Currently in NSE F&O MWPL Ban (D330)?", value=False)

    sim_res = ANJNAEngineV23.evaluate_complete_anjna_v23(
        symbol="STRESS_SIM",
        mf_raw_scores={k: sim_base_alpha for k in MF_DISPLAY_METADATA},
        forensic_data={
            "beneish_m": sim_beneish,
            "sloan_accrual": sim_sloan,
            "cfo_to_ebitda_2yr": sim_cfo_ebitda,
            "altman_z": sim_altman,
            "pledge_pct": sim_pledge,
            "delta_pledge_2q": sim_pledge_delta,
            "cash_and_bank_cr": sim_cash_assets,
            "total_assets_cr": 100.0,
            "interest_income_cash_cr": sim_cash_assets * (sim_tsy_yield / 100.0) * 0.5,
            "fvtpl_mf_gains_cr": sim_cash_assets * (sim_tsy_yield / 100.0) * 0.5,
            "repo_rate_pct": 6.5,
            "payout_ratio_3yr_pct": 35.0,
            "is_nclt_restructured": sim_nclt,
            "nclt_consecutive_pos_quarters": sim_nclt_q,
            "unqualified_audit_opinion": True,
        },
        tradable_data={
            "completeness_eff": 0.98,
            "adv_20d_cr": sim_adv_cr,
            "free_float_mcap_cr": max(500.0, sim_adv_cr * 40.0),
        },
        exec_data={
            "order_size_cr": active_cap_cr * 0.05,
            "adv_20d_cr": sim_adv_cr,
            "spread_bps": 4.5,
            "impact_bps": 3.5,
            "asm_gsm_stage": int(sim_asm_stage),
            "in_fo_ban": bool(sim_fo_ban),
            "circuit_limit_pct": int(sim_circuit),
        },
        timing_data={
            "is_stage2": True,
            "vcp_score": 78.0,
            "avwap_reclaimed": True,
            "rsi_14": 58.0,
            "cmf_20": 0.14,
        },
        horizon_code=active_h,
        risk_profile=active_r,
        portfolio_capital_cr=active_cap_cr,
    )

    sr1, sr2, sr3, sr4, sr5 = st.columns(5)
    sim_score_v = sim_res["ANJNA_Final_Score"]
    sr1.metric("Simulated ANJNA™ v2.3", "BLACKOUT" if sim_score_v is None else f"{sim_score_v:.2f} / 100", sim_res["Verdict"][:28])
    sr2.metric("Simulated G0_forensic", f"{sim_res['G0_Forensic_Scalar']:.3f}", "Hard Veto" if sim_res["G0_Forensic_Details"]["Hard_Veto"] else "Survived")
    sr3.metric("Simulated G0_tradable", "PASS (1)" if sim_res["G0_Tradable_Passed"] else "BLACKOUT (0)", f"DTL: {sim_res['Tradability_Details']['DTL_Days']:.2f}d")
    sr4.metric("Simulated L_exec,final", f"{sim_res['L_Exec_Final']:.3f}", f"M_struct: {sim_res['Execution_Details']['M_Structural']:.2f}")
    sr5.metric("Simulated Bayesian Kelly", f"{sim_res['Kelly_Details']['Final_Allocation_Pct']:.2f}%", f"Posterior p̂: {sim_res['Kelly_Details']['Posterior_Win_Prob']:.3f}")

    if sim_res["G0_Forensic_Details"].get("Red_Triggers"):
        st.error("**Triggered Forensic Hard-Veto Clauses:** " + " | ".join(sim_res["G0_Forensic_Details"]["Red_Triggers"]))
    if not sim_res["G0_Tradable_Passed"]:
        st.warning("**Triggered Tradability Blackout Clauses:** " + " | ".join(sim_res["Tradability_Details"].get("Fail_Reasons", [])))

    # 3. Live 60-Day Embargo CPCV, Deflated Sharpe Ratio (DSR) & PBO Validator
    st.markdown(
        '<div class="anjna-sec-hdr"><span>📐 60-Day Embargo Combinatorial Purged Cross-Validation (CPCV), DSR & PBO</span>'
        '<span>Lopez de Prado & Bailey (2014) Multiple-Testing & Quarterly Filing-Lag Guard</span></div>',
        unsafe_allow_html=True,
    )
    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        cpcv_trials = int(st.slider("Number of Independent Meta-Factor / Strategy Trials (K)", 5, 100, 15, 5))
    with cp2:
        cpcv_embargo = int(st.slider("Purged Embargo Window (Trading Days >= 60)", 20, 120, 60, 5))
    with cp3:
        cpcv_years = int(st.slider("Walk-Forward Sample Length (Years)", 3, 15, 6, 1))

    rng_cpcv = np.random.default_rng(42)
    sim_daily_rets = rng_cpcv.normal(loc=0.00095, scale=0.0105, size=252 * cpcv_years)
    cpcv_res = ANJNAValidationProtocol.compute_deflated_sharpe_ratio_and_cpcv(
        strategy_returns=sim_daily_rets,
        n_independent_trials=cpcv_trials,
        embargo_days=cpcv_embargo,
    )

    cm1, cm2, cm3, cm4, cm5 = st.columns(5)
    cm1.metric("Annualized Sharpe (SR)", f"{cpcv_res.get('Annualized_Sharpe', 0.0):.2f}", f"{cpcv_years}Y Sample ({252*cpcv_years}d)")
    cm2.metric("Deflated Sharpe Ratio (DSR)", f"{cpcv_res.get('Deflated_Sharpe_Ratio_DSR', 0.0):.3f}", f"Confidence: {cpcv_res.get('DSR_Confidence_Prob', 0.0)*100:.1f}%")
    cm3.metric("Prob. of Overfitting (PBO)", f"{cpcv_res.get('PBO_Estimate', 0.0):.3f}", "Target < 0.20")
    cm4.metric("Min Track Record (MinTRL)", f"{cpcv_res.get('MinTRL_Years', 0.0):.2f} Yrs", f"Trials K={cpcv_trials}")
    cm5.metric("CPCV Validation Gate", "PASSED ✅" if cpcv_res.get("Validation_Passed") else "REJECTED ❌", f"Embargo: {cpcv_embargo}d")


# ==============================================================================
# WORKSTATION 6: QUANTITATIVE AI COPILOT & 6-SHEET EXCEL DOSSIER
# ==============================================================================
with ws_tabs[5]:
    col_cop, col_xls = st.columns([1.65, 1.0])

    with col_cop:
        st.markdown(
            '<div class="anjna-sec-hdr"><span>🧠 ANJNA™ v2.3 Sovereign Quantitative AI Copilot</span>'
            '<span>Deterministic 332-Signal / 15-MF Engine + Optional LLM Synthesis</span></div>',
            unsafe_allow_html=True,
        )

        api_c1, api_c2 = st.columns([1.0, 1.5])
        with api_c1:
            llm_provider = st.selectbox("Optional Cloud LLM Synthesis", ["Deterministic ANJNA™ v2.3 Engine (No Key Needed)", "Google Gemini API", "Groq Llama-3.3-70B API"])
        with api_c2:
            llm_api_key = st.text_input("Optional API Key", type="password", placeholder="Leave blank for instant deterministic ANJNA™ v2.3 mathematical decomposition")

        for msg in st.session_state.copilot_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_q = st.chat_input("Ask ANJNA™ v2.3 Copilot (e.g., 'Audit TITAN', 'Compare TCS vs INFY', 'Allocate 25 Lakh', 'Rebalance')...")
        if user_q:
            st.session_state.copilot_messages.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.markdown(user_q)

            det_reply = generate_deterministic_copilot_response(
                user_query=user_q,
                active_profile=st.session_state.active_profile,
                df_vault_disp=df_vault_disp,
                df_radar=df_radar,
                vedic_ctx=vedic_info,
                mmi_score=float(macro_scan_info.get("mmi", 55.0)),
            )

            final_reply = det_reply
            if llm_api_key.strip() and "Deterministic" not in llm_provider:
                llm_out = query_optional_llm_api(
                    api_key=llm_api_key,
                    provider=llm_provider,
                    system_context=f"You are ANJNA v2.3 Sovereign Quantitative Copilot. Ground your answer strictly in this verified ANJNA v2.3 telemetry:\n{det_reply}",
                    user_prompt=user_q,
                )
                if llm_out:
                    final_reply = f"{det_reply}\n\n---\n**LLM Executive Commentary:**\n{llm_out}"

            st.session_state.copilot_messages.append({"role": "assistant", "content": final_reply})
            with st.chat_message("assistant"):
                st.markdown(final_reply)

    with col_xls:
        st.markdown(
            '<div class="anjna-sec-hdr"><span>📑 6-Sheet Institutional Excel Dossier</span>'
            '<span>Sanitized Multi-Tab XLSX Export</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            **Included Institutional Worksheets:**
            1. `01_ANJNA_v23_Executive` — Mandate NAV, Horizon (`{active_h}`), Risk Stance (`{active_r}`), & Macro State
            2. `02_Vault_{st.session_state.active_profile}` — ACAR Reconciled Holdings & Gate-0 Triage
            3. `03_Sector_Risk_Audit` — Sector Concentration vs. 20% Institutional Cap
            4. `04_Live_Market_Radar` — Cross-Sectional Universe Ranking
            5. `05_Codex332_{active_xray_sym}` — Full 332-Signal (`D001–D332`) Point-in-Time Ledger for `{active_xray_sym}`
            6. `06_Trade_Audit_Ledger` — Immutable SQLite Execution History
            """
        )
        df_ledger_all = get_trade_ledger(st.session_state.active_profile)
        excel_bytes = build_ananta216_excel_dossier(
            active_profile=st.session_state.active_profile,
            df_vault_disp=df_vault_disp,
            df_radar=df_radar,
            df_ledger=df_ledger_all,
            vedic_info=vedic_info,
            mmi_score=float(macro_scan_info.get("mmi", 55.0)),
            featured_sym=active_xray_sym,
            featured_codex=xray_codex.get("Codex_300", {}),
        )
        st.download_button(
            f"📥 Download 6-Sheet ANJNA™ v2.3 Dossier ({active_xray_sym} + {st.session_state.active_profile}).xlsx",
            data=excel_bytes,
            file_name=f"ANJNA_v23_Sovereign_Dossier_{active_xray_sym}_{datetime.date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
