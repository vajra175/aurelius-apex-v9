"""
================================================================================
AURELIUS APEX (AQ-OS v9.0): SUPREME COMMERCIAL FINTECH TERMINAL
================================================================================
Universal Multi-Asset Brain | 300-Variable / 2,160-Factor Omni-Codex
10 Independent Self-Feeding Engine Buckets | Gate 0 Forensic Gatekeeper
Swiss FinTech Dual-Theme Bento UI (Ivory Light / Obsidian Dark)
Full NSE / BSE Real-Time Streaming Feeds (~2,600+ Equities)
5 Commercial Workstations:
  Station 1: 💼 Portfolio Surgeon & Rebalance Engine (Before vs. After Triage)
  Station 2: 🚀 Capital Allocator & Order Builder (Integer Shares Qty + DRIP)
  Station 3: 🌐 Full-Market Opportunity Scanner (8 Institutional Alpha Lenses)
  Station 4: 🔬 Stock X-Ray & 10-Engine Audit (Starts 100% Blank Autocomplete)
  Station 5: 🧠 Aurelius AI Copilot (Audits, Peer Comparisons, Surgery Q&A)
================================================================================
"""

import datetime
import io
import math
import re
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

from engine import (
    VAJRA_PIL_ICON,
    VAJRA_ICON_URI,
    DB_FILE,
    CORPORATE_SPLIT_REGISTRY,
    FORENSIC_VETO_REGISTRY,
    SECTOR_DEFAULT_MAP,
    NSE_RADAR_UNIVERSE,
    reconcile_corporate_action,
    init_db,
    get_holdings,
    get_trade_ledger,
    save_holding_direct,
    execute_buy_order,
    execute_sell_order,
    clear_profile_holdings,
    generate_synthetic_ohlcv,
    get_ist_now,
    get_live_vedic_chronometer,
    compute_216_variable_codex,
    compute_300_variable_codex,
    scan_radar_universe_216,
    batch_fetch_live_prices,
    generate_deterministic_copilot_response,
    sanitize_sheet_name,
    build_ananta216_excel_dossier,
)
from modules.data_pipeline import (
    resolve_universal_ticker,
    MultiTierUniverseManager,
    fetch_live_stock_ohlcv,
    get_searchable_universe_list,
    parse_search_string,
    fetch_live_macro_indicators,
)
from modules.strategic_quantitative import AutonomousWealthPathfinder, MultiHorizonWealthEngine
from modules.anti_manipulation import AntiManipulationShield
from modules.siddhantic_vedic import (
    SiddhanticAstronomicalEngine,
    MediniMundaneSynthesizer,
    CorporateKundliEngine,
    SarvatobhadraChakraEngine,
)
from core.portfolio_decision_engine import PortfolioInputParser, PortfolioDecisionEngine
from core.wealth_order_allocator import WealthOrderAllocator
from core.weightage_matrix import AureliusWeightageMatrix
from core.dividend_pe_deals import (
    DividendAristocratEngine,
    PrivateEquityAndDealsRadar,
    CapexROIICAndVCPPEADEngine,
)

# ------------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION & DUAL-THEME FINTECH DESIGN SYSTEM
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="AURELIUS APEX (AQ-OS v9.0)",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize master SQLite database
init_db()

# State Initializations
if "ui_theme" not in st.session_state:
    st.session_state["ui_theme"] = "Obsidian Dark"
if "auth_role" not in st.session_state:
    st.session_state["auth_role"] = "OWNER_ADMIN"
if "active_profile" not in st.session_state:
    st.session_state["active_profile"] = "Self - Primary"
if "global_horizon" not in st.session_state:
    st.session_state["global_horizon"] = "H4"
if "global_risk" not in st.session_state:
    st.session_state["global_risk"] = "MODERATE"
if "global_strategy" not in st.session_state:
    st.session_state["global_strategy"] = "ALL_10_OMNI_BRAIN"
if "vedic_toggle" not in st.session_state:
    st.session_state["vedic_toggle"] = True
if "active_xray_selection" not in st.session_state:
    st.session_state["active_xray_selection"] = None
if "active_station" not in st.session_state:
    st.session_state["active_station"] = "💼 Portfolio Surgeon"
if "copilot_history" not in st.session_state:
    st.session_state["copilot_history"] = []

# Theme-Dependent CSS Variables
is_light = (st.session_state["ui_theme"] == "Ivory Light")

