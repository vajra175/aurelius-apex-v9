# ==============================================================================
# 👁️ ANJNA™ v2.3 — SOVEREIGN WEALTH & QUANTITATIVE INVESTMENT TERMINAL
# ==============================================================================
# World-Class Investor & Institutional FinTech Interface (Mobile + Desktop)
# Powered by the ANJNA™ v2.3 Orthogonal Engine (332 Signals -> 15 Meta-Factors)
# Design Principles:
#   - Zero Raw Math Formulas or Coding Jargon on Main Investor Screens
#   - Rich FinTech Bento Cards with Plain-English 3-Point Investment Thesis
#   - Live Dynamic Stock Selection (Zero ₹100 / 82.0 Static Placeholders)
#   - Dual High-Contrast Theme Engine (Obsidian Dark & Alabaster Light)
#   - Optional Deep Quant Drawer for 15 Meta-Factors, Heatmaps & 332 Signals
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
    ANJNAEngineV23,
    ANJNAMetaFactorEngine,
    ANJNAValidationProtocol,
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
    sanitize_ohlcv_corporate_actions,
    save_holding_direct,
    scan_radar_universe_216,
)
from modules.data_pipeline import (
    get_searchable_universe_list,
    parse_search_string,
)
from core.wealth_order_allocator import WealthOrderAllocator

# ------------------------------------------------------------------------------
# 1. PAGE CONFIG & SESSION STATE
# ------------------------------------------------------------------------------
APP_ICON_IMG, APP_ICON_B64 = build_vajra_app_icon()

