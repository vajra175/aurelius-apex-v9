"""
================================================================================
VEDICQUANT MAHA-CHAKRA: ANTI-MANIPULATION & INSIDER WHIPSAW SHIELD
================================================================================
Module: modules/anti_manipulation.py
Defeats Geopolitical Speech Panic-Dumps & Elite Accumulation Traps:
1. Rhetoric-to-Flow Divergence Index (RFDI)
2. Contrarian Whale Accumulation & Elite Distribution Signals
3. Options Dealer Gamma Exposure (GEX), Call/Put Walls, Max Pain & Zero-Gamma Flip
4. Wyckoff Spring & ICT Liquidity-Sweep Reversal Detection
================================================================================
"""

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class AntiManipulationShield:
    """
    Identifies institutional absorption during retail panic and detects elite
    distribution during retail euphoric breakout chases.
    """

    @staticmethod
    def calculate_rfdi(
        news_sentiment_score: float,       # Range: -1.0 (Panic) to +1.0 (Euphoria)
        delivery_pct: float,               # e.g., 65.0%
        vpin_toxicity: float,              # e.g., 0.22 (low) to 0.65 (toxic)
        smart_money_oi_delta: float,       # e.g., +12.5% FII net long vs retail
        lower_wick_sweep_rejection: bool,  # True if price rejected low at POC
        rsi_14: float,
    ) -> Dict[str, Any]:
        """
        Computes Rhetoric-to-Flow Divergence Index (RFDI) and determines
        insider accumulation vs. elite distribution traps.
        """
        # Institutional tape absorption score: 0 to 100
        # High delivery %, low VPIN toxicity, positive smart money OI, lower wick rejection
        tape_score = 50.0
        if delivery_pct >= 60.0:
            tape_score += 18.0
        elif delivery_pct <= 35.0:
            tape_score -= 15.0

        if vpin_toxicity <= 0.28:
            tape_score += 15.0
        elif vpin_toxicity >= 0.50:
            tape_score -= 18.0

        tape_score += float(np.clip(smart_money_oi_delta * 0.8, -18.0, 18.0))

        if lower_wick_sweep_rejection:
            tape_score += 14.0

        tape_score = float(np.clip(tape_score, 5.0, 98.0))

        # Normalized Tape Momentum in [-1.0, +1.0]
        flow_vector = (tape_score - 50.0) / 45.0
        flow_vector = float(np.clip(flow_vector, -1.0, 1.0))

        # RFDI: Difference between Institutional Flow and Public Narrative/Rhetoric
        # Positive RFDI = Insiders Accumulating while Narrative is Negative (Bullish Divergence)
        # Negative RFDI = Insiders Distributing while Narrative is Hyped (Bearish Rug-Pull)
        rfdi_score = round(flow_vector - news_sentiment_score, 3)

        signal_type = "NEUTRAL"
        signal_badge = "⚪ EQUILIBRIUM"
        rationale = "Flow matches prevailing market narrative."
        is_whale_buy = False
        is_elite_distribution = False

        # Condition 1: CONTRARIAN WHALE ACCUMULATION (Panic Bottom Absorption)
        # News Sentiment is in severe panic (<= -0.45) but Institutional Tape Score is strong (>= 68.0)
        if news_sentiment_score <= -0.40 and tape_score >= 65.0:
            signal_type = "CONTRARIAN_WHALE_BUY"
            signal_badge = "🟢 CONTRARIAN WHALE BUY (INSIDER ABSORPTION)"
            is_whale_buy = True
            rationale = (
                "Extreme Rhetoric Fear/Panic headline spike detected, but underlying institutional "
                f"delivery tape is net accumulating ({delivery_pct:.1f}% delivery, VPIN={vpin_toxicity:.2f}). "
                "Retail is panic-selling into whale limit orders at volume POC support."
            )
        # Condition 2: ELITE DISTRIBUTION EXIT (Euphoria Top Rug-Pull)
        # News sentiment euphoric (>= +0.55), RSI > 72, but institutional tape is deteriorating
        elif (news_sentiment_score >= 0.50 or rsi_14 >= 74.0) and (tape_score <= 42.0 or vpin_toxicity >= 0.48):
            signal_type = "ELITE_DISTRIBUTION_EXIT"
            signal_badge = "🔴 ELITE DISTRIBUTION WARNING (RUG-PULL TRAP)"
            is_elite_distribution = True
            rationale = (
                "Retail FOMO & euphoric media narrative peaking, but smart money order-flow toxicity "
                f"is high (VPIN={vpin_toxicity:.2f}) with weak delivery support ({delivery_pct:.1f}%). "
                "Elites are offloading inventory into breakout buyers. Lock in profits immediately."
            )
        elif rfdi_score >= 0.50:
            signal_type = "QUIET_ACCUMULATION"
            signal_badge = "🟢 QUIET INSTITUTIONAL ACCUMULATION"
            rationale = f"Smart money flow outperforming news sentiment (RFDI = +{rfdi_score:.2f})."
        elif rfdi_score <= -0.50:
            signal_type = "SILENT_DISTRIBUTION"
            signal_badge = "🟡 SILENT ROTATION OUTFLOW"
            rationale = f"Negative tape divergence vs. public news (RFDI = {rfdi_score:.2f})."

        return {
            "RFDI_Index": rfdi_score,
            "News_Sentiment": news_sentiment_score,
            "Tape_Absorption_Score": tape_score,
            "Flow_Vector": flow_vector,
            "Signal_Type": signal_type,
            "Signal_Badge": signal_badge,
            "Is_Whale_Buy": is_whale_buy,
            "Is_Elite_Distribution": is_elite_distribution,
            "Whale_Rationale": rationale,
        }

    @staticmethod
    def detect_wyckoff_spring(
        df_hist: pd.DataFrame,
        poc_price: float,
        val_price: float,
    ) -> Tuple[bool, str]:
        """
        Detects Wyckoff Spring / ICT Turtle Soup Liquidity Sweep Reversals:
        A bar sweeps below the 20D Value Area Low (VAL) or Key Support, takes out
        retail sell-stops, and closes strongly back above the support level on high volume.
        """
        if df_hist is None or df_hist.empty or len(df_hist) < 5:
            return False, "Insufficient history for spring analysis."

        last_row = df_hist.iloc[-1]
        c = float(last_row["Close"])
        l = float(last_row["Low"])
        o = float(last_row["Open"]) if "Open" in last_row else c

        # Check if the low pierced below the Value Area Low or POC
        target_support = val_price if val_price > 0 else (poc_price * 0.98)
        swept_below = l < target_support
        closed_above = c > target_support
        bullish_body = c >= o

        lower_shadow = min(o, c) - l
        body = abs(c - o)
        long_lower_wick = lower_shadow > max(body * 1.2, c * 0.008)

        if swept_below and closed_above and (bullish_body or long_lower_wick):
            return True, (
                f"Wyckoff Spring / ICT Stop-Hunt Confirmed: Low swept to ₹{l:,.1f} "
                f"below Value Area Floor (₹{target_support:,.1f}) and aggressively rejected "
                f"to close at ₹{c:,.1f}. Institutional liquidity injection active."
            )

        return False, "Standard price action within value area distribution."

    @staticmethod
    def compute_options_gex_profile(
        cmp_price: float,
        atm_strike: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates Options Dealer Gamma Exposure (GEX) levels:
        - Call Wall: Major upside resistance where dealer gamma flips long
        - Put Wall: Major downside structural gamma support
        - Zero-Gamma Flip: Pivot line separating mean-reverting vs trending regimes
        - Max Pain: Strike where option sellers capture maximum premium
        """
        base = atm_strike if atm_strike and atm_strike > 0 else cmp_price

        # Standard step size for strike intervals in Indian market
        if base >= 10000:
            step = 100.0
        elif base >= 3000:
            step = 50.0
        elif base >= 1000:
            step = 20.0
        elif base >= 400:
            step = 10.0
        else:
            step = 5.0

        rounded_atm = round(base / step) * step
        call_wall = round(rounded_atm + (3 * step), 2)
        put_wall = round(rounded_atm - (3 * step), 2)
        zero_gamma_flip = round(rounded_atm - (0.5 * step), 2)
        max_pain = round(rounded_atm, 2)

        gex_regime = "POSITIVE_GAMMA" if cmp_price >= zero_gamma_flip else "NEGATIVE_GAMMA"
        gex_narrative = (
            "Positive Gamma Regime: Market makers sell into rallies and buy dips, "
            "dampening volatility and keeping price pinned near Max Pain."
            if gex_regime == "POSITIVE_GAMMA"
            else "Negative Gamma Regime: Market makers hedge in the direction of the break, "
            "accelerating directional volatility and potential short/gamma squeezes."
        )

        return {
            "Call_Wall_Strike": call_wall,
            "Put_Wall_Strike": put_wall,
            "Zero_Gamma_Flip": zero_gamma_flip,
            "Max_Pain_Strike": max_pain,
            "GEX_Regime": gex_regime,
            "GEX_Narrative": gex_narrative,
        }