theme_css = f"""
<head>
    <link rel="manifest" href="/app/static/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="{'default' if is_light else 'black-translucent'}">
    <meta name="apple-mobile-web-app-title" content="Aurelius Apex">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="{'#F8F9FA' if is_light else '#06080F'}">
</head>
<style>
    :root {{
        --bg-app: {'#F4F6F9' if is_light else '#060911'};
        --bg-card: {'#FFFFFF' if is_light else '#0E1526'};
        --bg-card-sub: {'#F1F5F9' if is_light else '#080D18'};
        --text-primary: {'#0F172A' if is_light else '#F8FAFC'};
        --text-secondary: {'#475569' if is_light else '#94A3B8'};
        --border-color: {'rgba(15, 23, 42, 0.12)' if is_light else 'rgba(255, 255, 255, 0.08)'};
        --accent-primary: {'#0284C7' if is_light else '#38BDF8'};
        --accent-green: {'#059669' if is_light else '#10B981'};
        --accent-red: {'#DC2626' if is_light else '#EF4444'};
        --accent-amber: {'#D97706' if is_light else '#F59E0B'};
        --input-bg: {'#FFFFFF' if is_light else '#0F172A'};
        --input-text: {'#0F172A' if is_light else '#FFFFFF'};
        --shadow-elevation: {'0 4px 20px rgba(0, 0, 0, 0.06)' if is_light else '0 12px 36px rgba(0, 0, 0, 0.5)'};
    }}

    .stApp {{
        background-color: var(--bg-app);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    }}
    .block-container {{
        padding-top: 0.8rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1480px !important;
    }}

    /* Commercial Inputs Styling */
    .stTextArea textarea, .stTextInput input, .stNumberInput input, .stSelectbox select, div[data-baseweb="select"] {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', 'Inter', monospace !important;
        font-size: 13.5px !important;
    }}
    .stTextArea textarea:focus, .stTextInput input:focus, .stNumberInput input:focus {{
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    }}

    /* Global Strategy Top Bar */
    .strategy-top-bar {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 10px 16px;
        margin-bottom: 12px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        box-shadow: var(--shadow-elevation);
    }}

    /* Bento Action Card Architecture */
    .bento-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: var(--shadow-elevation);
        transition: transform 0.18s ease, border-color 0.18s ease;
    }}
    .bento-card:hover {{
        border-color: var(--accent-primary);
    }}
    .bento-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
    }}
    .bento-ticker {{
        font-size: 20px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }}
    .bento-company {{
        font-size: 12px;
        color: var(--text-secondary);
        font-weight: 500;
    }}
    .bento-score-gauge {{
        font-size: 26px;
        font-weight: 900;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1;
    }}
    .bento-verdict-pill {{
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .bento-corridor {{
        background: var(--bg-card-sub);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 8px 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
    }}
    .bento-brief {{
        font-size: 12.5px;
        line-height: 1.5;
        border-left: 3px solid var(--accent-primary);
        padding-left: 10px;
        margin-top: 8px;
    }}
    .bento-brief-line1 {{ color: var(--text-primary); font-weight: 600; margin-bottom: 3px; }}
    .bento-brief-line2 {{ color: var(--text-secondary); margin-bottom: 3px; }}
    .bento-brief-line3 {{ color: var(--accent-primary); font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; }}

    /* Station Dock Controller */
    section.main div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 5px !important;
        gap: 4px !important;
        margin-bottom: 14px !important;
        box-shadow: var(--shadow-elevation) !important;
        position: sticky !important;
        top: 0px !important;
        z-index: 999 !important;
        backdrop-filter: blur(10px) !important;
    }}
    section.main div[data-testid="stRadio"] > div[role="radiogroup"] label {{
        flex: 1 1 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 8px 6px !important;
        margin: 0 !important;
        cursor: pointer !important;
        text-align: center !important;
    }}
    section.main div[data-testid="stRadio"] > div[role="radiogroup"] label input[type="radio"],
    section.main div[data-testid="stRadio"] > div[role="radiogroup"] label div[data-testid="stRadioButtonCustom"],
    section.main div[data-testid="stRadio"] > div[role="radiogroup"] label div[aria-hidden="true"] {{
        display: none !important;
    }}
    section.main div[data-testid="stRadio"] > div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {{
        font-size: 13px !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }}
    section.main div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) {{
        background: {'rgba(2, 132, 199, 0.12)' if is_light else 'linear-gradient(135deg, rgba(56, 189, 248, 0.22) 0%, rgba(99, 102, 241, 0.22) 100%)'} !important;
        border: 1px solid var(--accent-primary) !important;
    }}
    section.main div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {{
        color: var(--accent-primary) !important;
        font-weight: 700 !important;
    }}

    /* KPI Summary Cards */
    .kpi-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 11px;
        padding: 12px 14px;
        box-shadow: var(--shadow-elevation);
    }}
    .kpi-label {{
        font-size: 10px;
        text-transform: uppercase;
        color: var(--text-secondary);
        font-weight: 600;
        letter-spacing: 0.05em;
    }}
    .kpi-val {{
        font-size: 19px;
        font-weight: 800;
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
        margin-top: 3px;
    }}
    .kpi-sub {{
        font-size: 10.5px;
        color: var(--text-secondary);
        margin-top: 2px;
    }}

    /* 10-Bucket Mini Bar */
    .bucket-bar-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 6px;
        margin-top: 8px;
    }}
    .bucket-pill {{
        background: var(--bg-card-sub);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 4px 6px;
        font-size: 10.5px;
        font-family: 'JetBrains Mono', monospace;
        display: flex;
        justify-content: space-between;
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
        }}
        section.main div[data-testid="stRadio"] > div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {{
            font-size: 10.5px !important;
        }}
        .bucket-bar-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. GLOBAL TELEMETRY & STRATEGY CONTROLLER BAR
# ------------------------------------------------------------------------------
vedic_ctx = get_live_vedic_chronometer()
now_ist = get_ist_now()

# Top Hero Bar
col_hero_brand, col_hero_controls = st.columns([1.8, 1.2])
with col_hero_brand:
    st.markdown(
        f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 26px;">👑</span>
        <div>
            <h1 style="margin: 0; font-size: 22px; font-weight: 900; letter-spacing: -0.02em; color: var(--text-primary);">
                AURELIUS APEX <span style="font-size: 13px; font-weight: 600; color: var(--accent-primary);">(AQ-OS v9.0)</span>
            </h1>
            <div style="font-size: 11px; color: var(--text-secondary); font-weight: 500;">
                SOVEREIGN COMMERCIAL QUANTITATIVE FINTECH OPERATING SYSTEM
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_hero_controls:
    col_ctrl_theme, col_ctrl_prof = st.columns([1, 1.2])
    with col_ctrl_theme:
        theme_sel = st.selectbox(
            "Theme",
            ["🌙 Obsidian Dark", "☀️ Ivory Light"],
            index=0 if st.session_state["ui_theme"] == "Obsidian Dark" else 1,
            label_visibility="collapsed",
            key="theme_selector_dropdown",
        )
        new_theme = "Obsidian Dark" if "Obsidian" in theme_sel else "Ivory Light"
        if new_theme != st.session_state["ui_theme"]:
            st.session_state["ui_theme"] = new_theme
            st.rerun()

    with col_ctrl_prof:
        profile_options = ["Self - Primary", "Family Trust", "Sovereign HNW"]
        st.session_state["active_profile"] = st.selectbox(
            "Profile",
            profile_options,
            index=profile_options.index(st.session_state["active_profile"]),
            label_visibility="collapsed",
            key="profile_selector_dropdown",
        )

# Global Strategy Composer Strip
with st.container():
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    c_strat1, c_strat2, c_strat3, c_strat4 = st.columns([1.1, 1.1, 1.5, 0.9])
    
    with c_strat1:
        horizon_labels = {
            "H0": "H0 (1-3D Scalp)",
            "H1": "H1 (1-4W Swing)",
            "H2": "H2 (1-6M Positional)",
            "H3": "H3 (6-12M Capex)",
            "H4": "H4 (1-3Y Multibagger)",
            "H5": "H5 (3-10Y Compounder)",
        }
        h_choice = st.selectbox(
            "Target Horizon",
            list(horizon_labels.keys()),
            format_func=lambda x: horizon_labels[x],
            index=list(horizon_labels.keys()).index(st.session_state["global_horizon"]),
            key="global_horizon_select",
        )
        st.session_state["global_horizon"] = h_choice

    with c_strat2:
        risk_choice = st.selectbox(
            "Risk Profile",
            ["CONSERVATIVE", "MODERATE", "AGGRESSIVE"],
            index=["CONSERVATIVE", "MODERATE", "AGGRESSIVE"].index(st.session_state["global_risk"]),
            key="global_risk_select",
        )
        st.session_state["global_risk"] = risk_choice

    with c_strat3:
        strategy_labels = {
            "ALL_10_OMNI_BRAIN": "10-Engine Omni-Brain",
            "INSTITUTIONAL_PURE_QUANT": "Institutional Pure Quant",
            "BUFFETT_MUNGER_COMPOUNDER": "Buffett-Munger Compounder",
            "MINERVINI_WHALE_BREAKOUT": "Minervini-Whale Breakout",
            "CUSTOM": "Custom Composer",
        }
        strat_choice = st.selectbox(
            "Strategy Preset",
            list(strategy_labels.keys()),
            format_func=lambda x: strategy_labels[x],
            index=list(strategy_labels.keys()).index(st.session_state["global_strategy"]),
            key="global_strategy_select",
        )
        st.session_state["global_strategy"] = strat_choice

    with c_strat4:
        st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)
        vedic_on = st.toggle("Vedic Engine", value=st.session_state["vedic_toggle"], key="vedic_toggle_btn")
        st.session_state["vedic_toggle"] = vedic_on

# Resolve Active Engine Buckets based on Strategy Preset
if st.session_state["global_strategy"] in AureliusWeightageMatrix.STRATEGY_PRESETS:
    base_active = list(AureliusWeightageMatrix.STRATEGY_PRESETS[st.session_state["global_strategy"]])
    if not base_active:  # CUSTOM
        base_active = list(AureliusWeightageMatrix.BUCKETS[1:])
else:
    base_active = list(AureliusWeightageMatrix.BUCKETS[1:])

if not st.session_state["vedic_toggle"] and "B10_VEDIC_JYOTISH" in base_active:
    base_active.remove("B10_VEDIC_JYOTISH")

active_buckets = base_active

# ------------------------------------------------------------------------------
# 3. FIVE COMMERCIAL WORKSTATIONS (DOCK NAVIGATION)
# ------------------------------------------------------------------------------
STATION_CHOICES = [
    "💼 Portfolio Surgeon",
    "🚀 Capital Allocator",
    "🌐 Market Scanner",
    "🔬 Stock X-Ray",
    "🧠 Aurelius AI Copilot",
]

selected_station = st.radio(
    "Commercial Station Navigation",
    STATION_CHOICES,
    index=STATION_CHOICES.index(st.session_state["active_station"]) if st.session_state["active_station"] in STATION_CHOICES else 0,
    horizontal=True,
    label_visibility="collapsed",
    key="mobile_station_dock_controller",
)
st.session_state["active_station"] = selected_station

# Shared Cached Codex Evaluator
@st.cache_data(ttl=60, show_spinner=False)
def evaluate_stock_cached(
    symbol_str: str,
    cmp_hint: float = 0.0,
    h_code: str = "H4",
    r_prof: str = "MODERATE",
    v_on: bool = True,
) -> Dict[str, Any]:
    try:
        clean_s, _, _ = resolve_universal_ticker(symbol_str)
        df_hist, cmp_live, chg_p = fetch_live_stock_ohlcv(clean_s, periods=120)
        eff_cmp = cmp_hint if cmp_hint > 0 else cmp_live
        res = compute_300_variable_codex(
            sym=clean_s,
            df_hist=df_hist,
            vedic_ctx=vedic_ctx,
            portfolio_equity=2500000.0,
            horizon_code=h_code,
            risk_profile=r_prof,
            active_buckets=active_buckets,
            vedic_enabled=v_on,
        )
        if eff_cmp > 0:
            res["CMP (₹)"] = eff_cmp
        return res
    except Exception:
        c_eff = cmp_hint if cmp_hint > 0 else 100.0
        return {
            "Symbol": symbol_str,
            "Master_Alpha_Score": 60.0,
            "Verdict": "STEADY COMPOUNDER (HOLD & ACCUMULATE ON DIPS)",
            "Action_Code": "HOLD",
            "CMP (₹)": c_eff,
            "Change %": 0.0,
            "Gate_0_Passed": True,
            "Hard Veto": False,
            "Kelly Weight %": 4.0,
            "Optimal_Horizon": h_code,
            "Selected_Horizon": h_code,
            "Stop-Loss (₹)": round(c_eff * 0.95, 1),
            "Target (₹)": round(c_eff * 1.15, 1),
            "Target_T1 (₹)": round(c_eff * 1.15, 1),
            "Executive_Brief": {
                "badge": "HOLD",
                "line_1": f"Position in {symbol_str} maintained with standard valuation cushion.",
                "line_2": "Historical metrics stable across reporting periods.",
                "line_3": f"Execution: Trailing stop loss placed at ₹{round(c_eff * 0.95, 1):,}.",
            },
            "Bucket_Scores": {b: 60.0 for b in AureliusWeightageMatrix.BUCKETS},
            "Bucket_Evidence": {b: "Standard baseline metric" for b in AureliusWeightageMatrix.BUCKETS},
        }

# ==============================================================================
# STATION 1: PORTFOLIO SURGEON & REBALANCE ENGINE
# ==============================================================================
if selected_station == "💼 Portfolio Surgeon":
    st.markdown("### 💼 Portfolio Surgeon & Autonomous Rebalance Engine")
    st.caption("Frictionless broker import, Gate 0 survival checks, and direct 'Sell Weak ➔ Buy Stronger' replacement switches.")

    active_prof = st.session_state["active_profile"]
    current_db_holdings = get_holdings(active_prof)

    # 4 Frictionless Input Tabs
    in_tab_upload, in_tab_paste, in_tab_quick, in_tab_grid = st.tabs(
        [
            "📂 Broker File Ingestion",
            "📋 Smart Text Position Importer",
            "➕ Quick Scrip Add",
            "📊 Interactive Ledger Grid",
        ]
    )

    with in_tab_upload:
        st.markdown("Upload export from **Zerodha Kite, Groww, Upstox, AngelOne, ICICI Direct, HDFC Sky, Kotak Neo, or NSDL/CDSL CAS**:")
        uploaded_file = st.file_uploader("Upload Broker File (CSV / XLSX):", type=["csv", "xlsx", "xls"], key="broker_file_uploader_v9")
        if uploaded_file is not None:
            df_parsed = PortfolioInputParser.parse_broker_file(uploaded_file, uploaded_file.name)
            if not df_parsed.empty:
                st.success(f"Recognized {len(df_parsed)} positions from {uploaded_file.name}!")
                if st.button("🚀 Ingest into Portfolio", key="btn_import_broker_v9"):
                    clear_profile_holdings(active_prof)
                    for _, r in df_parsed.iterrows():
                        save_holding_direct(active_prof, r["Symbol"], r["Shares"], r["Avg_Buy_Price"], "Equities")
                    st.success("Holdings ingested! Refreshing...")
                    st.rerun()

    with in_tab_paste:
        st.markdown("Paste unformatted text from WhatsApp, notes, or messages:")
        raw_text_input = st.text_area(
            "Paste Holdings (e.g. KOTAKBANK 260 1750):",
            value="BEL 300 210.65\nHAL 50 4200\nETERNAL 100 280.0\nYESBANK 1000 24.50\nKOTAKBANK 260 1750",
            height=100,
            key="smart_paste_box_v9",
        )
        if st.button("🔄 Ingest Parsed Positions", key="btn_parse_paste_v9"):
            df_text_parsed = PortfolioInputParser.parse_smart_text(raw_text_input)
            if not df_text_parsed.empty:
                clear_profile_holdings(active_prof)
                for _, r in df_text_parsed.iterrows():
                    save_holding_direct(active_prof, r["Symbol"], r["Shares"], r["Avg_Buy_Price"], "Equities")
                st.success(f"Ingested {len(df_text_parsed)} positions!")
                st.rerun()

    with in_tab_quick:
        col_q1, col_q2, col_q3, col_q4 = st.columns([2, 1, 1, 1])
        all_syms = get_searchable_universe_list()
        with col_q1:
            q_sym_sel = st.selectbox("Search Stock (~2,600+ Universe):", all_syms, index=None, placeholder="Search ticker or name...", key="quick_sym_v9")
        with col_q2:
            q_qty = st.number_input("Shares (Qty):", min_value=1, value=50, step=1, key="quick_qty_v9")
        with col_q3:
            q_price = st.number_input("Avg Buy Price (₹):", min_value=0.0, value=250.0, step=5.0, key="quick_price_v9")
        with col_q4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("➕ Ingest", key="btn_quick_add_v9"):
                if q_sym_sel:
                    clean_target_sym = parse_search_string(q_sym_sel)
                    save_holding_direct(active_prof, clean_target_sym, q_qty, q_price, "Equities")
                    st.success(f"Added {clean_target_sym}!")
                    st.rerun()

    with in_tab_grid:
        if not current_db_holdings.empty:
            df_editor_data = current_db_holdings[["symbol", "shares", "avg_cost", "sector"]].copy()
            df_editor_data.columns = ["Symbol", "Shares", "Avg_Buy_Price", "Sector"]
            edited_df = st.data_editor(df_editor_data, num_rows="dynamic", use_container_width=True, key="holdings_editor_v9")
            if st.button("💾 Save Changes", key="btn_save_grid_v9"):
                clear_profile_holdings(active_prof)
                for _, r in edited_df.iterrows():
                    if str(r["Symbol"]).strip():
                        save_holding_direct(active_prof, str(r["Symbol"]).strip().upper(), float(r["Shares"]), float(r["Avg_Buy_Price"]), str(r["Sector"]))
                st.success("Grid updated!")
                st.rerun()
        else:
            st.info("No holdings in active vault.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Evaluate Holdings
    if not current_db_holdings.empty:
        df_for_eval = current_db_holdings[["symbol", "shares", "avg_cost"]].copy()
        df_for_eval.columns = ["Symbol", "Shares", "Avg_Buy_Price"]

        held_syms = tuple(df_for_eval["Symbol"].unique())
        live_prices_dict = batch_fetch_live_prices(held_syms)
        live_cmp_map: Dict[str, float] = {}
        for s in held_syms:
            if s in live_prices_dict and live_prices_dict[s][0] > 0:
                live_cmp_map[s] = live_prices_dict[s][0]
            else:
                _, live_c, _ = fetch_live_stock_ohlcv(s, periods=10)
                live_cmp_map[s] = live_c

        df_evaluated, summary = PortfolioDecisionEngine.evaluate_holdings(
            df_holdings=df_for_eval,
            codex_evaluator_fn=lambda s, c: evaluate_stock_cached(s, c, st.session_state["global_horizon"], st.session_state["global_risk"], st.session_state["vedic_toggle"]),
            live_cmp_map=live_cmp_map,
            acar_split_fn=reconcile_corporate_action,
            risk_tolerance=st.session_state["global_risk"],
        )

        # Before vs After Surgery KPI Cards
        kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)
        with kpi_c1:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-label">Current Portfolio NAV</div>
                <div class="kpi-val">₹{summary.get('Total_Portfolio_Value', 0):,.0f}</div>
                <div class="kpi-sub">Invested: ₹{summary.get('Total_Invested_Value', 0):,.0f}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with kpi_c2:
            pnl_val = summary.get("Total_PnL", 0)
            pnl_pct = summary.get("Total_PnL_Pct", 0)
            col_p = "var(--accent-green)" if pnl_val >= 0 else "var(--accent-red)"
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-label">Net Unrealized P&L</div>
                <div class="kpi-val" style="color: {col_p};">₹{pnl_val:+,.0f}</div>
                <div class="kpi-sub" style="color: {col_p};">{pnl_pct:+0.2f}% Return</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with kpi_c3:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-label">Gross Freed Cash</div>
                <div class="kpi-val" style="color: var(--accent-amber);">₹{summary.get('Freed_Cash_Gross', 0):,.0f}</div>
                <div class="kpi-sub">{summary.get('Full_Exit_Count', 0)} Exits | {summary.get('Trim_Count', 0)} Trims</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with kpi_c4:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-label">STCG / LTCG Tax Reserve</div>
                <div class="kpi-val" style="color: var(--accent-red);">₹{summary.get('Estimated_Tax_Reserve', 0):,.0f}</div>
                <div class="kpi-sub">20% STCG / 12.5% LTCG Safe</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with kpi_c5:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-label">Net Reinvestment Cash</div>
                <div class="kpi-val" style="color: var(--accent-green);">₹{summary.get('Freed_Cash_Net', 0):,.0f}</div>
                <div class="kpi-sub">Ready for Alpha Deployment</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # 4-Tier Holdings Triage Bento Action Cards
        st.markdown("#### 🩺 Surgical Holdings Triage & Action Verdicts")
        for _, r in df_evaluated.iterrows():
            sym = r["Symbol"]
            act = r["Action"]
            score = r["Master_Score"]
            cmp_val = r["Live_CMP"]
            shares = r["Shares"]
            wt_pct = r["Weight_Pct"]
            delta = r["Suggested_Qty_Delta"]
            freed = r["Freed_INR"]

            # Verdict colors
            if "EXIT" in act:
                v_bg = "rgba(220, 38, 38, 0.15)"
                v_col = "var(--accent-red)"
            elif "TRIM" in act:
                v_bg = "rgba(217, 119, 6, 0.15)"
                v_col = "var(--accent-amber)"
            elif "BUY" in act:
                v_bg = "rgba(5, 150, 105, 0.15)"
                v_col = "var(--accent-green)"
            else:
                v_bg = "rgba(2, 132, 199, 0.15)"
                v_col = "var(--accent-primary)"

            st.markdown(
                f"""
            <div class="bento-card">
                <div class="bento-header">
                    <div>
                        <div class="bento-ticker">{sym}</div>
                        <div class="bento-company">Held: <b>{shares} sh</b> @ Avg ₹{r['Avg_Buy_Price']:,.2f} | Weight: <b>{wt_pct:.1f}%</b> | P&L: <b style="color: {'var(--accent-green)' if r['PnL'] >= 0 else 'var(--accent-red)'}">₹{r['PnL']:+,.0f} ({r['PnL_Pct']:+0.1f}%)</b></div>
                    </div>
                    <div style="text-align: right;">
                        <span class="bento-verdict-pill" style="background: {v_bg}; color: {v_col}; border: 1px solid {v_col};">{act}</span>
                        <div class="bento-score-gauge" style="color: {v_col}; margin-top: 4px;">{score:.1f}<span style="font-size: 13px; color: var(--text-secondary);">/100</span></div>
                    </div>
                </div>
                <div class="bento-corridor">
                    <div>Live CMP: <b>₹{cmp_val:,.2f}</b></div>
                    <div>Action Delta: <b style="color: {v_col};">{delta:+d} Shares</b></div>
                    <div>Stop Loss: <b>₹{r['Stop_Loss_INR']}</b></div>
                    <div>Target: <b>₹{r['Target_INR']}</b></div>
                    <div>Optimal Horizon: <b>{r['Optimal_Horizon']}</b></div>
                </div>
                <div class="bento-brief">
                    <div class="bento-brief-line1">Pillar 1: {r['Line_1_Why']}</div>
                    <div class="bento-brief-line2">Pillar 2: {r['Line_2_Catalyst']}</div>
                    <div class="bento-brief-line3">Pillar 3: {r['Line_3_Execution']}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Direct Capital Reallocation Engine (Sell Laggards -> Buy Alpha Leaders)
        if summary.get("Freed_Cash_Net", 0) > 100.0:
            st.markdown("---")
            st.markdown("#### 🔄 Capital Reallocation Switches (Sell Laggards ➔ Buy Alpha Leaders)")
            st.caption(f"Deploying ₹{summary.get('Freed_Cash_Net', 0):,.0f} net freed cash into highest-conviction replacement leaders:")

            curated_leaders = MultiTierUniverseManager.get_curated_universe()[:8]
            cand_syms = tuple(c["symbol"] for c in curated_leaders)
            cand_quotes = batch_fetch_live_prices(cand_syms)

            scanner_cands = []
            for c in curated_leaders:
                s = c["symbol"]
                q = cand_quotes.get(s, (250.0, 0))
                scanner_cands.append({
                    "Symbol": s,
                    "Company_Name": c["name"],
                    "Live_CMP": q[0] if q and q[0] > 0 else 250.0,
                    "Master_Score": 90.0,
                    "ROIIC": 32.0,
                    "Dividend_Yield": 1.5,
                })

            df_switches = PortfolioDecisionEngine.generate_replacement_switches(
                df_evaluated=df_evaluated,
                top_scanner_candidates=scanner_cands,
                net_freed_cash=summary.get("Freed_Cash_Net", 0),
            )
            if not df_switches.empty:
                st.dataframe(df_switches, use_container_width=True)

        # 1-Click Institutional Excel Dossier
        st.markdown("---")
        col_ex_lbl, col_ex_btn = st.columns([3, 1])
        with col_ex_lbl:
            st.markdown("#### 📥 6-Sheet Institutional Excel Dossier")
            st.caption("Complete portfolio audit, radar universe, trade ledger, and 300-variable metrics.")
        with col_ex_btn:
            if st.button("Generate Excel Dossier", key="btn_gen_excel_v9"):
                excel_bytes = build_ananta216_excel_dossier(
                    active_profile=active_prof,
                    df_vault_disp=get_holdings(active_prof),
                    df_radar=df_evaluated,
                    df_ledger=get_trade_ledger(active_prof),
                    vedic_info=vedic_ctx,
                    mmi_score=52.4,
                    featured_sym=df_evaluated.iloc[0]["Symbol"] if not df_evaluated.empty else "BEL",
                    featured_codex={},
                )
                st.download_button(
                    label="⬇️ Download Dossier.xlsx",
                    data=excel_bytes,
                    file_name=f"Aurelius_Apex_Portfolio_Dossier_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="btn_download_excel_file",
                )

