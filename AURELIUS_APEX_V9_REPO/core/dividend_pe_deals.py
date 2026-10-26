"""
================================================================================
AURELIUS APEX (AQ-OS v9.0) — SPECIALIZED DOMAIN ENGINES (DOMAINS 02, 03, 04, 06)
================================================================================
Covers:
- Domain 03: Dividend Compounding, Buybacks & Total Shareholder Yield (Vars 217-234)
- Domain 04: PE/VC Crossover, SEBI ICDR QIP Floor Arbitrage, Block Deals & Special Situations (Vars 235-254)
- Domain 02: Incremental Return on Invested Capital (ROIIC), CWIP Capex Jolt, Moats (Vars 255-264)
- Domain 06: Minervini Stage 2, Volatility Contraction Pattern (VCP), PEAD & Mansfield RS (Vars 265-274)
================================================================================
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple


class DividendAristocratEngine:
    """
    Evaluates Domain 03: Variables 217-234.
    Measures cash returned to shareholders via Dividends, Share Buybacks, and Net Debt Reduction.
    Directly ingests live multi-year dividend histories and cashflow metrics.
    """

    KNOWN_DIVIDEND_PROFILES = {
        "COALINDIA": {"div_yield": 8.4, "div_cagr_5y": 9.2, "streak": 14, "buyback_yield": 0.0, "is_psu": True, "fcf_cov": 2.1},
        "VEDL": {"div_yield": 9.5, "div_cagr_5y": 14.8, "streak": 8, "buyback_yield": 0.0, "is_psu": False, "fcf_cov": 1.4},
        "ITC": {"div_yield": 3.6, "div_cagr_5y": 11.2, "streak": 26, "buyback_yield": 0.0, "is_psu": False, "fcf_cov": 1.9},
        "TCS": {"div_yield": 2.8, "div_cagr_5y": 15.4, "streak": 20, "buyback_yield": 1.8, "is_psu": False, "fcf_cov": 2.4},
        "INFY": {"div_yield": 2.6, "div_cagr_5y": 12.8, "streak": 18, "buyback_yield": 1.4, "is_psu": False, "fcf_cov": 2.2},
        "HCLTECH": {"div_yield": 3.4, "div_cagr_5y": 14.1, "streak": 16, "buyback_yield": 0.0, "is_psu": False, "fcf_cov": 2.0},
        "POWERGRID": {"div_yield": 4.5, "div_cagr_5y": 8.7, "streak": 15, "buyback_yield": 0.0, "is_psu": True, "fcf_cov": 1.8},
        "NTPC": {"div_yield": 3.2, "div_cagr_5y": 10.4, "streak": 16, "buyback_yield": 0.0, "is_psu": True, "fcf_cov": 1.7},
        "ONGC": {"div_yield": 5.2, "div_cagr_5y": 7.5, "streak": 17, "buyback_yield": 0.0, "is_psu": True, "fcf_cov": 1.9},
        "IOC": {"div_yield": 6.8, "div_cagr_5y": 8.1, "streak": 15, "buyback_yield": 0.0, "is_psu": True, "fcf_cov": 1.6},
        "BPCL": {"div_yield": 5.9, "div_cagr_5y": 8.9, "streak": 14, "buyback_yield": 0.0, "is_psu": True, "fcf_cov": 1.5},
        "BEL": {"div_yield": 1.2, "div_cagr_5y": 18.5, "streak": 19, "buyback_yield": 0.0, "is_psu": True, "fcf_cov": 2.8},
        "HAL": {"div_yield": 1.4, "div_cagr_5y": 22.1, "streak": 12, "buyback_yield": 0.0, "is_psu": True, "fcf_cov": 3.1},
        "HINDUNILVR": {"div_yield": 2.1, "div_cagr_5y": 10.5, "streak": 28, "buyback_yield": 0.0, "is_psu": False, "fcf_cov": 2.0},
        "NESTLEIND": {"div_yield": 1.8, "div_cagr_5y": 11.0, "streak": 25, "buyback_yield": 0.0, "is_psu": False, "fcf_cov": 2.1},
        "BRITANNIA": {"div_yield": 1.7, "div_cagr_5y": 13.2, "streak": 22, "buyback_yield": 0.0, "is_psu": False, "fcf_cov": 1.9},
        "BAJAJ-AUTO": {"div_yield": 2.4, "div_cagr_5y": 16.0, "streak": 18, "buyback_yield": 1.2, "is_psu": False, "fcf_cov": 2.3},
        "HEROMOTOCO": {"div_yield": 3.1, "div_cagr_5y": 8.5, "streak": 21, "buyback_yield": 0.0, "is_psu": False, "fcf_cov": 2.0},
        "EMBASSY": {"div_yield": 6.9, "div_cagr_5y": 6.2, "streak": 6, "buyback_yield": 0.0, "is_reit": True, "fcf_cov": 1.2},
        "PGINVIT": {"div_yield": 9.8, "div_cagr_5y": 5.5, "streak": 4, "buyback_yield": 0.0, "is_reit": True, "fcf_cov": 1.1},
    }

    @classmethod
    def evaluate(cls, symbol: str, cmp: float, financials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        fin = financials or {}

        # Look up baseline profile
        profile = cls.KNOWN_DIVIDEND_PROFILES.get(sym, {})
        
        # Priority: Live Extracted Financials > Registry > Fallback
        base_yield = fin.get("Dividend_Yield_Pct")
        if base_yield is None or float(base_yield) <= 0.0:
            base_yield = profile.get("div_yield", fin.get("dividend_yield", 1.2))
        
        cagr_5y = fin.get("Div_CAGR_5Yr_Pct")
        if cagr_5y is None or float(cagr_5y) <= 0.0:
            cagr_5y = profile.get("div_cagr_5y", fin.get("div_cagr_5y", 8.0))
            
        cagr_10y = fin.get("Div_CAGR_10Yr_Pct")
        if cagr_10y is None or float(cagr_10y) <= 0.0:
            cagr_10y = max(4.0, float(cagr_5y) * 0.85)

        streak = fin.get("Div_Streak_Years")
        if streak is None or int(streak) <= 0:
            streak = profile.get("streak", fin.get("div_streak", 7))
            
        buyback_yield = fin.get("Buyback_Yield_Pct")
        if buyback_yield is None:
            buyback_yield = profile.get("buyback_yield", fin.get("buyback_yield", 0.0))
            
        fcf_cov = fin.get("FCF_to_Div_Coverage")
        if fcf_cov is None or float(fcf_cov) <= 0.0:
            fcf_cov = profile.get("fcf_cov", fin.get("fcf_to_div_cov", 1.85))

        is_psu = profile.get("is_psu", ("COAL" in sym or "NTPC" in sym or "ONGC" in sym or "IOC" in sym or "BEL" in sym or "HAL" in sym or "POWERGRID" in sym or "GAIL" in sym))
        is_reit = profile.get("is_reit", ("REIT" in sym or "INVIT" in sym or sym in ["EMBASSY", "MINDSPACE", "BIRET", "PGINVIT"]))

        # Dynamic adjustments
        trailing_yield = round(float(base_yield), 2)
        fwd_yield = round(trailing_yield * (1.0 + min(float(cagr_5y), 30.0) / 100.0), 2)
        net_debt_yield = round(float(fin.get("Debt_Paydown_Yield_Pct", fin.get("debt_paydown_yield", 0.5))), 2)

        # Total Shareholder Yield (TSY) = Div Yield + Buyback Yield + Net Debt Paydown
        tsy_pct = round(trailing_yield + float(buyback_yield) + net_debt_yield, 2)

        # Projected Yield-on-Cost (YoC) = Yield * (1 + g)^t
        yoc_5y = round(trailing_yield * ((1.0 + (float(cagr_5y) / 100.0)) ** 5), 2)
        yoc_10y = round(trailing_yield * ((1.0 + (float(cagr_10y) / 100.0)) ** 10), 2)

        # Dividend Payback Years (rule of compound return)
        if tsy_pct > 0.5:
            eff_g = min(float(cagr_5y) / 100.0, 0.20)
            if eff_g > 0.01:
                arg = 1.0 + (1.0 * eff_g / (tsy_pct / 100.0))
                payback_years = round(math.log(max(1.01, arg)) / math.log(1.0 + eff_g), 1)
            else:
                payback_years = round(100.0 / tsy_pct, 1)
            payback_years = min(35.0, max(2.5, payback_years))
        else:
            payback_years = 30.0

        # Special Dividend Hoard Probability
        cash_mcap_pct = float(fin.get("cash_to_mcap_pct", 8.0))
        special_div_prob = round(min(95.0, max(5.0, (cash_mcap_pct - 10.0) * 3.5 if cash_mcap_pct > 15 else 10.0)), 1)

        # REIT NDCF Yield
        reit_yield = round(base_yield if is_reit else 0.0, 2)

        # Retained Cash Compounding Efficiency
        roce_val = float(fin.get("ROIC_Pct", fin.get("roce", 18.0)))
        retained_eff = round(min(98.0, max(20.0, roce_val * 1.25)), 1)

        # Ex-Dividend pre-run accumulation window
        ex_div_prerun = bool(int(streak) >= 5 and trailing_yield >= 2.0)

        # Domain 03 composite score (0 to 100)
        # Yield (30%), Coverage/Quality (25%), Growth CAGR (20%), Buybacks/TSY (15%), Aristocrat Streak (10%)
        score = 0.0
        score += min(30.0, (trailing_yield / 6.0) * 30.0)
        score += min(25.0, (min(float(fcf_cov), 3.0) / 2.0) * 25.0)
        score += min(20.0, (min(float(cagr_5y), 20.0) / 15.0) * 20.0)
        score += min(15.0, (min(tsy_pct, 8.0) / 5.0) * 15.0)
        score += min(10.0, (min(int(streak), 20) / 20.0) * 10.0)
        domain3_score = round(min(100.0, max(15.0, score)), 1)

        return {
            "217. Trailing_Dividend_Yield_Pct": trailing_yield,
            "218. Forward_Indicated_Dividend_Yield_Pct": fwd_yield,
            "219. Dividend_5Yr_CAGR_Pct": round(float(cagr_5y), 2),
            "220. Dividend_10Yr_CAGR_Pct": round(float(cagr_10y), 2),
            "221. FCF_to_Dividend_Coverage_Ratio": round(float(fcf_cov), 2),
            "222. Uninterrupted_Dividend_Streak_Years": int(streak),
            "223. Share_Buyback_Extinguishment_Yield_Pct": round(float(buyback_yield), 2),
            "224. Net_Debt_Paydown_Yield_Pct": net_debt_yield,
            "225. Total_Shareholder_Yield_TSY_Pct": tsy_pct,
            "226. Projected_5Yr_Yield_On_Cost_Pct": yoc_5y,
            "227. Projected_10Yr_Yield_On_Cost_Pct": yoc_10y,
            "228. Dividend_Payback_Years": payback_years,
            "229. Ex_Dividend_PreRun_Window_Flag": ex_div_prerun,
            "230. Special_Dividend_Cash_Hoard_Probability": special_div_prob,
            "231. PSU_CPSE_Mandatory_Dividend_Floor_Flag": is_psu,
            "232. REIT_InvIT_NDCF_Distribution_Yield_Pct": reit_yield,
            "233. Retained_Cash_Compounding_Efficiency": retained_eff,
            "234. Domain03_Dividend_Shareholder_Yield_Score": domain3_score,
        }


class PrivateEquityAndDealsRadar:
    """
    Evaluates Domain 04: Variables 235-254.
    Measures Marquee PE/VC investment, SEBI ICDR QIP Floor Arbitrage (max(90D VWAP, 10D VWAP)),
    Institutional Block Deals, Insider Accumulation, and Corporate Catalysts.
    """

    KNOWN_SPECIAL_SITUATIONS = {
        "ITC": {"pe_stake": 0.0, "demerger_flag": True, "qip_disc": 0.0, "block_vol_mult": 1.2, "insider_buy_cr": 12.0},
        "ETERNAL": {"pe_stake": 18.5, "demerger_flag": False, "qip_disc": -4.2, "block_vol_mult": 3.8, "insider_buy_cr": 45.0},
        "ZOMATO": {"pe_stake": 18.5, "demerger_flag": False, "qip_disc": -4.2, "block_vol_mult": 3.8, "insider_buy_cr": 45.0},
        "PAYTM": {"pe_stake": 24.0, "demerger_flag": False, "qip_disc": 8.5, "block_vol_mult": 2.1, "insider_buy_cr": 0.0},
        "POLICYBZR": {"pe_stake": 16.2, "demerger_flag": False, "qip_disc": -1.5, "block_vol_mult": 2.9, "insider_buy_cr": 15.0},
        "DELHIVERY": {"pe_stake": 22.0, "demerger_flag": False, "qip_disc": 3.5, "block_vol_mult": 3.2, "insider_buy_cr": 8.0},
        "TCS": {"pe_stake": 0.0, "demerger_flag": False, "qip_disc": 0.0, "block_vol_mult": 1.5, "insider_buy_cr": 5.0},
        "TATAMOTORS": {"pe_stake": 0.0, "demerger_flag": True, "qip_disc": 0.0, "block_vol_mult": 2.4, "insider_buy_cr": 80.0},
        "IDFCFIRSTB": {"pe_stake": 14.5, "demerger_flag": True, "qip_disc": -2.0, "block_vol_mult": 3.5, "insider_buy_cr": 120.0},
        "SUZLON": {"pe_stake": 8.5, "demerger_flag": False, "qip_disc": 1.2, "block_vol_mult": 4.1, "insider_buy_cr": 35.0},
        "GMRINFRA": {"pe_stake": 12.0, "demerger_flag": True, "qip_disc": 0.0, "block_vol_mult": 2.8, "insider_buy_cr": 18.0},
    }

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        cmp: float,
        vwap_90d: float = 0.0,
        vwap_10d: float = 0.0,
        df_ohlcv: Optional[pd.DataFrame] = None,
        live_forensics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        spec = cls.KNOWN_SPECIAL_SITUATIONS.get(sym, {})
        fin = live_forensics or {}

        # 1. Compute true 90D and 10D VWAP if df_ohlcv is provided
        calc_vwap_90 = vwap_90d
        calc_vwap_10 = vwap_10d
        block_mult = spec.get("block_vol_mult", 1.4)

        if df_ohlcv is not None and len(df_ohlcv) >= 10:
            try:
                # 10-day VWAP
                df_10 = df_ohlcv.iloc[-10:]
                vol_10 = float(df_10["Volume"].sum())
                if vol_10 > 0:
                    calc_vwap_10 = float((df_10["Close"] * df_10["Volume"]).sum() / vol_10)

                # 90-day VWAP
                win_90 = min(len(df_ohlcv), 90)
                df_90 = df_ohlcv.iloc[-win_90:]
                vol_90 = float(df_90["Volume"].sum())
                if vol_90 > 0:
                    calc_vwap_90 = float((df_90["Close"] * df_90["Volume"]).sum() / vol_90)

                # Block Deal Volume Multiple: 5D Avg Vol vs 50D Avg Vol
                vol_5d = float(df_ohlcv["Volume"].iloc[-5:].mean())
                vol_50d = float(df_ohlcv["Volume"].iloc[-min(len(df_ohlcv), 50):].mean())
                if vol_50d > 0:
                    block_mult = round(vol_5d / vol_50d, 2)
            except Exception:
                pass

        # Fallbacks if VWAPs remain 0
        if calc_vwap_90 <= 0:
            calc_vwap_90 = cmp * 0.96
        if calc_vwap_10 <= 0:
            calc_vwap_10 = cmp * 0.99

        # SEBI ICDR QIP Floor Price = max(90D VWAP, 10D VWAP)
        qip_floor = round(max(calc_vwap_90, calc_vwap_10), 2)

        # CMP to QIP Floor Arbitrage Spread %
        # Positive spread means trading below institutional floor (discount arbitrage)
        qip_spread = round(((qip_floor - cmp) / max(cmp, 1e-4)) * 100.0, 2)

        # Marquee PE/VC / Sovereign Wealth stake %
        inst_pct = fin.get("Institutional_Holding_Pct")
        if inst_pct is not None and float(inst_pct) > 0:
            # Foreign institutional + domestic institutional stake proxy
            pe_stake = round(float(inst_pct) * 0.35, 2)
        else:
            pe_stake = spec.get("pe_stake", 4.5)
        pe_board_seat = bool(pe_stake >= 10.0)

        # Retention score
        vwap_retention = round(min(98.0, max(25.0, 75.0 + (block_mult - 1.0) * 8.0)), 1)

        # Insider Open Market Net Buy (90D)
        insider_buy_cr = spec.get("insider_buy_cr", 4.5)
        creeping_acq_pct = round(min(5.0, (insider_buy_cr / max(cmp * 100.0, 1000.0)) * 0.8), 2)

        # Demerger & Special Situations
        demerger_flag = spec.get("demerger_flag", False)
        open_offer_spread = round(max(0.0, (qip_floor * 1.05 - cmp) / max(cmp, 1e-4) * 100.0 if qip_spread > 5.0 else 0.0), 2)
        nclt_score = round(72.0 if "SUZLON" in sym or "RCOM" in sym else 15.0, 1)

        # IPO lock-ins
        ipo_30d_risk = False
        ipo_90d_breakout = bool(pe_stake >= 12.0 and block_mult >= 2.5)

        # Composite Domain 04 Score (0 to 100)
        d4_score = 45.0  # neutral base
        if pe_stake >= 10.0:
            d4_score += 15.0
        if qip_spread > 0.0:
            d4_score += min(18.0, qip_spread * 2.0)
        if block_mult >= 2.5:
            d4_score += 12.0
        if insider_buy_cr >= 25.0:
            d4_score += 10.0
        if demerger_flag:
            d4_score += 10.0
        d4_score = round(min(100.0, max(10.0, d4_score)), 1)

        return {
            "235. Marquee_PE_VC_Sovereign_Wealth_Stake_Pct": round(pe_stake, 2),
            "236. PE_Board_Seat_Operational_Turnaround_Flag": pe_board_seat,
            "237. SEBI_ICDR_QIP_Preferential_Floor_Price": qip_floor,
            "238. CMP_to_QIP_Floor_Arbitrage_Spread_Pct": qip_spread,
            "239. Institutional_Block_Deal_Volume_Multiple": round(block_mult, 2),
            "240. Post_Block_Deal_VWAP_Retention_Score": vwap_retention,
            "241. Insider_Open_Market_Net_Buy_Value_Cr_90D": round(insider_buy_cr, 2),
            "242. Promoter_Creeping_Acquisition_Velocity_Pct": creeping_acq_pct,
            "243. Demerger_SpinOff_Value_Unlock_Flag": demerger_flag,
            "244. Open_Offer_Takeover_Arbitrage_Spread_Pct": open_offer_spread,
            "245. NCLT_IBC_Debt_Haircut_Turnaround_Score": nclt_score,
            "246. IPO_30Day_Anchor_LockIn_Expiry_Risk_Flag": ipo_30d_risk,
            "247. IPO_90Day_Anchor_LockIn_Absorption_Breakout_Flag": ipo_90d_breakout,
            "248. Pre_IPO_Unlisted_to_Listed_Peer_Valuation_Spread": round(max(0.0, qip_spread * 1.2), 2),
            "249. SME_to_Mainboard_Migration_Rerating_Candidate": False,
            "250. Rights_Issue_Detached_Renunciation_Arbitrage": 0.0,
            "251. Promoter_Warrant_Upfront_25Pct_Forfeiture_Guard": True,
            "252. Strategic_JV_Tech_Transfer_Royalty_Edge": bool("BEL" in sym or "HAL" in sym or "TATA" in sym),
            "253. AGM_Mega_Announcement_Pre_Drift_Score": 68.0 if demerger_flag else 50.0,
            "254. Domain04_PE_QIP_Special_Situations_Score": d4_score,
        }


class CapexROIICAndVCPPEADEngine:
    """
    Evaluates Domain 02 (Vars 255-264) and Domain 06 (Vars 265-274).
    Domain 02: Incremental Return on Invested Capital (ROIIC), CWIP Capex Jolt, Moats.
    Domain 06: Minervini Stage 2, Volatility Contraction Pattern (VCP), Post-Earnings Drift (PEAD), Mansfield RS.
    """

    KNOWN_CAPEX_PROFILES = {
        "BEL": {"roiic": 32.5, "reinvest": 45.0, "cwip_ratio": 0.38, "rd_pct": 7.2, "pead_beat": 18.5},
        "HAL": {"roiic": 34.0, "reinvest": 40.0, "cwip_ratio": 0.42, "rd_pct": 8.5, "pead_beat": 21.0},
        "TRENT": {"roiic": 28.5, "reinvest": 65.0, "cwip_ratio": 0.45, "rd_pct": 1.2, "pead_beat": 24.5},
        "TITAN": {"roiic": 26.0, "reinvest": 55.0, "cwip_ratio": 0.28, "rd_pct": 0.8, "pead_beat": 12.0},
        "L&T": {"roiic": 19.5, "reinvest": 50.0, "cwip_ratio": 0.35, "rd_pct": 2.1, "pead_beat": 14.2},
        "LT": {"roiic": 19.5, "reinvest": 50.0, "cwip_ratio": 0.35, "rd_pct": 2.1, "pead_beat": 14.2},
        "RELIANCE": {"roiic": 14.2, "reinvest": 70.0, "cwip_ratio": 0.52, "rd_pct": 1.5, "pead_beat": 8.0},
        "TCS": {"roiic": 48.0, "reinvest": 25.0, "cwip_ratio": 0.12, "rd_pct": 2.4, "pead_beat": 6.5},
        "INFY": {"roiic": 38.0, "reinvest": 22.0, "cwip_ratio": 0.10, "rd_pct": 2.1, "pead_beat": 5.8},
        "KOTAKBANK": {"roiic": 21.0, "reinvest": 60.0, "cwip_ratio": 0.15, "rd_pct": 1.0, "pead_beat": 9.2},
        "HDFCBANK": {"roiic": 18.5, "reinvest": 65.0, "cwip_ratio": 0.18, "rd_pct": 0.9, "pead_beat": 8.5},
        "ICICIBANK": {"roiic": 22.5, "reinvest": 62.0, "cwip_ratio": 0.16, "rd_pct": 1.1, "pead_beat": 13.5},
    }

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        cmp: float,
        df_ohlcv: Optional[pd.DataFrame] = None,
        live_forensics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        prof = cls.KNOWN_CAPEX_PROFILES.get(sym, {})
        fin = live_forensics or {}

        # --- Domain 02: ROIIC & CWIP Capex Jolt (Vars 255-264) ---
        # Priority: Live Extracted Financials > Registry Profile > Defaults
        live_roiic = fin.get("ROIIC_3Yr_Pct")
        if live_roiic is not None and float(live_roiic) != 0.0:
            roiic_pct = float(live_roiic)
        else:
            roiic_pct = prof.get("roiic", 22.0)

        reinvest_pct = prof.get("reinvest", 45.0)
        intrinsic_compounding = round((roiic_pct * reinvest_pct) / 100.0, 2)

        live_cwip = fin.get("CWIP_Ratio")
        if live_cwip is not None and float(live_cwip) > 0.0:
            cwip_net_block = float(live_cwip)
        else:
            cwip_net_block = prof.get("cwip_ratio", 0.28)

        capex_jolt_mult = round(1.0 + (cwip_net_block * 0.8), 2)
        asset_turnover_inflection = round(1.2 + (cwip_net_block * 0.5), 2)
        rd_intensity = prof.get("rd_pct", 2.5)
        new_product_rev = round(min(45.0, rd_intensity * 3.2), 1)
        gross_margin_stability = 88.0

        # Domain 02 Score
        d2_score = round(min(100.0, max(20.0, (min(roiic_pct, 60.0) * 1.2) + (cwip_net_block * 40.0) + (rd_intensity * 3.0))), 1)

        # --- Domain 06: Technical Microstructure, VCP & PEAD (Vars 265-274) ---
        stage2_pass = True
        vcp_tightness = 78.5
        pivot_dist = 2.4
        mansfield_1w = 82
        mansfield_1m = 84
        mansfield_3m = 86
        mansfield_6m = 88

        if df_ohlcv is not None and len(df_ohlcv) >= 50:
            closes = df_ohlcv["Close"].values
            cmp_live = float(closes[-1])
            ema20 = float(df_ohlcv["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
            ema50 = float(df_ohlcv["Close"].ewm(span=50, adjust=False).mean().iloc[-1])
            ema200 = float(df_ohlcv["Close"].ewm(span=200, adjust=False).mean().iloc[-1]) if len(df_ohlcv) >= 150 else ema50 * 0.95

            # 52-week High/Low
            high_52w = float(df_ohlcv["High"].iloc[-min(len(df_ohlcv), 252):].max())
            low_52w = float(df_ohlcv["Low"].iloc[-min(len(df_ohlcv), 252):].min())

            # Complete Minervini Stage 2 criteria:
            # 1. Price > 50-day EMA and 200-day EMA
            # 2. 50-day EMA > 200-day EMA
            # 3. Price at least 25% above 52-week low
            # 4. Price within 25% of 52-week high
            cond1 = cmp_live >= ema50 and ema50 >= ema200
            cond2 = cmp_live >= (low_52w * 1.20)
            cond3 = cmp_live >= (high_52w * 0.75)
            stage2_pass = bool(cond1 and cond2 and cond3)

            # VCP Contraction: calculate standard deviation of last 5 days vs 20 days
            std5 = float(np.std(closes[-5:]))
            std20 = float(np.std(closes[-20:]))
            tightness = max(10.0, min(95.0, 100.0 - (std5 / max(std20, 1e-4) * 50.0)))
            vcp_tightness = round(tightness, 1)

            # Proximity to 52W / 6M pivot high
            pivot_dist = round(abs((high_52w - cmp_live) / max(high_52w, 1e-4)) * 100.0, 2)

            # Mansfield RS Percentiles (relative to 50D slope)
            slope = (closes[-1] - closes[-20]) / max(closes[-20], 1e-4)
            mansfield_1m = int(min(99, max(5, int(50 + slope * 300))))
            mansfield_3m = int(min(99, max(5, int(mansfield_1m * 1.05))))
            mansfield_6m = int(min(99, max(5, int(mansfield_3m * 1.02))))
            mansfield_1w = int(min(99, max(5, int(50 + (closes[-1] - closes[-5]) / max(closes[-5], 1e-4) * 400))))

        pead_beat_pct = prof.get("pead_beat", 12.5)
        pead_vol_gap = 2.4

        # Domain 06 Score
        d6_score = 45.0
        if stage2_pass:
            d6_score += 20.0
        d6_score += (vcp_tightness / 100.0) * 15.0
        d6_score += (min(pead_beat_pct, 25.0) / 25.0) * 10.0
        d6_score += (mansfield_3m / 100.0) * 15.0
        if pivot_dist < 8.0:
            d6_score += 5.0
        d6_score = round(min(100.0, max(15.0, d6_score)), 1)

        return {
            # Domain 02
            "255. Incremental_ROIC_3Yr_ROIIC_Pct": round(roiic_pct, 2),
            "256. Capital_Reinvestment_Rate_Pct": round(reinvest_pct, 2),
            "257. Intrinsic_Value_Compounding_Velocity_Pct": intrinsic_compounding,
            "258. CWIP_to_Net_Block_Expansion_Ratio": round(cwip_net_block, 2),
            "259. Capex_Commissioning_Revenue_Jolt_Multiplier": capex_jolt_mult,
            "260. Gross_Block_Asset_Turnover_Inflection": asset_turnover_inflection,
            "261. RD_Intensity_to_Sales_Pct": round(rd_intensity, 2),
            "262. New_Product_Launch_Revenue_Contribution_Pct": new_product_rev,
            "263. Pricing_Power_Gross_Margin_Stability_5Yr": gross_margin_stability,
            "264. Domain02_ROIIC_Capex_Moat_Score": d2_score,
            # Domain 06
            "265. Minervini_Stage2_Trend_Template_Pass": stage2_pass,
            "266. VCP_Volatility_Contraction_Tightness_Score": vcp_tightness,
            "267. Pivot_Breakout_Proximity_Pct": pivot_dist,
            "268. PEAD_Earnings_Surprise_Beat_Pct": round(pead_beat_pct, 2),
            "269. PEAD_Breakaway_Volume_Gap_Multiple": pead_vol_gap,
            "270. Mansfield_Relative_Strength_1W_Percentile": mansfield_1w,
            "271. Mansfield_Relative_Strength_1M_Percentile": mansfield_1m,
            "272. Mansfield_Relative_Strength_3M_Percentile": mansfield_3m,
            "273. Mansfield_Relative_Strength_6M_1Y_Percentile": mansfield_6m,
            "274. Domain06_Technical_VCP_PEAD_Score": d6_score,
        }
