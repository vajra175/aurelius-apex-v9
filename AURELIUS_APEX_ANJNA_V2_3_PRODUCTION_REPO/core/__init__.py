"""
================================================================================
AURELIUS SOVEREIGN (AQ-OS v9.2) — CORE QUANTITATIVE & ANJNA™ v2.3 ENGINES
================================================================================
"""

from core.anjna_v2_3_engine import (
    ANJNAEngineV23,
    ANJNAMetaFactorEngine,
    ANJNAPointInTimeContract,
    ANJNAValidationProtocol,
    sanitize_ohlcv_corporate_actions,
    norm_cdf,
    norm_ppf,
)

__version__ = "9.2.0-ANJNA-v2.3"
__author__ = "Aurelius Quantitative Systems"

__all__ = [
    "ANJNAEngineV23",
    "ANJNAMetaFactorEngine",
    "ANJNAPointInTimeContract",
    "ANJNAValidationProtocol",
    "sanitize_ohlcv_corporate_actions",
    "norm_cdf",
    "norm_ppf",
]