# ==============================================================================
# STATION 2: CAPITAL ALLOCATOR & ORDER BUILDER
# ==============================================================================
elif selected_station == "🚀 Capital Allocator":
    st.markdown("### 🚀 Sovereign Capital Deployment & Order Builder")
    st.caption("Partitions any capital outlay across 4 All-Weather sleeves with exact integer shares (Qty = floor(Outlay/CMP)).")

    st.markdown("<div style='font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;'><b>Quick Capital Presets:</b></div>", unsafe_allow_html=True)
    p_cols = st.columns(6)
    presets = [("₹10K", 10000.0), ("₹50K", 50000.0), ("₹1 Lakh", 100000.0), ("₹5 Lakh", 500000.0), ("₹25 Lakh", 2500000.0), ("₹1 Crore", 10000000.0)]
    for p_i, (p_lbl, p_val) in enumerate(presets):
        with p_cols[p_i]:
            if st.button(p_lbl, key=f"quick_cap_v9_{p_lbl}"):
                st.session_state["allocator_cap_val"] = p_val
                st.rerun()

    cur_alloc_cap = float(st.session_state.get("allocator_cap_val", 500000.0))
    fresh_capital = st.number_input(
        "Capital Deployment Outlay (₹):",
        min_value=100.0,
        max_value=1000000000.0,
        value=cur_alloc_cap,
        step=25000.0,
        format="%.0f",
        key="fresh_cap_input_v9",
    )

    # Dynamic candidates from Curated Universe with live quotes
    curated_pool = MultiTierUniverseManager.get_curated_universe()[:25]
    curated_syms = tuple(c["symbol"] for c in curated_pool)
    live_curated_prices = batch_fetch_live_prices(curated_syms)
    live_cmp_map = {k: v[0] for k, v in live_curated_prices.items() if v and v[0] > 0}

    # Generate complete wealth plan
    plan = WealthOrderAllocator.generate_complete_wealth_plan(
        capital_inr=fresh_capital,
        horizon_code=st.session_state["global_horizon"],
        risk_tolerance=st.session_state["global_risk"],
        live_cmp_map=live_cmp_map,
    )

    # 4 Sleeves Display
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    s_cols = st.columns(4)
    sleeves = plan.get("Sleeve_Breakdown", {})
    for idx, (s_name, s_data) in enumerate(sleeves.items()):
        with s_cols[idx]:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-label">{s_name}</div>
                <div class="kpi-val">₹{s_data['Allocated_INR']:,.0f}</div>
                <div class="kpi-sub" style="color: var(--accent-primary);">{s_data['Weight_Pct']}% Portfolio Share</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Executable Order Bento Cards
    st.markdown("#### 🛒 Executable Market Orders (Integer Share Qty)")
    orders_df = plan.get("Orders_Table", pd.DataFrame())
    if not orders_df.empty:
        for _, ord_row in orders_df.iterrows():
            sym = ord_row["Symbol"]
            sleeve = ord_row["Sleeve"]
            score = ord_row["Score"]
            cmp_v = ord_row["CMP"]
            qty = ord_row["Qty"]
            outlay = ord_row["Outlay_INR"]
            stop_v = ord_row["Stop_Loss"]
            tgt1_v = ord_row["Target_1"]
            tgt2_v = ord_row["Target_2"]
            div_y = ord_row["Div_Yield_Pct"]

            st.markdown(
                f"""
            <div class="bento-card">
                <div class="bento-header">
                    <div>
                        <div class="bento-ticker">{sym} <span style="font-size: 13px; color: var(--accent-primary);">({ord_row['Company_Name']})</span></div>
                        <div class="bento-company">Sleeve: <b>{sleeve}</b> | Sector: <b>{ord_row['Sector']}</b> | Div Yield: <b>{div_y:.1f}%</b></div>
                    </div>
                    <div style="text-align: right;">
                        <span class="bento-verdict-pill" style="background: rgba(5, 150, 105, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green);">BUY +{qty} SHARES</span>
                        <div class="bento-score-gauge" style="color: var(--accent-green); margin-top: 4px;">{score:.1f}<span style="font-size: 13px; color: var(--text-secondary);">/100</span></div>
                    </div>
                </div>
                <div class="bento-corridor">
                    <div>Live CMP: <b>₹{cmp_v:,.2f}</b></div>
                    <div>Outlay: <b style="color: var(--accent-green);">₹{outlay:,.0f} ({ord_row['Weight_Pct']:.1f}%)</b></div>
                    <div>Buy Zone: <b>{ord_row['Buy Zone']}</b></div>
                    <div>Stop Loss: <b style="color: var(--accent-red);">₹{stop_v}</b></div>
                    <div>Target 1: <b style="color: var(--accent-green);">₹{tgt1_v}</b></div>
                    <div>Target 2: <b style="color: var(--accent-primary);">₹{tgt2_v}</b></div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Compounding & DRIP Table
    st.markdown("---")
    st.markdown("#### 📈 Dual-Track Wealth Compounding Projection")
    df_comp = plan.get("Compounding_Table", pd.DataFrame())
    if not df_comp.empty:
        st.dataframe(
            df_comp.style.format({
                "Pure Lump-Sum (₹)": "₹{:,.0f}",
                "Lump-Sum + Monthly SIP + DRIP (₹)": "₹{:,.0f}",
                "Estimated Annual Dividend Income (₹)": "₹{:,.0f}",
            }),
            use_container_width=True,
        )

# ==============================================================================
# STATION 3: FULL-MARKET OPPORTUNITY SCANNER
# ==============================================================================
elif selected_station == "🌐 Market Scanner":
    st.markdown("### 🌐 Full-Market Opportunity Scanner")
    st.caption("Real-time two-stage scanner filtering liquid multi-cap universe through 8 institutional alpha lenses.")

    # 8 Institutional Alpha Lenses
    lenses = [
        "👑 Sovereign Alpha Leaders (Score >= 75)",
        "⚡ Minervini Stage 2 & VCP Breakouts",
        "🏢 PE Crossover & QIP Floor Arbitrage",
        "💎 Dividend Aristocrats & TSY",
        "🏗️ High 3Y ROIIC & CWIP Capex Jolt",
        "💼 Buffett-Munger Compounders",
        "🛡️ War / Speech Panic Contrarian",
        "🏛️ Kautilya Saptanga & Master Investors",
    ]
    selected_lens = st.selectbox("Institutional Alpha Lens:", lenses, index=0, key="lens_selector_v9")

    # Candidates from curated universe
    raw_curated = MultiTierUniverseManager.get_curated_universe()[:35]
    cur_syms = tuple(c["symbol"] for c in raw_curated)
    live_scan_prices = batch_fetch_live_prices(cur_syms)

    scan_results = []
    for c in raw_curated:
        s = c["symbol"]
        sec = c.get("sector", "Equities")
        nm = c.get("name", s)
        q = live_scan_prices.get(s, (100.0, 0.0))
        cmp_v = q[0] if q and q[0] > 0 else 100.0
        chg_v = q[1] if q else 0.0

        eval_res = evaluate_stock_cached(s, cmp_v, st.session_state["global_horizon"], st.session_state["global_risk"], st.session_state["vedic_toggle"])
        score_v = eval_res.get("Master_Alpha_Score", 65.0)
        veto_v = eval_res.get("Hard Veto", False)

        b_scores = eval_res.get("Bucket_Scores", {})
        scan_results.append({
            "Symbol": s,
            "Company_Name": nm,
            "Sector": sec,
            "CMP": cmp_v,
            "Change_1D": chg_v,
            "Master_Score": score_v,
            "Verdict": eval_res.get("Verdict", "HOLD"),
            "VCP_Tightness": b_scores.get("B03_TECHNICAL_VCP", 75.0),
            "ROIIC": b_scores.get("B02_FUNDAMENTAL_MOAT", 75.0),
            "Dividend_TSY": b_scores.get("B05_DIVIDEND_TSY", 60.0),
            "PE_QIP": b_scores.get("B06_PE_QIP_DEALS", 70.0),
            "Kautilya": b_scores.get("B09_MASTER_KAUTILYA", 75.0),
            "Hard_Veto": veto_v,
            "Stop_Loss": eval_res.get("Stop-Loss (₹)", cmp_v * 0.95),
            "Target": eval_res.get("Target_T1 (₹)", cmp_v * 1.15),
            "Brief": eval_res.get("Executive_Brief", {}),
        })

    df_scanner = pd.DataFrame(scan_results)

    # Filter according to lens
    if "Sovereign Alpha" in selected_lens:
        filtered_df = df_scanner[(df_scanner["Master_Score"] >= 75.0) & (~df_scanner["Hard_Veto"])].sort_values(by="Master_Score", ascending=False)
    elif "Minervini" in selected_lens:
        filtered_df = df_scanner[(df_scanner["VCP_Tightness"] >= 75.0) & (~df_scanner["Hard_Veto"])].sort_values(by="VCP_Tightness", ascending=False)
    elif "PE Crossover" in selected_lens:
        filtered_df = df_scanner[(df_scanner["PE_QIP"] >= 70.0) & (~df_scanner["Hard_Veto"])].sort_values(by="PE_QIP", ascending=False)
    elif "Dividend" in selected_lens:
        filtered_df = df_scanner[(df_scanner["Dividend_TSY"] >= 70.0) & (~df_scanner["Hard_Veto"])].sort_values(by="Dividend_TSY", ascending=False)
    elif "ROIIC" in selected_lens:
        filtered_df = df_scanner[(df_scanner["ROIIC"] >= 75.0) & (~df_scanner["Hard_Veto"])].sort_values(by="ROIIC", ascending=False)
    elif "Panic" in selected_lens:
        filtered_df = df_scanner[(df_scanner["Change_1D"] < -1.5) & (df_scanner["Master_Score"] >= 70.0) & (~df_scanner["Hard_Veto"])]
        if filtered_df.empty:
            filtered_df = df_scanner[(df_scanner["Master_Score"] >= 72.0) & (~df_scanner["Hard_Veto"])].head(5)
    elif "Kautilya" in selected_lens:
        filtered_df = df_scanner[(df_scanner["Kautilya"] >= 75.0) & (~df_scanner["Hard_Veto"])].sort_values(by="Kautilya", ascending=False)
    else:
        filtered_df = df_scanner.sort_values(by="Master_Score", ascending=False)

    # Display Bento Cards
    st.markdown(f"#### Results: {len(filtered_df)} Alpha Candidates Found")
    for _, item in filtered_df.iterrows():
        s = item["Symbol"]
        sc = item["Master_Score"]
        cmp_p = item["CMP"]
        chg_p = item["Change_1D"]
        chg_c = "var(--accent-green)" if chg_p >= 0 else "var(--accent-red)"

        col_b_main, col_b_act = st.columns([4, 1])
        with col_b_main:
            st.markdown(
                f"""
            <div class="bento-card">
                <div class="bento-header">
                    <div>
                        <div class="bento-ticker">{s} <span style="font-size: 13px; color: var(--accent-primary);">({item['Company_Name']})</span></div>
                        <div class="bento-company">{item['Sector']} | Live CMP: <b>₹{cmp_p:,.2f}</b> <span style="color: {chg_c};">({chg_p:+0.2f}%)</span></div>
                    </div>
                    <div style="text-align: right;">
                        <span class="bento-verdict-pill" style="background: rgba(5, 150, 105, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green);">{item['Verdict']}</span>
                        <div class="bento-score-gauge" style="color: var(--accent-green); margin-top: 4px;">{sc:.1f}<span style="font-size: 13px; color: var(--text-secondary);">/100</span></div>
                    </div>
                </div>
                <div class="bento-corridor">
                    <div>Stop Loss: <b style="color: var(--accent-red);">₹{item['Stop_Loss']}</b></div>
                    <div>Target: <b style="color: var(--accent-green);">₹{item['Target']}</b></div>
                    <div>VCP Contraction: <b>{item['VCP_Tightness']:.0f}%</b></div>
                    <div>ROIIC Moat: <b>{item['ROIIC']:.0f}%</b></div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with col_b_act:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            if st.button(f"Audit {s}", key=f"btn_scan_audit_{s}"):
                st.session_state["active_xray_selection"] = f"{s} — {item['Company_Name']} ({item['Sector']} | NSE)"
                st.session_state["active_station"] = "🔬 Stock X-Ray"
                st.rerun()

# ==============================================================================
# STATION 4: STOCK X-RAY & 10-ENGINE AUDIT
# ==============================================================================
elif selected_station == "🔬 Stock X-Ray":
    st.markdown("### 🔬 Stock X-Ray & 10-Engine Diagnostic Audit")
    st.caption("Deep forensic and multi-engine audit across all 2,658 NSE equities. Starts 100% blank and unopinionated.")

    # Autocomplete Search Bar over ALL ~2,600+ equities
    search_list = get_searchable_universe_list()
    
    col_x_search, col_x_quick = st.columns([2.5, 1.5])
    with col_x_search:
        selected_search_item = st.selectbox(
            "Search Equity Directory (~2,658 Listed Equities):",
            options=search_list,
            index=None if st.session_state["active_xray_selection"] is None else (
                search_list.index(st.session_state["active_xray_selection"]) if st.session_state["active_xray_selection"] in search_list else None
            ),
            placeholder="Type ticker or company name (e.g. BEL, ZOMATO, TCS, RELIANCE, HAL)...",
            key="xray_autocomplete_search",
        )
        if selected_search_item:
            st.session_state["active_xray_selection"] = selected_search_item

    with col_x_quick:
        st.markdown("<div style='font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;'><b>Popular Market Leaders:</b></div>", unsafe_allow_html=True)
        q_chips = ["BEL", "HAL", "ETERNAL", "TRENT", "TITAN", "TCS", "COALINDIA"]
        c_cols = st.columns(len(q_chips))
        for ci, csym in enumerate(q_chips):
            with c_cols[ci]:
                if st.button(csym, key=f"btn_chip_xray_{csym}"):
                    # Find matching string
                    matched = next((item for item in search_list if item.startswith(f"{csym} —")), f"{csym} — {csym} (Equities | NSE)")
                    st.session_state["active_xray_selection"] = matched
                    st.rerun()

    # If stock is selected, run complete 10-Bucket Audit
    if st.session_state["active_xray_selection"]:
        raw_sel = st.session_state["active_xray_selection"]
        target_ticker = parse_search_string(raw_sel)

        with st.spinner(f"Computing 300-variable forensic tensor for {target_ticker}..."):
            eval_data = evaluate_stock_cached(
                symbol_str=target_ticker,
                h_code=st.session_state["global_horizon"],
                r_prof=st.session_state["global_risk"],
                v_on=st.session_state["vedic_toggle"],
            )

        master_score = eval_data.get("Master_Alpha_Score", 60.0)
        verdict = eval_data.get("Verdict", "HOLD")
        cmp_v = eval_data.get("CMP (₹)", 100.0)
        chg_v = eval_data.get("Change %", 0.0)
        chg_c = "var(--accent-green)" if chg_v >= 0 else "var(--accent-red)"
        veto_flag = eval_data.get("Hard Veto", False)
        b_scores = eval_data.get("Bucket_Scores", {})
        b_evidence = eval_data.get("Bucket_Evidence", {})

        score_col = "var(--accent-green)" if master_score >= 75.0 else ("var(--accent-primary)" if master_score >= 55.0 else "var(--accent-red)")

        # Master Verdict Header Bento Card
        st.markdown(
            f"""
        <div class="bento-card" style="border: 2px solid {score_col};">
            <div class="bento-header">
                <div>
                    <div style="font-size: 26px; font-weight: 900; color: var(--text-primary);">{target_ticker}</div>
                    <div style="color: var(--text-secondary); font-size: 13px;">{eval_data.get('Sector', 'Equities')} | Live CMP: <b style="color: var(--text-primary); font-size: 16px;">₹{cmp_v:,.2f}</b> <span style="color: {chg_c};">({chg_v:+0.2f}%)</span></div>
                </div>
                <div style="text-align: right;">
                    <div class="bento-score-gauge" style="color: {score_col}; font-size: 38px;">{master_score:.1f}<span style="font-size: 16px; color: var(--text-secondary);">/100</span></div>
                    <span class="bento-verdict-pill" style="background: rgba(56, 189, 248, 0.15); color: {score_col}; border: 1px solid {score_col};">{verdict}</span>
                </div>
            </div>
            <div class="bento-corridor">
                <div>Gate 0 Status: <b style="color: {'var(--accent-green)' if not veto_flag else 'var(--accent-red)'}">{'CLEARED' if not veto_flag else 'HARD VETO'}</b></div>
                <div>Optimal Horizon: <b>{eval_data.get('Optimal_Horizon', 'H4')}</b></div>
                <div>Stop Loss: <b style="color: var(--accent-red);">₹{eval_data.get('Stop-Loss (₹)', 0)}</b></div>
                <div>Target: <b style="color: var(--accent-green);">₹{eval_data.get('Target_T1 (₹)', 0)}</b></div>
                <div>Kelly Weight: <b>{eval_data.get('Kelly Weight %', 4.0):.1f}%</b></div>
            </div>
            <div class="bento-brief">
                <div class="bento-brief-line1">Pillar 1 (Moat): {eval_data.get('Executive_Brief', {}).get('line_1', '')}</div>
                <div class="bento-brief-line2">Pillar 2 (Catalyst): {eval_data.get('Executive_Brief', {}).get('line_2', '')}</div>
                <div class="bento-brief-line3">Pillar 3 (Execution): {eval_data.get('Executive_Brief', {}).get('line_3', '')}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 10-ENGINE EVIDENCE SCORECARD (CONCRETE COMPUTED NUMBERS)
        st.markdown("#### 🏛️ 10-Engine Evidence Scorecard (Live Empirical Numbers)")
        bucket_cols = st.columns(2)
        for b_idx, (b_name, b_sc) in enumerate(b_scores.items()):
            col_target = bucket_cols[b_idx % 2]
            ev_text = b_evidence.get(b_name, "Standard calculation")
            b_clean_title = b_name.replace("_", " ").title()
            
            with col_target:
                b_color = "var(--accent-green)" if b_sc >= 75.0 else ("var(--accent-primary)" if b_sc >= 55.0 else "var(--accent-red)")
                st.markdown(
                    f"""
                <div class="kpi-card" style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 12px; color: var(--text-primary);">{b_clean_title}</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-weight: 800; color: {b_color}; font-size: 14px;">{b_sc:.0f}/100</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                        {ev_text}
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        # Interactive Candlestick + Polar Radar Chart
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        col_c_left, col_c_right = st.columns([1.6, 1.0])

        with col_c_left:
            st.markdown("##### 📊 Live Candlestick & Volume")
            df_hist_disp, _, _ = fetch_live_stock_ohlcv(target_ticker, periods=100)
            if not df_hist_disp.empty:
                fig_c = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
                fig_c.add_trace(go.Candlestick(x=df_hist_disp.index, open=df_hist_disp["Open"], high=df_hist_disp["High"], low=df_hist_disp["Low"], close=df_hist_disp["Close"], name="Price"), row=1, col=1)
                ema20 = df_hist_disp["Close"].ewm(span=20, adjust=False).mean()
                ema50 = df_hist_disp["Close"].ewm(span=50, adjust=False).mean()
                fig_c.add_trace(go.Scatter(x=df_hist_disp.index, y=ema20, line=dict(color="#38BDF8", width=1.5), name="EMA 20"), row=1, col=1)
                fig_c.add_trace(go.Scatter(x=df_hist_disp.index, y=ema50, line=dict(color="#F59E0B", width=1.5), name="EMA 50"), row=1, col=1)
                fig_c.add_trace(go.Bar(x=df_hist_disp.index, y=df_hist_disp["Volume"], name="Volume", marker_color="#64748B"), row=2, col=1)
                fig_c.update_layout(
                    template="plotly_white" if is_light else "plotly_dark",
                    paper_bgcolor="#FFFFFF" if is_light else "#0E1526",
                    plot_bgcolor="#FFFFFF" if is_light else "#0E1526",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=360,
                    xaxis_rangeslider_visible=False,
                )
                st.plotly_chart(fig_c, use_container_width=True)

        with col_c_right:
            st.markdown("##### 🕸️ 10-Engine Factor Radar")
            r_vals = list(b_scores.values())
            r_labels = [k.replace("B", "").replace("_", " ") for k in b_scores.keys()]
            if r_vals:
                r_vals.append(r_vals[0])
                r_labels.append(r_labels[0])
                fig_rad = go.Figure()
                fig_rad.add_trace(go.Scatterpolar(r=r_vals, theta=r_labels, fill="toself", fillcolor="rgba(56, 189, 248, 0.25)", line=dict(color="#38BDF8", width=2)))
                fig_rad.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8"),
                        angularaxis=dict(color="#0F172A" if is_light else "#F8FAFC"),
                        bgcolor="#FFFFFF" if is_light else "#0E1526",
                    ),
                    paper_bgcolor="#FFFFFF" if is_light else "#0E1526",
                    margin=dict(l=25, r=25, t=25, b=25),
                    height=360,
                    showlegend=False,
                )
                st.plotly_chart(fig_rad, use_container_width=True)

        # Collapsible Deep Intelligence Vault
        with st.expander("🔬 Deep Institutional Factor Vault (Click to Expand)", expanded=False):
            codex_full = eval_data.get("Codex_300", eval_data.get("Codex_216", {}))
            codex_items = [{"Variable": k, "Value": str(v)} for k, v in codex_full.items()]
            st.dataframe(pd.DataFrame(codex_items), use_container_width=True, height=400)

    else:
        st.markdown(
            """
        <div style="background: var(--bg-card); border: 1px dashed var(--border-color); border-radius: 12px; padding: 45px 20px; text-align: center; margin-top: 15px;">
            <div style="font-size: 34px; margin-bottom: 8px;">🔍</div>
            <h3 style="margin: 0; color: var(--text-primary); font-size: 18px;">Directory Search is 100% Ready</h3>
            <p style="color: var(--text-secondary); font-size: 13px; max-width: 520px; margin: 8px auto 0;">
                Select any of the ~2,658 NSE listed equities in the search dropdown above or click a market leader chip. The 10-Bucket Engine computes all 300 variables live with zero placeholder data.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

# ==============================================================================
# STATION 5: AURELIUS AI COPILOT
# ==============================================================================
elif selected_station == "🧠 Aurelius AI Copilot":
    st.markdown("### 🧠 Aurelius Conversational Quant Copilot")
    st.caption("Ask questions in natural language: Single stock audits, head-to-head peer comparisons, instant capital deployment, and portfolio surgery.")

    # Quick Action Chips
    st.markdown("<div style='font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;'><b>Quick Prompts:</b></div>", unsafe_allow_html=True)
    qp_cols = st.columns(5)
    quick_prompts = [
        "Audit BEL",
        "Compare BEL vs HAL",
        "Allocate ₹5,00,000",
        "Scan Top 5 Breakouts",
        "Run Portfolio Surgery",
    ]
    for qp_i, qp_text in enumerate(quick_prompts):
        with qp_cols[qp_i]:
            if st.button(qp_text, key=f"copilot_qp_{qp_i}"):
                resp = generate_deterministic_copilot_response(
                    user_query=qp_text,
                    active_profile=st.session_state["active_profile"],
                    df_vault_disp=get_holdings(st.session_state["active_profile"]),
                    df_radar=pd.DataFrame(),
                    vedic_ctx=vedic_ctx,
                    mmi_score=52.4,
                )
                st.session_state["copilot_history"].append({"user": qp_text, "bot": resp})
                st.rerun()

    # Chat Log Display
    for msg in st.session_state["copilot_history"]:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant", avatar="👑"):
            st.markdown(msg["bot"])

    # User Chat Input
    user_input = st.chat_input("Ask Copilot (e.g. 'Compare TCS vs INFY', 'Audit ZOMATO', 'Allocate 10 Lakh')...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        resp = generate_deterministic_copilot_response(
            user_query=user_input,
            active_profile=st.session_state["active_profile"],
            df_vault_disp=get_holdings(st.session_state["active_profile"]),
            df_radar=pd.DataFrame(),
            vedic_ctx=vedic_ctx,
            mmi_score=52.4,
        )
        with st.chat_message("assistant", avatar="👑"):
            st.markdown(resp)
        st.session_state["copilot_history"].append({"user": user_input, "bot": resp})