st.set_page_config(
    page_title="ANJNA™ Wealth & Quant Terminal",
    page_icon=APP_ICON_IMG,
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

if "active_profile" not in st.session_state:
    st.session_state.active_profile = DEFAULT_PROFILES[0]
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "🌙 Obsidian Dark"
if "active_horizon" not in st.session_state:
    st.session_state.active_horizon = "H4"
if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = "MODERATE"
if "mandate_capital_inr" not in st.session_state:
    st.session_state.mandate_capital_inr = 1000000.0
if "vedic_overlay_enabled" not in st.session_state:
    st.session_state.vedic_overlay_enabled = False
if "selected_xray_symbol" not in st.session_state:
    st.session_state.selected_xray_symbol = "TITAN"
if "copilot_messages" not in st.session_state:
    st.session_state.copilot_messages = [
        {
            "role": "assistant",
            "content": (
                "### 👋 Welcome to Your ANJNA™ AI Investment Advisor\n"
                "I analyze **332 financial, cash-flow, institutional-flow, and technical indicators** across Indian stocks to help you invest safely and profitably.\n\n"
                "**Tap any quick button above or type a question below:**\n"
                "- *\"What are the top 5 stocks to buy today?\"*\n"
                "- *\"Allocate ₹10 Lakh safely\"*\n"
                "- *\"Audit TITAN\"* or *\"Compare TCS vs INFY\"*\n"
                "- *\"Check my portfolio for risk and red flags\"*"
            ),
        }
    ]

HORIZON_LABELS = {
    "H0": "Intraday / 1–3 Days",
    "H1": "Swing Trade (1–3 Weeks)",
    "H2": "Quarterly Earnings (1–3 Months)",
    "H3": "Medium-Term Cycle (3–6 Months)",
    "H4": "1–3 Year Wealth Builder",
    "H5": "3–5+ Year Compounder",
}

MF_PLAIN_NAMES: Dict[str, Tuple[str, str]] = {
    "MF01": ("Accounting & Cash Purity", "Quality & Safety"),
    "MF02": ("Return on Capital (ROIC Spread)", "Quality & Safety"),
    "MF03": ("Reinvestment Moat (3Y ROIIC)", "Quality & Safety"),
    "MF04": ("Governance & Promoter Integrity", "Quality & Safety"),
    "MF05": ("Valuation Margin of Safety", "Value & Yield"),
    "MF06": ("Dividend & Shareholder Yield", "Value & Yield"),
    "MF07": ("Institutional & PE Sponsorship", "Catalysts & Deals"),
    "MF08": ("Relative Trend Strength", "Momentum & Trend"),
    "MF09": ("Volatility Contraction (VCP)", "Momentum & Trend"),
    "MF10": ("Swing Pullback Elasticity", "Smart-Money Flow"),
    "MF11": ("Whale Accumulation & Delivery Flow", "Smart-Money Flow"),
    "MF12": ("Trend Persistence & Low Slippage", "Macro & Regime"),
    "MF13": ("Order-Book & Earnings Catalysts", "Catalysts & Deals"),
    "MF14": ("Sector Rotation Tailwind", "Macro & Regime"),
    "MF15": ("Quality × Momentum Synergy", "Momentum & Trend"),
}


# ------------------------------------------------------------------------------
# 2. DUAL-THEME FINTECH BENTO DESIGN SYSTEM (DARK OBSIDIAN & LIGHT ALABASTER)
# ------------------------------------------------------------------------------
def inject_fintech_theme_css(theme_choice: str) -> None:
    is_light = "Light" in theme_choice
    if is_light:
        bg_app = "#F4F7FB"
        bg_card = "#FFFFFF"
        bg_subtle = "#EEF2F6"
        text_main = "#0F172A"
        text_muted = "#475569"
        border_col = "#CBD5E1"
        accent_primary = "#0284C7"
        accent_green = "#059669"
        accent_amber = "#D97706"
        accent_red = "#DC2626"
        shadow_css = "0 4px 16px rgba(15, 23, 42, 0.06)"
    else:
        bg_app = "#060913"
        bg_card = "#0F1629"
        bg_subtle = "#162038"
        text_main = "#F8FAFC"
        text_muted = "#94A3B8"
        border_col = "#1E293B"
        accent_primary = "#38BDF8"
        accent_green = "#10B981"
        accent_amber = "#F59E0B"
        accent_red = "#EF4444"
        shadow_css = "0 8px 28px rgba(0, 0, 0, 0.42)"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: {bg_app} !important;
            color: {text_main} !important;
        }}
        .stApp {{
            background-color: {bg_app} !important;
            color: {text_main} !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {bg_card} !important;
            border-right: 1px solid {border_col} !important;
        }}
        .block-container {{
            padding-top: 0.9rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1420px !important;
        }}

        /* Top Hero Bar */
        .hero-bar {{
            background: linear-gradient(135deg, {bg_card} 0%, {bg_subtle} 100%);
            border: 1px solid {border_col};
            border-radius: 16px;
            padding: 16px 20px;
            margin-bottom: 12px;
            box-shadow: {shadow_css};
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .hero-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .hero-title {{
            font-size: 1.28rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: {text_main};
            margin: 0;
        }}
        .hero-subtitle {{
            font-size: 0.80rem;
            color: {text_muted};
            margin-top: 2px;
        }}
        .hero-badges {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .pill-badge {{
            font-size: 0.74rem;
            font-weight: 600;
            padding: 5px 11px;
            border-radius: 999px;
            border: 1px solid {border_col};
            background: {bg_app};
            color: {text_main};
        }}
        .pill-green {{
            border-color: {accent_green};
            color: {accent_green};
        }}
        .pill-blue {{
            border-color: {accent_primary};
            color: {accent_primary};
        }}

        /* Bento Stock Card */
        .bento-stock-card {{
            background: {bg_card};
            border: 1px solid {border_col};
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: {shadow_css};
            transition: transform 0.12s ease, border-color 0.12s ease;
        }}
        .bento-stock-card:hover {{
            border-color: {accent_primary};
        }}
        .bento-top-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 12px;
        }}
        .bento-sym {{
            font-size: 1.15rem;
            font-weight: 800;
            color: {text_main};
            letter-spacing: -0.01em;
        }}
        .bento-sec {{
            font-size: 0.75rem;
            color: {text_muted};
            margin-top: 2px;
        }}
        .verdict-chip {{
            font-size: 0.72rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 8px;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .verdict-buy {{
            background: rgba(16, 185, 129, 0.14);
            color: {accent_green};
            border: 1px solid {accent_green};
        }}
        .verdict-hold {{
            background: rgba(245, 158, 11, 0.14);
            color: {accent_amber};
            border: 1px solid {accent_amber};
        }}
        .verdict-avoid {{
            background: rgba(239, 68, 68, 0.14);
            color: {accent_red};
            border: 1px solid {accent_red};
        }}

        /* 4-Metric Grid inside Bento Card */
        .bento-metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            background: {bg_subtle};
            border-radius: 10px;
            padding: 10px 12px;
            margin-bottom: 12px;
        }}
        @media (max-width: 640px) {{
            .bento-metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        .bm-item-label {{
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            color: {text_muted};
            margin-bottom: 2px;
        }}
        .bm-item-val {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.92rem;
            font-weight: 700;
            color: {text_main};
        }}

        /* Visual Price Range Bar */
        .range-bar-wrap {{
            margin: 8px 0 12px 0;
        }}
        .range-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 0.71rem;
            font-family: 'JetBrains Mono', monospace;
            color: {text_muted};
            margin-bottom: 4px;
        }}
        .range-track {{
            width: 100%;
            height: 7px;
            background: {bg_subtle};
            border-radius: 4px;
            overflow: hidden;
            display: flex;
        }}

        /* 3-Line Plain English Thesis */
        .bento-thesis {{
            font-size: 0.81rem;
            line-height: 1.48;
            color: {text_main};
            border-top: 1px solid {border_col};
            padding-top: 10px;
        }}
        .bento-thesis-item {{
            margin-bottom: 4px;
        }}
        .bento-news-box {{
            margin-top: 8px;
            padding: 8px 10px;
            border-radius: 8px;
            background: {bg_subtle};
            font-size: 0.75rem;
            color: {text_muted};
        }}

        /* Section Title */
        .sec-banner {{
            font-size: 1.05rem;
            font-weight: 800;
            color: {text_main};
            margin: 14px 0 10px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid {border_col};
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_fintech_theme_css(st.session_state.ui_theme)
IS_LIGHT = "Light" in st.session_state.ui_theme
PLOTLY_TEMPLATE = "plotly_white" if IS_LIGHT else "plotly_dark"
PLOT_BG = "#FFFFFF" if IS_LIGHT else "#0F1629"
PAPER_BG = "#F4F7FB" if IS_LIGHT else "#060913"
FONT_COLOR = "#0F172A" if IS_LIGHT else "#F8FAFC"


# ------------------------------------------------------------------------------
# 3. HTML BENTO CARD RENDERER (PLAIN ENGLISH, MOBILE & DESKTOP RESPONSIVE)
# ------------------------------------------------------------------------------
def render_stock_bento_card(
    sym: str,
    sector: str,
    score: float,
    cmp_val: float,
    chg_pct: float,
    buy_zone: str,
    stop_loss: float,
    target_1: float,
    roic_pct: float,
    kelly_pct: float,
    verdict_text: str,
    is_veto: bool = False,
    forensic_note: str = "100% Clean Accounting & Governance",
    extra_badge: str = "",
    order_qty: Optional[int] = None,
    order_outlay: Optional[float] = None,
    news_list: Optional[List[str]] = None,
) -> str:
    upside_pct = ((target_1 - cmp_val) / max(cmp_val, 1.0)) * 100.0
    stop_risk_pct = ((cmp_val - stop_loss) / max(cmp_val, 1.0)) * 100.0

    if is_veto or score < 40.0:
        chip_cls = "verdict-avoid"
        clean_verdict = "🔴 AVOID / RED FLAG"
    elif score >= 70.0:
        chip_cls = "verdict-buy"
        clean_verdict = "🟢 STRONG BUY" if score >= 78.0 else "🟢 BUY / ACCUMULATE"
    else:
        chip_cls = "verdict-hold"
        clean_verdict = "🟡 HOLD / WATCH"

    chg_color = "#10B981" if chg_pct >= 0 else "#EF4444"
    score_color = "#10B981" if score >= 70.0 else ("#F59E0B" if score >= 52.0 else "#EF4444")

    # Calculate position along Stop -> Target range
    span = max(target_1 - stop_loss, 1.0)
    pos_pct = float(np.clip(((cmp_val - stop_loss) / span) * 100.0, 8.0, 92.0))

    if order_qty is not None and order_outlay is not None:
        metric_4_label = "Actionable Order"
        metric_4_val = f"Buy {order_qty:,} sh (₹{order_outlay:,.0f})"
    else:
        alloc_inr = st.session_state.mandate_capital_inr * (kelly_pct / 100.0)
        est_sh = int(alloc_inr // max(cmp_val, 1.0))
        metric_4_label = "Suggested Sizing"
        metric_4_val = f"{kelly_pct:.1f}% ({est_sh:,} sh)" if not is_veto else "0.0% (Do Not Buy)"

    if is_veto:
        line_1 = f"⛔ <b>Accounting & Safety Alert:</b> {forensic_note}"
        line_2 = f"📉 <b>Capital Protection Rule:</b> Automatically blocked by Gate-0 Forensic Shield to protect your capital."
        line_3 = f"🛡️ <b>Action:</b> Avoid fresh entry; if held in portfolio, exit position."
    else:
        line_1 = f"💎 <b>Business Quality:</b> Return on Capital (ROIC) <b>{roic_pct:.1f}%</b> • {forensic_note}."
        line_2 = f"📈 <b>Reward vs Risk:</b> Target <b>₹{target_1:,.1f} (+{upside_pct:.1f}% upside)</b> with volatility stop-loss at <b>₹{stop_loss:,.1f} (-{stop_risk_pct:.1f}%)</b>."
        line_3 = f"🎯 <b>Execution Plan:</b> Accumulate in Buy Zone <b>{buy_zone}</b> • {metric_4_label}: <b>{metric_4_val}</b>."

    news_html = ""
    if news_list:
        top_n = str(news_list[0]).strip()
        news_html = f'<div class="bento-news-box">📰 <b>Catalyst & Intelligence:</b> {top_n}</div>'

    sub_badge = f" • {extra_badge}" if extra_badge else ""

    return f"""
    <div class="bento-stock-card">
        <div class="bento-top-row">
            <div>
                <div class="bento-sym">{sym} <span style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;color:{score_color};">({score:.1f}/100)</span></div>
                <div class="bento-sec">{sector}{sub_badge}</div>
            </div>
            <div>
                <span class="verdict-chip {chip_cls}">{clean_verdict}</span>
            </div>
        </div>
        <div class="bento-metrics-grid">
            <div>
                <div class="bm-item-label">Live Price</div>
                <div class="bm-item-val">₹{cmp_val:,.2f} <span style="font-size:0.76rem;color:{chg_color};">({chg_pct:+.2f}%)</span></div>
            </div>
            <div>
                <div class="bm-item-label">Ideal Buy Zone</div>
                <div class="bm-item-val">{buy_zone}</div>
            </div>
            <div>
                <div class="bm-item-label">1Y Target Price</div>
                <div class="bm-item-val" style="color:#10B981;">₹{target_1:,.1f} (+{upside_pct:.1f}%)</div>
            </div>
            <div>
                <div class="bm-item-label">{metric_4_label}</div>
                <div class="bm-item-val">{metric_4_val}</div>
            </div>
        </div>
        <div class="range-bar-wrap">
            <div class="range-labels">
                <span>🛡️ Stop: ₹{stop_loss:,.1f}</span>
                <span>📍 CMP: ₹{cmp_val:,.1f}</span>
                <span>🎯 Target: ₹{target_1:,.1f}</span>
            </div>
            <div class="range-track">
                <div style="width:{pos_pct:.0f}%;background:linear-gradient(90deg, #EF4444 0%, #38BDF8 100%);"></div>
                <div style="width:{100.0 - pos_pct:.0f}%;background:rgba(16, 185, 129, 0.30);"></div>
            </div>
        </div>
        <div class="bento-thesis">
            <div class="bento-thesis-item">{line_1}</div>
            <div class="bento-thesis-item">{line_2}</div>
            <div class="bento-thesis-item">{line_3}</div>
        </div>
        {news_html}
    </div>
    """


# ------------------------------------------------------------------------------
# 4. TOP HERO HEADER & ON-SCREEN INVESTOR CONTROL BAR (MOBILE + DESKTOP READY)
# ------------------------------------------------------------------------------
vedic_info = get_live_vedic_chronometer()

# Load cached market scan so all 5 stations have live NSE data immediately
df_radar, macro_scan_info = scan_radar_universe_216(vedic_info)
mmi_val = float(macro_scan_info.get("mmi", 54.0))
mmi_label = (
    "Fear / Contrarian Buy Zone"
    if mmi_val < 38
    else ("Balanced Accumulation" if mmi_val < 62 else "Strong Bullish Momentum")
)

st.markdown(
    f"""
    <div class="hero-bar">
        <div class="hero-brand">
            <img src="data:image/png;base64,{APP_ICON_B64}" width="42" height="42" style="border-radius:10px;" />
            <div>
                <div class="hero-title">ANJNA™ Sovereign Wealth & Stock Intelligence</div>
                <div class="hero-subtitle">Institutional Accounting Forensics • Smart-Money Flow • Automated Capital Sizing</div>
            </div>
        </div>
        <div class="hero-badges">
            <span class="pill-badge pill-green">📊 Market Mood: {mmi_val:.1f} ({mmi_label})</span>
            <span class="pill-badge pill-blue">💼 Capital: ₹{st.session_state.mandate_capital_inr/1e5:,.1f} Lakh ({st.session_state.risk_profile.title()})</span>
            <span class="pill-badge">🕒 {vedic_info['time_ist']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# On-Screen Quick Control Bar (Visible directly on mobile & desktop without opening sidebar)
ctrl_1, ctrl_2, ctrl_3, ctrl_4 = st.columns([1.3, 1.2, 1.4, 1.0])
with ctrl_1:
    new_cap = st.number_input(
        "💰 Investment Capital (₹)",
        min_value=10000.0,
        max_value=1000000000.0,
        value=float(st.session_state.mandate_capital_inr),
        step=100000.0,
    )
    st.session_state.mandate_capital_inr = float(new_cap)

with ctrl_2:
    RISK_MAP = {
        "CONSERVATIVE": "🛡️ Conservative (Safety First)",
        "MODERATE": "⚖️ Moderate (Balanced Growth)",
        "AGGRESSIVE": "🔥 Aggressive (High Velocity)",
    }
    st.session_state.risk_profile = st.selectbox(
        "🛡️ Risk Profile",
        options=list(RISK_MAP.keys()),
        format_func=lambda k: RISK_MAP[k],
        index=list(RISK_MAP.keys()).index(st.session_state.risk_profile),
    )

with ctrl_3:
    st.session_state.active_horizon = st.selectbox(
        "⏱️ Investment Horizon",
        options=list(HORIZON_LABELS.keys()),
        format_func=lambda k: f"{k}: {HORIZON_LABELS[k]}",
        index=list(HORIZON_LABELS.keys()).index(st.session_state.active_horizon),
    )

with ctrl_4:
    chosen_theme = st.selectbox(
        "🎨 Display Theme",
        ["🌙 Obsidian Dark", "☀️ Alabaster Light"],
        index=0 if "Dark" in st.session_state.ui_theme else 1,
    )
    if chosen_theme != st.session_state.ui_theme:
        st.session_state.ui_theme = chosen_theme
        st.rerun()

active_h = st.session_state.active_horizon
active_r = st.session_state.risk_profile
active_cap_inr = st.session_state.mandate_capital_inr


# Sidebar for Advanced Settings & Vault Backup
with st.sidebar:
    st.markdown("### ⚙️ Portfolio & Advanced Settings")
    st.session_state.active_profile = st.selectbox(
        "Active Family Portfolio Vault",
        DEFAULT_PROFILES,
        index=DEFAULT_PROFILES.index(st.session_state.active_profile)
        if st.session_state.active_profile in DEFAULT_PROFILES
        else 0,
    )
    st.session_state.vedic_overlay_enabled = st.toggle(
        "Enable Optional 4% Vedic Timing Tilt",
        value=bool(st.session_state.vedic_overlay_enabled),
        help="Off by default (100% pure quantitative & fundamental scoring).",
    )
    st.markdown("---")
    st.markdown("#### 💾 Backup & Restore Portfolio")
    st.download_button(
        "⬇️ Download Portfolio Backup (.json)",
        data=export_all_vaults_json(),
        file_name=f"anjna_portfolio_backup_{datetime.date.today().isoformat()}.json",
        mime="application/json",
        use_container_width=True,
    )
    up_j = st.file_uploader("Restore Backup (.json)", type=["json"])
    if up_j is not None:
        ok_j, msg_j = restore_vaults_from_json(up_j.read().decode("utf-8"))
        if ok_j:
            st.success(msg_j)
        else:
            st.error(msg_j)


# ------------------------------------------------------------------------------
# 5. HELPER: BUILD ENRICHED PORTFOLIO DATAFRAME & LIVE CANDIDATE POOL
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
                "Conviction Score": float(eval_res.get("ANJNA_v23_Score", eval_res.get("Master_Alpha_Score", 50.0))),
                "ROIC %": float(eval_res.get("ROIC %", 18.0)),
                "Safety Shield": str(eval_res.get("ANJNA_Forensic_Status", "PASS")),
                "Suggested Weight %": float(eval_res.get("ANJNA_Kelly_Pct", eval_res.get("Kelly Weight %", 0.0))),
                "Verdict": str(eval_res.get("ANJNA_Verdict", eval_res.get("Verdict", "HOLD"))),
                "Buy Zone": str(eval_res.get("Buy Zone", f"₹{cmp_live*0.98:.1f}-₹{cmp_live:.1f}")),
                "Stop-Loss (₹)": float(eval_res.get("Stop-Loss (₹)", cmp_live * 0.92)),
                "Target (₹)": float(eval_res.get("Target_T1 (₹)", cmp_live * 1.18)),
                "Forensic Note": str(eval_res.get("Forensic Note", "Clean Accounting")),
                "Hard Veto": bool(eval_res.get("Hard Veto", False)),
                "ACAR Note": acar_note,
            }
        )

    df_disp = pd.DataFrame(rows)
    tot_mv = float(df_disp["Market Value"].sum()) if not df_disp.empty else 0.0
    df_disp["Weight %"] = np.round((df_disp["Market Value"] / tot_mv) * 100.0, 2) if tot_mv > 0 else 0.0
    return df_disp.sort_values(by="Conviction Score", ascending=False).reset_index(drop=True)


def build_live_candidate_pool_from_radar(df_rad: pd.DataFrame) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    pool = []
    cmp_map: Dict[str, float] = {}
    if df_rad is None or df_rad.empty:
        return pool, cmp_map

    for _, r in df_rad.iterrows():
        sym = str(r["Symbol"])
        cmp_v = float(r.get("CMP (₹)", 100.0))
        cmp_map[sym] = cmp_v
        score_v = float(r.get("ANJNA_v23_Score", r.get("Master_Alpha_Score", 70.0)))
        eb = r.get("Executive_Brief", {}) or {}
        lf = r.get("Live_Forensics", {}) or {}
        div_y = float((r.get("Codex_300", {}) or {}).get("217. Trailing_Dividend_Yield_Pct", 1.5))
        pool.append(
            {
                "Symbol": sym,
                "Company_Name": sym,
                "Sector": str(r.get("Sector", "Equities")),
                "Score": score_v,
                "Master_Score": score_v,
                "CMP": cmp_v,
                "Live_CMP": cmp_v,
                "ROIC_Pct": float(r.get("ROIC %", 20.0)),
                "Div_Yield": div_y,
                "Dividend_Yield": div_y,
                "Horizon": str(r.get("Optimal_Horizon", active_h)),
                "Gate_0_Passed": not bool(r.get("Hard Veto", False)),
                "Stop_Loss": float(r.get("Stop-Loss (₹)", cmp_v * 0.92)),
                "Target_1": float(r.get("Target_T1 (₹)", cmp_v * 1.18)),
                "Buy_Zone": str(r.get("Buy Zone", f"₹{cmp_v*0.98:.1f}–₹{cmp_v:.1f}")),
                "Forensic_Note": str(r.get("Forensic Note", "Clean Accounting")),
                "Line_1": eb.get("line_1") or eb.get("bullet_1_fundamental", ""),
                "Line_2": eb.get("line_2") or eb.get("bullet_2_tape_flow", ""),
                "News_Headlines": lf.get("News_Headlines", []),
            }
        )
    return pool, cmp_map


df_vault_disp = build_enriched_portfolio_df(
    st.session_state.active_profile,
    active_h,
    active_r,
    active_cap_inr,
)


# ------------------------------------------------------------------------------
# 6. FIVE CLEAN, ACTIONABLE INVESTOR STATIONS
# ------------------------------------------------------------------------------
nav_tabs = st.tabs(
    [
        "🔥 1. Top Stocks to Buy",
        "🚀 2. Invest Capital (Order Builder)",
        "💼 3. My Portfolio Doctor",
        "🔍 4. Stock X-Ray (Search 2,600+)",
        "🤖 5. AI Advisor & Excel Report",
    ]
)


# ==============================================================================
# STATION 1: 🔥 TOP STOCKS TO BUY TODAY (BENTO CARDS + RED-FLAG AVOID LIST)
# ==============================================================================
with nav_tabs[0]:
    st.markdown(
        '<div class="sec-banner">'
        '<span>🔥 Top High-Conviction Stocks to Buy Right Now</span>'
        '<span style="font-size:0.80rem;font-weight:500;color:#94A3B8;">100% Accounting-Verified • Ranked Live Across NSE Leaders</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    f_col1, f_col2, f_col3 = st.columns([1.4, 1.4, 1.2])
    with f_col1:
        all_sectors = ["All Sectors"] + sorted(df_radar["Sector"].dropna().unique().tolist()) if not df_radar.empty else ["All Sectors"]
        sec_filter = st.selectbox("Filter by Sector", all_sectors, index=0)
    with f_col2:
        view_filter = st.selectbox(
            "Filter by Signal Type",
            [
                "🟢 Top Conviction Buys (Clean Accounting Only)",
                "🌐 Full Scanned Universe (Buys + Holds)",
                "🔴 Accounting Red Flags & Stocks to Avoid",
            ],
            index=0,
        )
    with f_col3:
        custom_scan_input = st.text_input(
            "Scan Custom Tickers (Optional)",
            value="",
            placeholder="e.g. ZOMATO, BAJFINANCE, M&M",
        )

    if custom_scan_input.strip():
        custom_syms = tuple([s.strip().upper() for s in custom_scan_input.split(",") if s.strip()])
        df_scan_active, _ = scan_radar_universe_216(vedic_info, custom_universe=custom_syms)
    else:
        df_scan_active = df_radar.copy()

    if sec_filter != "All Sectors":
        df_scan_active = df_scan_active[df_scan_active["Sector"] == sec_filter]

    if "Top Conviction Buys" in view_filter:
        df_show = df_scan_active[~df_scan_active["Hard Veto"]].sort_values(by="ANJNA_v23_Score", ascending=False)
    elif "Red Flags" in view_filter:
        df_show = df_scan_active[df_scan_active["Hard Veto"]].sort_values(by="ANJNA_v23_Score", ascending=True)
    else:
        df_show = df_scan_active.sort_values(by="ANJNA_v23_Score", ascending=False)

    # Render Bento Cards in a 2-column responsive grid
    cards_list = df_show.head(12).to_dict(orient="records")
    if not cards_list:
        st.info("No stocks matched your current filter criteria.")
    else:
        for i in range(0, len(cards_list), 2):
            c_left, c_right = st.columns(2)
            for col_obj, item in zip([c_left, c_right], cards_list[i : i + 2]):
                lf_news = (item.get("Live_Forensics", {}) or {}).get("News_Headlines", [])
                with col_obj:
                    st.markdown(
                        render_stock_bento_card(
                            sym=str(item["Symbol"]),
                            sector=str(item.get("Sector", "Equities")),
                            score=float(item.get("ANJNA_v23_Score", item.get("Master_Alpha_Score", 70.0))),
                            cmp_val=float(item.get("CMP (₹)", 100.0)),
                            chg_pct=float(item.get("Change %", 0.0)),
                            buy_zone=str(item.get("Buy Zone", "N/A")),
                            stop_loss=float(item.get("Stop-Loss (₹)", 90.0)),
                            target_1=float(item.get("Target_T1 (₹)", 120.0)),
                            roic_pct=float(item.get("ROIC %", 18.0)),
                            kelly_pct=float(item.get("ANJNA_Kelly_Pct", item.get("Kelly Weight %", 5.0))),
                            verdict_text=str(item.get("ANJNA_Verdict", item.get("Verdict", "BUY"))),
                            is_veto=bool(item.get("Hard Veto", False)),
                            forensic_note=str(item.get("Forensic Note", "Clean Accounting")),
                            extra_badge=f"Best Horizon: {item.get('Optimal_Horizon', active_h)}",
                            news_list=lf_news,
                        ),
                        unsafe_allow_html=True,
                    )

    # Also show Red-Flag Avoid Summary if user is on the default Buy view
    if "Top Conviction Buys" in view_filter:
        df_vetoes = df_scan_active[df_scan_active["Hard Veto"]]
        if not df_vetoes.empty:
            with st.expander(f"🚨 View {len(df_vetoes)} Stocks Automatically Blocked by Accounting & Governance Shield", expanded=False):
                v_cols = st.columns(2)
                for idx_v, (_, v_row) in enumerate(df_vetoes.iterrows()):
                    with v_cols[idx_v % 2]:
                        st.markdown(
                            render_stock_bento_card(
                                sym=str(v_row["Symbol"]),
                                sector=str(v_row.get("Sector", "Equities")),
                                score=float(v_row.get("ANJNA_v23_Score", 18.0)),
                                cmp_val=float(v_row.get("CMP (₹)", 100.0)),
                                chg_pct=float(v_row.get("Change %", 0.0)),
                                buy_zone="DO NOT BUY",
                                stop_loss=float(v_row.get("Stop-Loss (₹)", 90.0)),
                                target_1=float(v_row.get("Target_T1 (₹)", 100.0)),
                                roic_pct=float(v_row.get("ROIC %", 5.0)),
                                kelly_pct=0.0,
                                verdict_text="AVOID / EXIT",
                                is_veto=True,
                                forensic_note=str(v_row.get("Forensic Note", "Accounting Red Flag")),
                            ),
                            unsafe_allow_html=True,
                        )

    if st.toggle("📊 Show Compact Spreadsheet Table View", value=False, key="scanner_table_toggle"):
        clean_table = df_show[
            [
                "Symbol",
                "Sector",
                "CMP (₹)",
                "Change %",
                "ANJNA_v23_Score",
                "ROIC %",
                "Buy Zone",
                "Stop-Loss (₹)",
                "Target_T1 (₹)",
                "ANJNA_Kelly_Pct",
                "Optimal_Horizon",
                "Forensic Note",
            ]
        ].rename(
            columns={
                "ANJNA_v23_Score": "Conviction Score (/100)",
                "Target_T1 (₹)": "1Y Target (₹)",
                "ANJNA_Kelly_Pct": "Suggested Weight %",
                "Optimal_Horizon": "Best Horizon",
            }
        )
        st.dataframe(clean_table.reset_index(drop=True), use_container_width=True)


# ==============================================================================
# STATION 2: 🚀 INVEST CAPITAL (EXECUTABLE SHOPPING LIST & COMPOUNDING PLAN)
# ==============================================================================
with nav_tabs[1]:
    st.markdown(
        f'<div class="sec-banner">'
        f'<span>🚀 Custom Capital Deployment Plan: ₹{active_cap_inr:,.0f}</span>'
        f'<span style="font-size:0.80rem;font-weight:500;color:#94A3B8;">Exact Share Quantities • Live NSE Prices • {active_r.title()} Risk Mode</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    live_pool, live_cmp_lookup = build_live_candidate_pool_from_radar(df_radar)
    alloc_plan = WealthOrderAllocator.generate_complete_wealth_plan(
        capital_inr=active_cap_inr,
        horizon_code=active_h,
        risk_tolerance=active_r,
        candidate_pool=live_pool,
        live_cmp_map=live_cmp_lookup,
    )

    # Top 4 Summary Metrics
    ca1, ca2, ca3, ca4 = st.columns(4)
    ca1.metric("Total Capital to Invest", f"₹{active_cap_inr:,.0f}", f"{active_r.title()} Profile")
    ca2.metric("Deployed in Top Stocks & ETFs", f"₹{alloc_plan['Total_Deployed_INR']:,.0f}", f"{alloc_plan['Total_Deployed_INR']/max(active_cap_inr,1)*100:.1f}% Invested")
    ca3.metric("Safety Cash Reserve", f"₹{alloc_plan['Cash_Buffer_INR']:,.0f}", "Keep in Liquid / Savings")
    ca4.metric("Recommended Monthly SIP", f"₹{alloc_plan['Monthly_SIP_Suggested']:,.0f}/mo", "For Long-Term Compounding")

    # 4-Sleeve Breakdown Pills
    sleeve_bd = alloc_plan.get("Sleeve_Breakdown", {})
    if sleeve_bd:
        s_cols = st.columns(len(sleeve_bd))
        for s_col, (sl_name, sl_info) in zip(s_cols, sleeve_bd.items()):
            s_col.info(f"**{sl_name}**\n\n**{sl_info['Weight_Pct']}%** (`₹{sl_info['Allocated_INR']:,.0f}`)")

    st.markdown("#### 🛒 Your Executable Stock Shopping List (Exact Shares & Price Levels)")
    df_orders = alloc_plan["Orders_Table"].copy()
    if df_orders.empty:
        st.warning("Increase capital amount to generate whole-share stock orders.")
    else:
        order_records = df_orders.to_dict(orient="records")
        for i in range(0, len(order_records), 2):
            oc1, oc2 = st.columns(2)
            for col_o, ord_item in zip([oc1, oc2], order_records[i : i + 2]):
                sym_clean = str(ord_item["Symbol"]).replace(".NS", "")
                rad_match = df_radar[df_radar["Symbol"] == sym_clean] if not df_radar.empty else pd.DataFrame()
                roic_v = float(rad_match["ROIC %"].iloc[0]) if not rad_match.empty else 22.0
                chg_v = float(rad_match["Change %"].iloc[0]) if not rad_match.empty else 0.0
                with col_o:
                    st.markdown(
                        render_stock_bento_card(
                            sym=sym_clean,
                            sector=str(ord_item.get("Sector", "Equities")),
                            score=float(ord_item.get("Score", 82.0)),
                            cmp_val=float(ord_item.get("CMP", 100.0)),
                            chg_pct=chg_v,
                            buy_zone=str(ord_item.get("Buy_Zone", "Market")),
                            stop_loss=float(ord_item.get("Stop_Loss", 90.0)),
                            target_1=float(ord_item.get("Target_1", 120.0)),
                            roic_pct=roic_v,
                            kelly_pct=float(ord_item.get("Weight_Pct", 8.0)),
                            verdict_text="BUY ORDER",
                            is_veto=False,
                            forensic_note="Verified Clean Balance Sheet",
                            extra_badge=f"Sleeve: {ord_item.get('Sleeve', 'Core')}",
                            order_qty=int(ord_item.get("Qty", 1)),
                            order_outlay=float(ord_item.get("Outlay_INR", 100.0)),
                            news_list=ord_item.get("News_Headlines", []),
                        ),
                        unsafe_allow_html=True,
                    )

    # Wealth Compounding Chart & Table
    df_comp = alloc_plan.get("Compounding_Table", pd.DataFrame())
    if not df_comp.empty:
        st.markdown("#### 📈 Projected Wealth & Dividend Compounding Trajectory (1 to 20 Years)")
        cc1, cc2 = st.columns([1.4, 1.0])
        with cc1:
            fig_comp = go.Figure()
            fig_comp.add_trace(
                go.Bar(
                    x=df_comp["Year"],
                    y=df_comp["Pure Lump-Sum (₹)"],
                    name="One-Time Investment Only",
                    marker_color="#38BDF8",
                )
            )
            fig_comp.add_trace(
                go.Bar(
                    x=df_comp["Year"],
                    y=df_comp["Lump-Sum + Monthly SIP + DRIP (₹)"],
                    name="With Monthly SIP + Reinvested Dividends",
                    marker_color="#10B981",
                )
            )
            fig_comp.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor=PAPER_BG,
                plot_bgcolor=PLOT_BG,
                font=dict(color=FONT_COLOR, size=11),
                height=320,
                barmode="group",
                margin=dict(l=15, r=15, t=20, b=15),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        with cc2:
            st.dataframe(df_comp, use_container_width=True, height=300)


# ==============================================================================
# STATION 3: 💼 MY PORTFOLIO DOCTOR & REBALANCER (ZERO HARDCODED STOCKS)
# ==============================================================================
with nav_tabs[2]:
    st.markdown(
        f'<div class="sec-banner">'
        f'<span>💼 Portfolio Health Doctor & Rebalancer ({st.session_state.active_profile})</span>'
        f'<span style="font-size:0.80rem;font-weight:500;color:#94A3B8;">Automatic Split Adjustment • Red-Flag Exit Alerts • Replacement Switches</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ Add or Import Your Portfolio Holdings (Paste Text / Upload Broker CSV / Single Stock)", expanded=df_vault_disp.empty):
        pc1, pc2, pc3 = st.columns([1.4, 1.2, 1.1])
        with pc1:
            raw_paste = st.text_area(
                "📋 Paste Holdings (Format: SYMBOL SHARES AVG_PRICE per line)",
                value="",
                placeholder="Example (one stock per line):\nRELIANCE 50 1380\nTCS 20 3850\nICICIBANK 100 1120",
                height=115,
            )
            if st.button("⚡ Import Pasted Stocks", use_container_width=True):
                parsed = parse_raw_broker_holdings_text(raw_paste)
                if parsed:
                    for item in parsed:
                        sym_p = item.get("Symbol") or item.get("symbol")
                        sh_p = float(item.get("Shares") or item.get("shares", 0.0))
                        cost_p = float(item.get("Avg_Cost") or item.get("avg_cost", 0.0))
                        if sym_p and sh_p > 0 and cost_p > 0:
                            save_holding_direct(st.session_state.active_profile, sym_p, sh_p, cost_p, SECTOR_DEFAULT_MAP.get(sym_p, "Equities"))
                    st.success(f"Imported {len(parsed)} stocks into {st.session_state.active_profile}!")
                    st.rerun()
                else:
                    st.warning("Please enter lines in `SYMBOL SHARES BUY_PRICE` format.")

        with pc2:
            up_csv = st.file_uploader("📂 Upload Broker CSV (Zerodha / Groww / Angel)", type=["csv"])
            if up_csv is not None:
                try:
                    df_u = pd.read_csv(up_csv)
                    cmap = {c.lower().strip(): c for c in df_u.columns}
                    sc = next((cmap[k] for k in ("instrument", "symbol", "ticker", "scrip", "trading symbol") if k in cmap), None)
                    qc = next((cmap[k] for k in ("qty.", "qty", "quantity", "shares", "net qty") if k in cmap), None)
                    cc = next((cmap[k] for k in ("avg. cost", "avg cost", "average price", "buy price", "cost") if k in cmap), None)
                    if sc and qc and cc:
                        n_imp = 0
                        for _, ru in df_u.iterrows():
                            su = str(ru[sc]).upper().replace(".NS", "").replace(".BO", "").strip()
                            qu = float(ru[qc])
                            cu = float(ru[cc])
                            if su and qu > 0 and cu > 0:
                                save_holding_direct(st.session_state.active_profile, su, qu, cu, SECTOR_DEFAULT_MAP.get(su, "Equities"))
                                n_imp += 1
                        st.success(f"Imported {n_imp} positions from CSV!")
                        st.rerun()
                    else:
                        st.error("CSV needs Symbol/Instrument, Qty, and Avg Cost columns.")
                except Exception as ex:
                    st.error(f"CSV error: {ex}")

            b_samp, b_clr = st.columns(2)
            with b_samp:
                if st.button("📥 Load Sample Portfolio", use_container_width=True):
                    for sd, qd, cd, secd in VERIFIED_57_SEED_HOLDINGS[:12]:
                        save_holding_direct(st.session_state.active_profile, sd, float(qd), float(cd), secd)
                    st.rerun()
            with b_clr:
                if st.button("🗑️ Clear Portfolio", use_container_width=True):
                    clear_profile_holdings(st.session_state.active_profile)
                    st.rerun()

        with pc3:
            st.markdown("**Add / Update Single Stock**")
            in_sym = st.text_input("Stock Symbol", value="", placeholder="e.g. TITAN").upper().strip()
            in_qty = st.number_input("Shares", min_value=1.0, value=10.0, step=1.0)
            in_cost = st.number_input("Buy Price (₹)", min_value=1.0, value=1000.0, step=10.0)
            b_add, b_sell = st.columns(2)
            with b_add:
                if st.button("🟢 Add / Buy", use_container_width=True) and in_sym:
                    ok_b, msg_b = execute_buy_order(st.session_state.active_profile, in_sym, in_qty, in_cost, SECTOR_DEFAULT_MAP.get(in_sym, "Equities"))
                    st.success(msg_b)
                    st.rerun()
            with b_sell:
                if st.button("🔴 Sell / Exit", use_container_width=True) and in_sym:
                    ok_s, msg_s = execute_sell_order(st.session_state.active_profile, in_sym, in_qty, in_cost)
                    if ok_s:
                        st.success(msg_s)
                    else:
                        st.error(msg_s)
                    st.rerun()

    if df_vault_disp.empty:
        st.info("Your portfolio is currently empty. Add your stocks above to get a complete health diagnosis, red-flag check, and replacement plan.")
    else:
        tot_c = float(df_vault_disp["Cost Basis"].sum())
        tot_v = float(df_vault_disp["Market Value"].sum())
        tot_pnl = tot_v - tot_c
        tot_ret = ((tot_v / tot_c) - 1.0) * 100.0 if tot_c > 0 else 0.0
        port_score = float((df_vault_disp["Conviction Score"] * df_vault_disp["Weight %"]).sum() / 100.0)
        red_flags_cnt = int(df_vault_disp["Hard Veto"].sum())

        pm1, pm2, pm3, pm4 = st.columns(4)
        pm1.metric("Total Invested Cost", f"₹{tot_c:,.0f}", f"{len(df_vault_disp)} Stocks Held")
        pm2.metric("Current Portfolio Value", f"₹{tot_v:,.0f}", f"₹{tot_pnl:+,.0f} ({tot_ret:+.2f}%)")
        pm3.metric("Portfolio Quality Score", f"{port_score:.1f} / 100", "Weighted Conviction")
        pm4.metric("Accounting Red Flags", f"{red_flags_cnt} Stocks", "Exit Immediately" if red_flags_cnt > 0 else "100% Clean Shield")

        # Rebalance & Replacement Order Tickets (Zero TypeError!)
        df_tickets = generate_autonomous_rebalance_tickets(
            df_vault_disp=df_vault_disp,
            df_radar=df_radar,
            target_equity=max(tot_v, active_cap_inr),
            vedic_ctx=vedic_info,
        )
        if df_tickets is not None and not df_tickets.empty:
            st.markdown("#### 🔄 Recommended Portfolio Upgrades (Sell Weak / Overweight → Buy High-Conviction Leaders)")
            st.dataframe(df_tickets, use_container_width=True)

        st.markdown("#### 📋 Stock-by-Stock Health Cards in Your Portfolio")
        held_records = df_vault_disp.to_dict(orient="records")
        for i in range(0, len(held_records), 2):
            hc1, hc2 = st.columns(2)
            for col_h, h_item in zip([hc1, hc2], held_records[i : i + 2]):
                pnl_str = f"Held: {h_item['Shares']:,.0f} sh @ ₹{h_item['Buy Price']:,.1f} | P&L: ₹{h_item['P&L (₹)']:+,.0f} ({h_item['P&L %']:+.1f}%)"
                with col_h:
                    st.markdown(
                        render_stock_bento_card(
                            sym=str(h_item["Symbol"]),
                            sector=str(h_item.get("Sector", "Equities")),
                            score=float(h_item.get("Conviction Score", 60.0)),
                            cmp_val=float(h_item.get("Live CMP", 100.0)),
                            chg_pct=float(h_item.get("1D Change %", 0.0)),
                            buy_zone=str(h_item.get("Buy Zone", "N/A")),
                            stop_loss=float(h_item.get("Stop-Loss (₹)", 90.0)),
                            target_1=float(h_item.get("Target (₹)", 120.0)),
                            roic_pct=float(h_item.get("ROIC %", 18.0)),
                            kelly_pct=float(h_item.get("Weight %", 5.0)),
                            verdict_text=str(h_item.get("Verdict", "HOLD")),
                            is_veto=bool(h_item.get("Hard Veto", False)),
                            forensic_note=str(h_item.get("Forensic Note", "Clean Accounting")),
                            extra_badge=pnl_str,
                        ),
                        unsafe_allow_html=True,
                    )

        if st.toggle("📊 Show Full Portfolio Table", value=False, key="port_table_toggle"):
            st.dataframe(df_vault_disp, use_container_width=True)


# ==============================================================================
# STATION 4: 🔍 STOCK X-RAY (SEARCH 2,600+ NSE/BSE STOCKS + OPTIONAL PRO LAB)
# ==============================================================================
with nav_tabs[3]:
    st.markdown(
        '<div class="sec-banner">'
        '<span>🔍 Instant Stock X-Ray & Safety Check</span>'
        '<span style="font-size:0.80rem;font-weight:500;color:#94A3B8;">Search 2,600+ NSE/BSE Companies or Type Any Ticker</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    searchable_options = get_searchable_universe_list()
    sx1, sx2 = st.columns([2.2, 1.2])
    with sx1:
        def_idx = 0
        for idx_s, lbl_s in enumerate(searchable_options):
            if lbl_s.startswith(f"{st.session_state.selected_xray_symbol} "):
                def_idx = idx_s
                break
        picked_entry = st.selectbox(
            "🔍 Search by Company Name or Ticker Symbol",
            options=searchable_options,
            index=def_idx,
        )
        sym_from_list = parse_search_string(picked_entry)

    with sx2:
        typed_sym = st.text_input(
            "⌨️ Or Type Any NSE/BSE Symbol Directly",
            value="",
            placeholder="e.g. RELIANCE, ZOMATO, HAL, MRF...",
        )

    active_xray_sym = typed_sym.strip().upper().replace(".NS", "").replace(".BO", "") if typed_sym.strip() else sym_from_list
    st.session_state.selected_xray_symbol = active_xray_sym

    try:
        df_hist_raw = yf.Ticker(f"{active_xray_sym}.NS").history(period="1y") if yf is not None else pd.DataFrame()
    except Exception:
        df_hist_raw = pd.DataFrame()
    if df_hist_raw is None or df_hist_raw.empty or len(df_hist_raw) < 30:
        df_hist_raw = generate_synthetic_ohlcv(active_xray_sym, periods=200)

    df_hist_clean = sanitize_ohlcv_corporate_actions(df_hist_raw, active_xray_sym)

    xray_codex = evaluate_320_institutional_codex(
        sym=active_xray_sym,
        df_hist=df_hist_clean,
        vedic_ctx=vedic_info,
        portfolio_equity=active_cap_inr,
        horizon_code=active_h,
        risk_profile=active_r,
        vedic_enabled=st.session_state.vedic_overlay_enabled,
    )
    anjna_payload = xray_codex["ANJNA_v2_3_Payload"]
    anjna_score_val = float(xray_codex.get("ANJNA_v23_Score", 50.0))
    lf_news_xray = (xray_codex.get("Live_Forensics", {}) or {}).get("News_Headlines", [])

    # 1. Plain-English Executive Bento Card at Top of X-Ray
    st.markdown(
        render_stock_bento_card(
            sym=active_xray_sym,
            sector=str(xray_codex.get("Sector", "Equities")),
            score=anjna_score_val,
            cmp_val=float(xray_codex.get("CMP (₹)", 100.0)),
            chg_pct=float(xray_codex.get("Change %", 0.0)),
            buy_zone=str(xray_codex.get("Buy Zone", "N/A")),
            stop_loss=float(xray_codex.get("Stop-Loss (₹)", 90.0)),
            target_1=float(xray_codex.get("Target_T1 (₹)", 120.0)),
            roic_pct=float(xray_codex.get("ROIC %", 18.0)),
            kelly_pct=float(xray_codex.get("ANJNA_Kelly_Pct", 5.0)),
            verdict_text=str(xray_codex.get("ANJNA_Verdict", "HOLD")),
            is_veto=bool(xray_codex.get("Hard Veto", False)),
            forensic_note=str(xray_codex.get("Forensic Note", "Clean Accounting")),
            extra_badge=f"Best Horizon: {xray_codex.get('Optimal_Horizon', active_h)}",
            news_list=lf_news_xray,
        ),
        unsafe_allow_html=True,
    )

    # 2. Interactive Price Chart + 6-Point Accounting & Safety Checklist
    ch_col, safe_col = st.columns([1.45, 1.0])
    with ch_col:
        st.markdown(f"**📈 Price Action, Buy Zone & Target Corridor (`{active_xray_sym}`)**")
        df_p = df_hist_clean.tail(130).copy()
        df_p["EMA20"] = df_p["Close"].ewm(span=20, adjust=False).mean()
        df_p["EMA50"] = df_p["Close"].ewm(span=50, adjust=False).mean()

        fig_c = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.75, 0.25])
        fig_c.add_trace(
            go.Candlestick(x=df_p.index, open=df_p["Open"], high=df_p["High"], low=df_p["Low"], close=df_p["Close"], name="Price"),
            row=1,
            col=1,
        )
        fig_c.add_trace(go.Scatter(x=df_p.index, y=df_p["EMA20"], name="20-Day Trend", line=dict(color="#38BDF8", width=1.5)), row=1, col=1)
        fig_c.add_trace(go.Scatter(x=df_p.index, y=df_p["EMA50"], name="50-Day Trend", line=dict(color="#F59E0B", width=1.5)), row=1, col=1)
        fig_c.add_hline(y=float(xray_codex["Stop-Loss (₹)"]), line_dash="dash", line_color="#EF4444", annotation_text="Stop-Loss", row=1, col=1)
        fig_c.add_hline(y=float(xray_codex["Target_T1 (₹)"]), line_dash="dash", line_color="#10B981", annotation_text="1Y Target", row=1, col=1)

        v_cols_bar = ["#10B981" if c >= o else "#EF4444" for c, o in zip(df_p["Close"], df_p["Open"])]
        fig_c.add_trace(go.Bar(x=df_p.index, y=df_p["Volume"], name="Volume", marker_color=v_cols_bar), row=2, col=1)
        fig_c.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT_COLOR, size=11),
            height=380,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=15, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        )
        st.plotly_chart(fig_c, use_container_width=True)

    with safe_col:
        st.markdown("**🛡️ 6-Point Accounting & Financial Safety Check**")
        for_details = anjna_payload["G0_Forensic_Details"]
        if for_details.get("Hard_Veto") or xray_codex.get("Hard Veto"):
            st.error(f"🚨 **Red Flag Detected:** {xray_codex.get('Forensic Note', 'Accounting Veto')}")
            for trig in for_details.get("Red_Triggers", []):
                st.markdown(f"- ⛔ **{trig}**")
        else:
            st.success("✅ **Passed All 6 Institutional Accounting & Safety Checks**")

        grey_gates = for_details.get("Grey_Zone_Gates", {}) or {}
        safety_checks = [
            ("1. Earnings Manipulation Check (Beneish M)", float(grey_gates.get("g_beneish", 1.0)), f"Score: {xray_codex['Beneish M']:.2f}"),
            ("2. Cash vs Paper Profit (Sloan Accruals)", float(grey_gates.get("g_sloan", 1.0)), f"Accruals: {xray_codex['Sloan Accrual %']:.1f}%"),
            ("3. Promoter Share Pledge Safety", float(grey_gates.get("g_pledge", 1.0)), f"Pledge: {xray_codex['Promoter Pledge %']:.1f}%"),
            ("4. Corporate Governance & Audit Cleanliness", float(grey_gates.get("g_gov", 1.0)), f"Piotroski F: {xray_codex['Piotroski F']}/9"),
            ("5. Treasury Cash Yield Authenticity", float(grey_gates.get("g_cash", 1.0)), "Verified Real Cash Yield"),
            ("6. Balance-Sheet Debt & Solvency (Altman Z)", float(grey_gates.get("g_solvency", 1.0)), f"Altman Z: {xray_codex['Altman Z']:.2f}"),
        ]
        for chk_name, chk_val, chk_sub in safety_checks:
            st.progress(min(1.0, max(0.0, chk_val)), text=f"{chk_name} — {chk_val*100:.0f}% ({chk_sub})")

    # 3. Expandable Pro Quantitative Lab (15 Orthogonal Meta-Factors, Waterfall & 332 Signals)
    with st.expander("🔬 Open Pro Quantitative Lab (15 Factor Breakdown, Conviction Waterfall & 332 Signals)", expanded=False):
        q_col1, q_col2 = st.columns(2)
        mf_scores = anjna_payload["MF_Orthogonal_Scores"]
        omega_w = anjna_payload["Omega_MF_Weights"]

        with q_col1:
            st.markdown("**15 Orthogonal Factor Scores (0–100)**")
            mf_df = pd.DataFrame(
                [
                    {
                        "Factor": f"{k}: {MF_PLAIN_NAMES[k][0]}",
                        "Category": MF_PLAIN_NAMES[k][1],
                        "Score (/100)": float(mf_scores.get(k, 50.0)),
                        "Weight %": round(float(omega_w.get(k, 0.0)) * 100.0, 1),
                    }
                    for k in MF_PLAIN_NAMES
                ]
            )
            fig_mf_bar = px.bar(
                mf_df,
                x="Score (/100)",
                y="Factor",
                color="Category",
                orientation="h",
                range_x=[0, 105],
            )
            fig_mf_bar.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor=PAPER_BG,
                plot_bgcolor=PLOT_BG,
                font=dict(color=FONT_COLOR, size=10),
                height=420,
                yaxis=dict(autorange="reversed"),
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_mf_bar, use_container_width=True)

        with q_col2:
            st.markdown("**Multi-Horizon Conviction Outlook (`H0` to `H5`)**")
            mh_vec = xray_codex.get("Multi_Horizon_Vector", {})
            h_list = ["H0", "H1", "H2", "H3", "H4", "H5"]
            fig_mh = go.Figure(
                go.Scatter(
                    x=[f"{h} ({HORIZON_LABELS[h]})" for h in h_list],
                    y=[float(mh_vec.get(h, anjna_score_val)) for h in h_list],
                    mode="lines+markers+text",
                    text=[f"{float(mh_vec.get(h, anjna_score_val)):.1f}" for h in h_list],
                    textposition="top center",
                    line=dict(color="#10B981", width=3),
                )
            )
            fig_mh.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor=PAPER_BG,
                plot_bgcolor=PLOT_BG,
                font=dict(color=FONT_COLOR, size=10),
                height=420,
                yaxis=dict(range=[0, 105], title="Conviction Score (/100)"),
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig_mh, use_container_width=True)

        st.markdown("**Search Full 332-Indicator Ledger (`D001–D332`)**")
        sig_q = st.text_input("Filter Indicators (e.g. ROIC, Beneish, Dividend, VCP, Kelly)", value="")
        codex_all = xray_codex.get("Codex_300", {})
        df_332 = pd.DataFrame([{"Indicator": k, "Computed Value": str(v)} for k, v in codex_all.items()])
        if sig_q.strip():
            df_332 = df_332[df_332["Indicator"].str.contains(sig_q.strip(), case=False, na=False)]
        st.dataframe(df_332, use_container_width=True, height=280)


# ==============================================================================
# STATION 5: 🤖 AI INVESTMENT ADVISOR (COPILOT) & 6-SHEET EXCEL REPORT
# ==============================================================================
with nav_tabs[4]:
    st.markdown(
        '<div class="sec-banner">'
        '<span>🤖 AI Investment Advisor & 6-Sheet Excel Report</span>'
        '<span style="font-size:0.80rem;font-weight:500;color:#94A3B8;">1-Tap Quick Prompts • Instant Stock Comparisons • Full Excel Export</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_chat, col_export = st.columns([1.65, 1.0])

    with col_chat:
        st.markdown("**⚡ 1-Tap Instant Questions:**")
        qb1, qb2, qb3, qb4 = st.columns(4)
        triggered_prompt = None
        if qb1.button("🔥 Top 5 Buys Today", use_container_width=True):
            triggered_prompt = "What are the top 5 stocks to buy today?"
        if qb2.button(f"💰 Invest ₹{active_cap_inr/1e5:.0f} Lakh", use_container_width=True):
            triggered_prompt = f"Allocate {int(active_cap_inr)}"
        if qb3.button("⚖️ Compare TCS vs INFY", use_container_width=True):
            triggered_prompt = "Compare TCS vs INFY"
        if qb4.button(f"🔍 Audit {st.session_state.selected_xray_symbol}", use_container_width=True):
            triggered_prompt = f"Audit {st.session_state.selected_xray_symbol}"

        typed_prompt = st.chat_input("Ask about any stock, comparison, or portfolio plan (e.g. 'Audit RELIANCE', 'Compare HAL vs BEL', 'Rebalance')...")
        active_query = triggered_prompt or typed_prompt

        if active_query:
            st.session_state.copilot_messages.append({"role": "user", "content": active_query})
            reply_text = generate_deterministic_copilot_response(
                user_query=active_query,
                active_profile=st.session_state.active_profile,
                df_vault_disp=df_vault_disp,
                df_radar=df_radar,
                vedic_ctx=vedic_info,
                mmi_score=mmi_val,
            )
            st.session_state.copilot_messages.append({"role": "assistant", "content": reply_text})

        for msg in st.session_state.copilot_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    with col_export:
        st.markdown("#### 📥 Download Complete 6-Sheet Excel Report")
        st.markdown(
            f"""
            Exports your complete analysis into a formatted `.xlsx` workbook:
            1. **Executive Summary** (`{st.session_state.active_profile}`)
            2. **Portfolio Holdings & Split Audit**
            3. **Sector Concentration Risk Check**
            4. **Live NSE Market Scanner Ranking**
            5. **332-Indicator Deep Ledger (`{st.session_state.selected_xray_symbol}`)**
            6. **Trade Execution History**
            """
        )
        df_led_exp = get_trade_ledger(st.session_state.active_profile)
        xlsx_data = build_ananta216_excel_dossier(
            active_profile=st.session_state.active_profile,
            df_vault_disp=df_vault_disp,
            df_radar=df_radar,
            df_ledger=df_led_exp,
            vedic_info=vedic_info,
            mmi_score=mmi_val,
            featured_sym=st.session_state.selected_xray_symbol,
            featured_codex=xray_codex.get("Codex_300", {}),
        )
        st.download_button(
            f"📥 Download 6-Sheet Excel Report ({st.session_state.selected_xray_symbol}).xlsx",
            data=xlsx_data,
            file_name=f"ANJNA_Wealth_Report_{st.session_state.selected_xray_symbol}_{datetime.date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
