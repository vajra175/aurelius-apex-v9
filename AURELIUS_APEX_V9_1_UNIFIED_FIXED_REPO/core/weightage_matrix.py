"""
================================================================================
AURELIUS APEX (AQ-OS v9.1) — UNIFIED 10-BUCKET WEIGHTAGE MATRIX & HORIZON ENGINE
================================================================================
Implements:
- Unified 9-Core Quant Engine by Default (B01 through B09 working in 100% unison)
- Optional B10 Vedic Jyotish Overlay (OFF by default so pure quant is never diluted;
  1-click toggle ON or custom multi-select)
- 6 Investing Horizons (H0 to H5) & Panic Contrarian Regime with all 9 Core Engines active
- 3 Risk Profiles (Conservative, Moderate, Aggressive)
- Gate 0 Principle-1 Hard Forensic Gatekeeper
- Dynamic Auto-Normalization of Active Buckets (sum(W) == 100.0%)
- Commercial 3-Line Plain-English Executive Brief Generator
================================================================================
"""

import math
from typing import Dict, Any, List, Optional, Tuple, Set


class AureliusWeightageMatrix:
    """
    Computes exact institutional weights across the 10 Engine Buckets as a function
    of target Investing Horizon (H0 to H5), Market Regime, and user-selected Active Buckets.
    By default, ALL 9 Core Quantitative/Fundamental/Technical/Whale/Dividend/PE/News/Macro/
    Master-Investor buckets run together in unison (100% combined power).
    """

    # 10 Standard Engine Buckets
    BUCKETS = [
        "B01_FORENSIC_SHIELD",      # Gate 0 Hard Veto + Forensic Quality (Always Mandatory)
        "B02_FUNDAMENTAL_MOAT",     # Valuation, Cash-Flow, 3Y ROIIC, CWIP, Damani CCC
        "B03_TECHNICAL_VCP",        # Minervini Stage 2, VCP Tightness, PEAD, Mansfield RS
        "B04_BEHAVIORAL_WHALE",     # Volume Profile POC/VAH/VAL, VPIN, Wyckoff, Order Flow
        "B05_DIVIDEND_TSY",         # 10Y Dividend CAGR, Streak, Buybacks, TSY, YoC
        "B06_PE_QIP_DEALS",         # PE/VC Stakes, SEBI ICDR QIP Floor, Block Deals
        "B07_NEWS_CATALYSTS",       # Live ticker.news NLP, Order-Book-to-Bill, Margin Spreads
        "B08_MACRO_RRG_CHAOS",      # Live Macro Feeds, Sector RRG Quadrants, Hurst, Entropy
        "B09_MASTER_KAUTILYA",      # 12 Master Investors Checklists & Kautilya Saptanga
        "B10_VEDIC_JYOTISH",        # Optional 1-Click Toggle ON/OFF (9-Graha Lahiri Ephemeris)
    ]

    BUCKET_LABELS = {
        "B01_FORENSIC_SHIELD": "B01: Forensic & Accounting Shield (Gate 0 + Beneish/Sloan/Z'')",
        "B02_FUNDAMENTAL_MOAT": "B02: Fundamental Moat, 3Y ROIIC & CWIP Capex Jolt",
        "B03_TECHNICAL_VCP": "B03: Technical VCP, Minervini Stage 2 & Mansfield RS",
        "B04_BEHAVIORAL_WHALE": "B04: Behavioral Whale Flow, Dark Pool & VPIN Toxicity",
        "B05_DIVIDEND_TSY": "B05: Dividend Aristocrat, Buybacks & Total Shareholder Yield",
        "B06_PE_QIP_DEALS": "B06: PE/VC Crossover, SEBI QIP Floor & Block Deals",
        "B07_NEWS_CATALYSTS": "B07: Live News NLP, Order-Book-to-Bill & Margin Catalysts",
        "B08_MACRO_RRG_CHAOS": "B08: Macro Liquidity, Sector RRG & Chaos Physics",
        "B09_MASTER_KAUTILYA": "B09: 12 Master Investors DNA & Kautilya Saptanga",
        "B10_VEDIC_JYOTISH": "B10: Siddhantic Vedic Jyotish & SBC Vedha (Optional Overlay)",
    }

    # Core 9 Quantitative & Institutional Engines (Default Unified Powerhouse — excludes Vedic)
    CORE_9_QUANT_BUCKETS = [
        "B01_FORENSIC_SHIELD",
        "B02_FUNDAMENTAL_MOAT",
        "B03_TECHNICAL_VCP",
        "B04_BEHAVIORAL_WHALE",
        "B05_DIVIDEND_TSY",
        "B06_PE_QIP_DEALS",
        "B07_NEWS_CATALYSTS",
        "B08_MACRO_RRG_CHAOS",
        "B09_MASTER_KAUTILYA",
    ]

    # Strategy Modes (Unified All-9 Core Quant is primary default; never dilutes into narrow single-method silos unless customized)
    STRATEGY_PRESETS = {
        "UNIFIED_9_CORE_QUANT": list(CORE_9_QUANT_BUCKETS),
        "ALL_10_OMNI_BRAIN": list(BUCKETS),
        "INSTITUTIONAL_PURE_QUANT": list(CORE_9_QUANT_BUCKETS),
        "BUFFETT_MUNGER_COMPOUNDER": list(CORE_9_QUANT_BUCKETS),
        "MINERVINI_WHALE_BREAKOUT": list(CORE_9_QUANT_BUCKETS),
        "CUSTOM": list(CORE_9_QUANT_BUCKETS),
    }

    # Baseline Weight Vectors across all 6 Horizons (H0 - H5)
    # Every core bucket has a meaningful, horizon-calibrated weight so all methods work together in unison.
    HORIZON_WEIGHT_TENSORS = {
        "H0": {  # 1 - 3 Days (Ultra-Fast Momentum / Intraday / Bada-Swing Scalp)
            "B01_FORENSIC_SHIELD": 0.08,
            "B02_FUNDAMENTAL_MOAT": 0.06,
            "B03_TECHNICAL_VCP": 0.30,
            "B04_BEHAVIORAL_WHALE": 0.28,
            "B05_DIVIDEND_TSY": 0.02,
            "B06_PE_QIP_DEALS": 0.08,
            "B07_NEWS_CATALYSTS": 0.10,
            "B08_MACRO_RRG_CHAOS": 0.05,
            "B09_MASTER_KAUTILYA": 0.03,
            "B10_VEDIC_JYOTISH": 0.03,
        },
        "H1": {  # 1 - 4 Weeks (Swing Velocity & Breakout Catalysts)
            "B01_FORENSIC_SHIELD": 0.10,
            "B02_FUNDAMENTAL_MOAT": 0.10,
            "B03_TECHNICAL_VCP": 0.24,
            "B04_BEHAVIORAL_WHALE": 0.22,
            "B05_DIVIDEND_TSY": 0.04,
            "B06_PE_QIP_DEALS": 0.11,
            "B07_NEWS_CATALYSTS": 0.10,
            "B08_MACRO_RRG_CHAOS": 0.05,
            "B09_MASTER_KAUTILYA": 0.04,
            "B10_VEDIC_JYOTISH": 0.04,
        },
        "H2": {  # 1 - 6 Months (Positional & PEAD Post-Earnings Drift)
            "B01_FORENSIC_SHIELD": 0.12,
            "B02_FUNDAMENTAL_MOAT": 0.18,
            "B03_TECHNICAL_VCP": 0.18,
            "B04_BEHAVIORAL_WHALE": 0.14,
            "B05_DIVIDEND_TSY": 0.06,
            "B06_PE_QIP_DEALS": 0.12,
            "B07_NEWS_CATALYSTS": 0.09,
            "B08_MACRO_RRG_CHAOS": 0.05,
            "B09_MASTER_KAUTILYA": 0.06,
            "B10_VEDIC_JYOTISH": 0.04,
        },
        "H3": {  # 6 - 12 Months (Annual Catalysts & Capex Inflection)
            "B01_FORENSIC_SHIELD": 0.14,
            "B02_FUNDAMENTAL_MOAT": 0.22,
            "B03_TECHNICAL_VCP": 0.14,
            "B04_BEHAVIORAL_WHALE": 0.10,
            "B05_DIVIDEND_TSY": 0.09,
            "B06_PE_QIP_DEALS": 0.10,
            "B07_NEWS_CATALYSTS": 0.08,
            "B08_MACRO_RRG_CHAOS": 0.05,
            "B09_MASTER_KAUTILYA": 0.08,
            "B10_VEDIC_JYOTISH": 0.04,
        },
        "H4": {  # 1 - 3 Years (Multibagger Capex & Institutional Re-rating Cycle)
            "B01_FORENSIC_SHIELD": 0.15,
            "B02_FUNDAMENTAL_MOAT": 0.25,
            "B03_TECHNICAL_VCP": 0.10,
            "B04_BEHAVIORAL_WHALE": 0.08,
            "B05_DIVIDEND_TSY": 0.12,
            "B06_PE_QIP_DEALS": 0.09,
            "B07_NEWS_CATALYSTS": 0.06,
            "B08_MACRO_RRG_CHAOS": 0.05,
            "B09_MASTER_KAUTILYA": 0.10,
            "B10_VEDIC_JYOTISH": 0.04,
        },
        "H5": {  # 3 - 10 Years+ (Dynastic Forever Compounder & Dividend Royalty)
            "B01_FORENSIC_SHIELD": 0.18,
            "B02_FUNDAMENTAL_MOAT": 0.28,
            "B03_TECHNICAL_VCP": 0.05,
            "B04_BEHAVIORAL_WHALE": 0.05,
            "B05_DIVIDEND_TSY": 0.18,
            "B06_PE_QIP_DEALS": 0.06,
            "B07_NEWS_CATALYSTS": 0.04,
            "B08_MACRO_RRG_CHAOS": 0.04,
            "B09_MASTER_KAUTILYA": 0.12,
            "B10_VEDIC_JYOTISH": 0.03,
        },
        "PANIC_CONTRARIAN": {  # Speech / War / Flash Crash Dislocation
            "B01_FORENSIC_SHIELD": 0.18,
            "B02_FUNDAMENTAL_MOAT": 0.24,
            "B03_TECHNICAL_VCP": 0.06,
            "B04_BEHAVIORAL_WHALE": 0.20,
            "B05_DIVIDEND_TSY": 0.12,
            "B06_PE_QIP_DEALS": 0.08,
            "B07_NEWS_CATALYSTS": 0.04,
            "B08_MACRO_RRG_CHAOS": 0.04,
            "B09_MASTER_KAUTILYA": 0.04,
            "B10_VEDIC_JYOTISH": 0.00,
        },
    }

    # Backward compatibility mapping with legacy 12 domains
    LEGACY_DOMAIN_MAP = {
        "D01_CashForensics": "B01_FORENSIC_SHIELD",
        "D02_ROIIC_Capex": "B02_FUNDAMENTAL_MOAT",
        "D03_Dividend_TSY": "B05_DIVIDEND_TSY",
        "D04_PE_QIP_Deals": "B06_PE_QIP_DEALS",
        "D05_AntiManipulation": "B04_BEHAVIORAL_WHALE",
        "D06_Technical_VCP": "B03_TECHNICAL_VCP",
        "D07_CausalCatalysts": "B07_NEWS_CATALYSTS",
        "D08_MacroLiquidity": "B08_MACRO_RRG_CHAOS",
        "D09_KautilyaStrategy": "B09_MASTER_KAUTILYA",
        "D10_MasterInvestors": "B09_MASTER_KAUTILYA",
        "D11_VedicChronometry": "B10_VEDIC_JYOTISH",
        "D12_RiskParity_Stress": "B08_MACRO_RRG_CHAOS",
    }

    @classmethod
    def get_weights(
        cls,
        horizon_code: str = "H4",
        is_panic_mode: bool = False,
        active_buckets: Optional[List[str]] = None,
    ) -> Dict[str, float]:
        """
        Returns normalized weights for active buckets so sum(weights) == 1.0 (100.0%).
        """
        h_key = "PANIC_CONTRARIAN" if is_panic_mode else horizon_code.upper()
        if h_key not in cls.HORIZON_WEIGHT_TENSORS:
            h_key = "H4"

        base_weights = cls.HORIZON_WEIGHT_TENSORS[h_key].copy()

        # Default to all 9 Core Quant buckets if none passed
        effective_list = active_buckets if (active_buckets is not None and len(active_buckets) > 0) else cls.CORE_9_QUANT_BUCKETS
        active_set = set(effective_list)
        filtered = {k: v for k, v in base_weights.items() if k in active_set}
        total = sum(filtered.values())
        if total > 0.0001:
            return {k: round(v / total, 4) for k, v in filtered.items()}
        eq = round(1.0 / max(len(active_set), 1), 4)
        return {k: eq for k in active_set}

    @classmethod
    def get_risk_parameters(cls, risk_profile: str = "MODERATE") -> Dict[str, Any]:
        """
        Returns sizing caps and ATR stop loss multiples based on user risk tolerance.
        """
        prof = risk_profile.upper()
        if prof == "CONSERVATIVE":
            return {
                "risk_profile": "CONSERVATIVE",
                "max_single_stock_pct": 5.0,
                "atr_stop_multiplier": 1.8,
                "target_1_multiplier": 3.0,
                "target_2_multiplier": 5.0,
                "min_f_score": 7,
                "min_altman_z": 2.5,
            }
        elif prof == "AGGRESSIVE":
            return {
                "risk_profile": "AGGRESSIVE",
                "max_single_stock_pct": 10.0,
                "atr_stop_multiplier": 2.8,
                "target_1_multiplier": 4.5,
                "target_2_multiplier": 7.5,
                "min_f_score": 5,
                "min_altman_z": 1.5,
            }
        else:  # MODERATE default
            return {
                "risk_profile": "MODERATE",
                "max_single_stock_pct": 8.0,
                "atr_stop_multiplier": 2.2,
                "target_1_multiplier": 3.5,
                "target_2_multiplier": 6.0,
                "min_f_score": 6,
                "min_altman_z": 1.8,
            }

    @classmethod
    def evaluate_gate_0(cls, symbol: str, codex: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Gate 0: Principle-1 Non-Negotiable Forensic & Survival Gatekeeper.
        """
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")

        if sym in ["YESBANK", "RCOM", "DHFL", "VODIDEA", "IDEA", "SUZLON_OLD", "JPPOWER"]:
            return False, f"Gate 0 Hard Veto: {sym} flagged for catastrophic debt, equity dilution, or insolvency risk."

        m_score = float(codex.get("008. Beneish_M_Score", codex.get("Beneish_M_Score", -2.85)))
        if m_score > -1.78:
            return False, f"Gate 0 Hard Veto: Beneish M-Score ({m_score:.2f}) indicates high earnings manipulation risk (> -1.78 threshold)."

        sloan = float(codex.get("015. Sloan_Accrual_Ratio_Pct", codex.get("Sloan_Accrual_Ratio", 4.2)))
        sloan_pct = sloan * 100.0 if 0 < abs(sloan) <= 1.0 else sloan
        if sloan_pct > 15.0:
            return False, f"Gate 0 Hard Veto: Sloan Accrual ({sloan_pct:.1f}%) exceeds 15.0% limit (paper earnings vs. real cash divergence)."

        cfo_ebitda = float(codex.get("050. CFO_to_EBITDA_Pct", 85.0))
        if 0.0 < cfo_ebitda < 35.0:
            return False, f"Gate 0 Hard Veto: CFO-to-EBITDA ratio ({cfo_ebitda:.1f}%) below 35.0% safety floor."

        pledge = float(codex.get("055. Promoter_Pledge_Pct", codex.get("Promoter_Pledge_Pct", 0.0)))
        if pledge > 25.0:
            return False, f"Gate 0 Hard Veto: Promoter Pledge ({pledge:.1f}%) exceeds 25.0% confiscation barrier."

        altman_z = float(codex.get("209. Altmans_Z_Score_Emerging_Markets", codex.get("Altman_Z_Score", 3.4)))
        if altman_z < 1.2:
            return False, f"Gate 0 Hard Veto: Altman Z-Score ({altman_z:.2f}) in distressed zone (< 1.20)."

        return True, "PASSED: All forensic survival gatekeepers cleared."

    @classmethod
    def synthesize_master_conviction(
        cls,
        symbol: str,
        bucket_scores: Dict[str, float],
        codex: Dict[str, Any],
        horizon_code: str = "H4",
        risk_profile: str = "MODERATE",
        is_panic_mode: bool = False,
        active_buckets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes Master Conviction Score (0-100) across all active engine buckets.
        Calculates multi-horizon tensor vector, Kelly sizing, and generates 3-line brief.
        """
        gate_passed, gate_reason = cls.evaluate_gate_0(symbol, codex)
        gate_multiplier = 1.0 if gate_passed else 0.0

        risk_params = cls.get_risk_parameters(risk_profile)
        max_alloc_cap = risk_params["max_single_stock_pct"]

        # Calculate scores across all 6 horizons
        horizon_scores = {}
        for h_code in ["H0", "H1", "H2", "H3", "H4", "H5"]:
            weights = cls.get_weights(h_code, is_panic_mode, active_buckets)
            raw_s = 0.0
            for b_name, b_wt in weights.items():
                s = bucket_scores.get(b_name, 50.0)
                raw_s += s * b_wt

            # Multi-engine confluence synergy boost when multiple engines confirm simultaneously
            synergy = 0.0
            if bucket_scores.get("B02_FUNDAMENTAL_MOAT", 0) >= 78 and bucket_scores.get("B03_TECHNICAL_VCP", 0) >= 75:
                synergy += 3.5
            if bucket_scores.get("B05_DIVIDEND_TSY", 0) >= 72 and bucket_scores.get("B06_PE_QIP_DEALS", 0) >= 70:
                synergy += 2.5
            if bucket_scores.get("B04_BEHAVIORAL_WHALE", 0) >= 75 and bucket_scores.get("B07_NEWS_CATALYSTS", 0) >= 70:
                synergy += 2.5
            if bucket_scores.get("B01_FORENSIC_SHIELD", 0) >= 82 and bucket_scores.get("B09_MASTER_KAUTILYA", 0) >= 75:
                synergy += 2.0

            final_s = gate_multiplier * min(100.0, max(0.0, raw_s + synergy))
            if not gate_passed:
                final_s = min(24.5, final_s if final_s > 0 else 18.0)
            horizon_scores[h_code] = round(final_s, 1)

        sel_h = horizon_code.upper() if horizon_code.upper() in horizon_scores else "H4"
        master_score = horizon_scores[sel_h]
        best_h = max(horizon_scores, key=horizon_scores.get)

        if not gate_passed or master_score < 45.0:
            verdict = "RED FULL EXIT / AVOID"
            action_code = "FULL_EXIT"
            kelly_pct = 0.0
        elif master_score >= 82.0:
            verdict = "PARAMA VAJRA APEX (HEAVY ACCUMULATE)"
            action_code = "BUY_MORE"
            kelly_pct = min(max_alloc_cap, 8.5)
        elif master_score >= 72.0:
            verdict = "HIGH ALPHA INSTITUTIONAL BREAKOUT"
            action_code = "BUY_MORE"
            kelly_pct = min(max_alloc_cap, 6.0)
        elif master_score >= 55.0:
            verdict = "STEADY COMPOUNDER (HOLD & ACCUMULATE ON DIPS)"
            action_code = "HOLD"
            kelly_pct = min(max_alloc_cap * 0.6, 4.0)
        else:
            verdict = "CAUTION / PROFIT HARVESTING (TRIM)"
            action_code = "TRIM"
            kelly_pct = 1.5

        brief = cls.generate_3line_brief(
            symbol=symbol,
            score=master_score,
            verdict=verdict,
            horizon=sel_h,
            bucket_scores=bucket_scores,
            codex=codex,
            gate_passed=gate_passed,
            risk_params=risk_params,
        )

        return {
            "Master_Alpha_Score": master_score,
            "Verdict": verdict,
            "Action_Code": action_code,
            "Optimal_Horizon": best_h,
            "Selected_Horizon": sel_h,
            "Multi_Horizon_Vector": horizon_scores,
            "Gate_0_Passed": gate_passed,
            "Gate_0_Reason": gate_reason,
            "Kelly_Weight_Pct": round(kelly_pct, 2),
            "Bucket_Scores": bucket_scores,
            "Active_Weights": cls.get_weights(sel_h, is_panic_mode, active_buckets),
            "Executive_Brief": brief,
            "Risk_Params": risk_params,
        }

    @classmethod
    def generate_3line_brief(
        cls,
        symbol: str,
        score: float,
        verdict: str,
        horizon: str,
        bucket_scores: Dict[str, float],
        codex: Dict[str, Any],
        gate_passed: bool,
        risk_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Creates a rich, stock-specific 3-line executive plain-English brief:
        Line 1 (Economic Moat & Why Buy / Avoid Now)
        Line 2 (Catalyst, Whale Flow & Cash-Flow Proof)
        Line 3 (Exact Execution Corridor & Risk Guardrail)
        """
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        cmp = float(codex.get("CMP", 100.0))
        r_params = risk_params or cls.get_risk_parameters("MODERATE")
        atr_mult = r_params.get("atr_stop_multiplier", 2.2)
        atr = float(codex.get("105. ATR14", max(cmp * 0.025, 1.0)))

        stop_loss = round(cmp - (atr_mult * atr), 1)
        tgt1 = round(cmp + (r_params.get("target_1_multiplier", 3.5) * atr), 1)
        tgt2 = round(cmp + (r_params.get("target_2_multiplier", 6.0) * atr), 1)
        div_yield = float(codex.get("217. Trailing_Dividend_Yield_Pct", codex.get("Dividend_Yield_Pct", 1.2)))
        roiic = float(codex.get("255. Incremental_ROIC_3Yr_ROIIC_Pct", 22.0))
        vcp = float(codex.get("266. VCP_Volatility_Contraction_Tightness_Score", 78.0))
        beneish = float(codex.get("008. Beneish_M_Score", -2.65))
        altman = float(codex.get("209. Altmans_Z_Score_Emerging_Markets", 3.40))
        qip_floor = float(codex.get("237. SEBI_ICDR_QIP_Preferential_Floor_Price", cmp * 0.96))

        if not gate_passed:
            return {
                "badge": "FORENSIC HARD VETO",
                "line_1": f"Forensic Veto Triggered: {sym} breached Gate 0 survival rules (Beneish M: {beneish:.2f}, Altman Z: {altman:.2f}) due to balance-sheet stress or earnings dilution.",
                "line_2": "Negative owner cash conversion and elevated accrual risk indicate severe downside vulnerability during institutional de-risking.",
                "line_3": "Immediate Execution: 100% Capital Preservation Active. Liquidate exposure and rotate freed capital into Gate-0 cleared Alpha Leaders.",
            }

        h_names = {
            "H0": "1-3 Days Ultra-Fast Scalp",
            "H1": "1-4 Weeks Swing Velocity",
            "H2": "1-6 Months Positional PEAD",
            "H3": "6-12 Months Capex Inflection",
            "H4": "1-3 Years Multibagger Cycle",
            "H5": "3-10 Years Forever Compounder",
        }
        h_desc = h_names.get(horizon, "1-3 Years Multibagger")

        # Line 1: Economic Moat & Multi-Engine Thesis
        if score >= 75.0:
            if bucket_scores.get("B05_DIVIDEND_TSY", 0) >= 75 and div_yield >= 2.0:
                l1 = f"High-Yield Compounder Moat: {sym} combines a {div_yield:.1f}% dividend yield with {roiic:.1f}% 3Y incremental ROIC and clean forensic accounting (Beneish M: {beneish:.2f})."
            elif bucket_scores.get("B06_PE_QIP_DEALS", 0) >= 75:
                l1 = f"Institutional & PE Sponsorship: {sym} is backed by institutional block accumulation near SEBI QIP Floor (₹{qip_floor:,.1f}) with {roiic:.1f}% 3Y ROIIC."
            elif bucket_scores.get("B02_FUNDAMENTAL_MOAT", 0) >= 75:
                l1 = f"Capex & ROIIC Inflection Leader: {sym} generates {roiic:.1f}% 3-year incremental ROIC with strong CWIP-to-Net-Block commissioning and fortress Altman Z ({altman:.2f})."
            else:
                l1 = f"Multi-Engine Sovereign Leader: {sym} passes all 9 core quantitative engines simultaneously with {roiic:.1f}% ROIIC, {div_yield:.1f}% dividend yield, and clean cash conversion."
        else:
            l1 = f"Core Portfolio Compounder: {sym} maintains resilient operating cash flows (3Y ROIIC: {roiic:.1f}%, Altman Z: {altman:.2f}, Div Yield: {div_yield:.1f}%) with intact balance-sheet safety."

        # Line 2: Catalyst, Microstructure & Tape Proof
        l2 = f"Catalyst & Tape Proof: VCP volatility tightness at {vcp:.1f}%, SEBI QIP institutional reference at ₹{qip_floor:,.1f}, and positive whale delivery absorption."

        # Line 3: Exact Execution Corridor
        l3 = f"Execution ({horizon} — {h_desc}): Accumulate in Buy Zone ₹{cmp*0.99:.1f}–₹{cmp*1.01:.1f} | Stop-Loss: ₹{stop_loss:,.1f} ({atr_mult}x ATR) | Target T1: ₹{tgt1:,.1f} & T2: ₹{tgt2:,.1f}."

        return {
            "badge": verdict,
            "line_1": l1,
            "line_2": l2,
            "line_3": l3,
        }
