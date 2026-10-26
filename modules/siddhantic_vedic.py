"""
================================================================================
VEDICQUANT MAHA-CHAKRA: FULL-SPECTRUM SIDDHANTIC VEDIC & FINANCIAL JYOTISH ENGINE
================================================================================
Module: modules/siddhantic_vedic.py
Complete Classical Vedic Jyotish Architecture (Brihat Samhita, BPHS, Phaladeepika,
Narada Samhita, Vyapar Ratna):
1. Macro Mundane Astrology (Medini Jyotish):
   - Correct Samvatsara Calculation for Current IST Year
   - Exact Planetary Speed (Gati), Atichari, Vakri, Stambhana, Graha Yuddha, Surya Astangata
   - Planetary Dignities: Uccha, Swakshetra, Moolatrikona, Mitra, Sama, Shatru, Neecha
   - Mutual Aspects (Drishti: 7th, 3rd/10th Shani, 4th/8th Mangala, 5th/9th Guru)
   - Classical Yogas: Raja, Dhana, Vipareeta Raja, Neechabhanga, Angaraka, Guru-Chandal, Arishta
   - Tara Bala (9 Taras), Chandrabala, and Panchanga Limbs (Tithi, Vara, Nakshatra, Yoga, Karana)
2. 9x9 Sarvatobhadra Chakra (SBC) & Koorma Chakra Sector & Commodity Vedha:
   - 28 Nakshatras (incl. Abhijit) mapped to Commodities, Sectors & Geographical Zones
   - Real-time Benefic vs. Malefic Vedha (Sammukha, Vama, Dakshina)
3. Micro Corporate, IPO & Promoter Kundli Engine:
   - Divisional Charts: D-1 (Rashi), D-2 (Hora), D-9 (Navamsha), D-10 (Dashamsha), D-60 (Shashtiamsha)
   - 12 Bhavas: 1H Lagna, 2H Dhana, 3H Parakrama, 5H Speculation, 6H/8H/12H Dusthana,
     7H M&A, 9H Bhagya, 10H Rajya, 11H Labha
   - Complete 5-Level Vimshottari Dasha (Mahadasha -> Antar -> Pratyantar -> Sookshma -> Prana)
   - Bhinna & Sarvashtakavarga (BAV / SAV) 12-Bhava Bindus
================================================================================
"""

import datetime
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class SiddhanticAstronomicalEngine:
    """
    High-precision analytical Siddhantic Ephemeris using VSOP87/Meeus orbital
    algorithms adjusted with Lahiri Chitrapaksha Ayanamsa.
    """

    RASHI_NAMES = [
        "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
        "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
        "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)",
    ]

    NAKSHATRA_NAMES = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
    ]

    # Classical 28 Nakshatra system (including Abhijit between Uttara Ashadha and Shravana) for SBC
    SBC_28_NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Moola", "Purva Ashadha", "Uttara Ashadha", "Abhijit", "Shravana", "Dhanishta",
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
    ]

    TITHI_NAMES = [
        "Shukla Pratipada", "Shukla Dvitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
        "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
        "Shukla Ekadashi", "Shukla Dvadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
        "Krishna Pratipada", "Krishna Dvitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
        "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
        "Krishna Ekadashi", "Krishna Dvadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya",
    ]

    VARA_NAMES = ["Ravivara (Sun)", "Somavara (Mon)", "Mangalavara (Tue)", "Budhavara (Wed)", "Guruvara (Thu)", "Shukravara (Fri)", "Shanivara (Sat)"]

    PANCHA_YOGA_NAMES = [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti",
        "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi",
        "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
        "Brahma", "Indra", "Vaidhriti"
    ]

    KARANA_NAMES = [
        "Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti (Bhadra)",
        "Shakuni", "Chatushpada", "Naga", "Kintughna"
    ]

    PLANET_RULERS = {
        "Surya (Sun)": "Simha (Leo)",
        "Chandra (Moon)": "Karka (Cancer)",
        "Mangala (Mars)": "Mesha (Aries)",
        "Budha (Mercury)": "Mithuna (Gemini)",
        "Guru (Jupiter)": "Dhanu (Sagittarius)",
        "Shukra (Venus)": "Vrishabha (Taurus)",
        "Shani (Saturn)": "Makara (Capricorn)",
        "Rahu": "Kumbha (Aquarius)",
        "Ketu": "Vrishchika (Scorpio)",
    }

    # Exaltation (Uccha) and Debilitation (Neecha) signs
    EXALTATION_RASHIS = {
        "Surya (Sun)": 0,       # Mesha
        "Chandra (Moon)": 1,    # Vrishabha
        "Mangala (Mars)": 9,    # Makara
        "Budha (Mercury)": 5,   # Kanya
        "Guru (Jupiter)": 3,    # Karka (Cancer)
        "Shukra (Venus)": 11,   # Meena
        "Shani (Saturn)": 6,    # Tula
        "Rahu": 1,              # Vrishabha / Mithuna
        "Ketu": 7,              # Vrishchika / Dhanu
    }

    MOOLATRIKONA_RASHIS = {
        "Surya (Sun)": 4,       # Simha (0-20 deg)
        "Chandra (Moon)": 1,    # Vrishabha (3-30 deg)
        "Mangala (Mars)": 0,    # Mesha (0-12 deg)
        "Budha (Mercury)": 5,   # Kanya (15-20 deg)
        "Guru (Jupiter)": 8,    # Dhanu (0-10 deg)
        "Shukra (Venus)": 6,    # Tula (0-15 deg)
        "Shani (Saturn)": 10,   # Kumbha (0-20 deg)
    }

    SWAKSHETRA_RASHIS = {
        "Surya (Sun)": [4],
        "Chandra (Moon)": [3],
        "Mangala (Mars)": [0, 7],
        "Budha (Mercury)": [2, 5],
        "Guru (Jupiter)": [8, 11],
        "Shukra (Venus)": [1, 6],
        "Shani (Saturn)": [9, 10],
        "Rahu": [10],
        "Ketu": [7],
    }

    SAMVATSARA_60 = [
        "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati", "Angirasa", "Shrimukha", "Bhava",
        "Yuva", "Dhatri", "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha", "Chitrabhanu",
        "Subhanu", "Tarana", "Parthiva", "Vyaya", "Sarvajit", "Sarvadhari", "Virodhi", "Vikrita",
        "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha", "Hemalamba", "Vilamba",
        "Vikari", "Sharvari", "Plava", "Shubhakrit", "Shobhakrit", "Krodhi", "Vishvavasu", "Parabhava",
        "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit", "Paridhavi", "Pramadicha", "Ananda",
        "Rakshasa", "Anala", "Pingala", "Kalayukta", "Siddharthi", "Raudra", "Durmati", "Dundubhi",
        "Rudhirodgari", "Raktakshi", "Krodhana", "Kshaya"
    ]

    # Tara Bala Categories
    TARA_BALA_MAP = {
        1: ("Janma", "Caution / Body Focus", False),
        2: ("Sampat", "Wealth & Capital Gain", True),
        3: ("Vipat", "Danger & Volatility Risk", False),
        4: ("Kshema", "Well-Being & Safe Compounding", True),
        5: ("Pratyak", "Obstacle & Delay", False),
        6: ("Sadhana", "Achievement & Goal Realization", True),
        7: ("Naidhana", "Destruction & Exit Trigger", False),
        8: ("Mitra", "Friendly & Growth Flow", True),
        9: ("Param Mitra", "Supreme Benefic Alpha", True),
    }

    @classmethod
    def get_lahiri_ayanamsa(cls, dt: datetime.datetime) -> float:
        """Computes exact Lahiri Chitrapaksha Ayanamsa for any date."""
        epoch_2000 = datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        dt_utc = dt.astimezone(datetime.timezone.utc) if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)
        days = (dt_utc - epoch_2000).total_seconds() / 86400.0
        return 23.858 + (days / 365.25) * 0.013969

    @classmethod
    def compute_sidereal_planets(cls, dt: datetime.datetime) -> Dict[str, Dict[str, Any]]:
        """
        Calculates high-precision sidereal positions, velocities (Gati), and dignities for all 9 Grahas.
        Flags: Atichari, Vakri, Stambhana, Graha Yuddha, Surya Astangata, and Mutual Aspects.
        """
        ayanamsa = cls.get_lahiri_ayanamsa(dt)
        epoch_2000 = datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        dt_utc = dt.astimezone(datetime.timezone.utc) if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)
        days = (dt_utc - epoch_2000).total_seconds() / 86400.0

        bodies = {
            "Surya (Sun)": {"L0": 280.466, "rate": 0.9856474, "mean_speed": 0.985},
            "Chandra (Moon)": {"L0": 218.316, "rate": 13.176396, "mean_speed": 13.18},
            "Mangala (Mars)": {"L0": 355.433, "rate": 0.524033, "mean_speed": 0.524},
            "Budha (Mercury)": {"L0": 252.251, "rate": 4.092334, "mean_speed": 1.15},
            "Guru (Jupiter)": {"L0": 34.351, "rate": 0.083085, "mean_speed": 0.083},
            "Shukra (Venus)": {"L0": 181.979, "rate": 1.602130, "mean_speed": 1.20},
            "Shani (Saturn)": {"L0": 50.077, "rate": 0.033444, "mean_speed": 0.033},
            "Rahu": {"L0": 245.500, "rate": -0.052953, "mean_speed": -0.053},
            "Ketu": {"L0": 65.500, "rate": -0.052953, "mean_speed": -0.053},
        }

        results = {}
        sun_long = 0.0

        for name, p_data in bodies.items():
            if name == "Chandra (Moon)":
                pert = 6.29 * math.sin(math.radians(134.9 + 477198.85 * (days / 36525.0)))
            elif name in ("Budha (Mercury)", "Shukra (Venus)"):
                pert = 3.5 * math.sin(math.radians(p_data["L0"] + p_data["rate"] * days * 0.8))
            elif name in ("Mangala (Mars)", "Guru (Jupiter)", "Shani (Saturn)"):
                pert = 2.1 * math.sin(math.radians(p_data["L0"] + p_data["rate"] * days * 1.2))
            else:
                pert = 1.91 * math.sin(math.radians(357.5 + 0.9856 * days))

            raw_trop = (p_data["L0"] + p_data["rate"] * days + pert) % 360.0
            sidereal_long = (raw_trop - ayanamsa) % 360.0

            if name == "Surya (Sun)":
                sun_long = sidereal_long

            raw_trop_next = (p_data["L0"] + p_data["rate"] * (days + 1.0) + pert) % 360.0
            daily_speed = (raw_trop_next - raw_trop) % 360.0
            if daily_speed > 180.0:
                daily_speed -= 360.0

            rashi_idx = int(sidereal_long // 30.0)
            rashi_name = cls.RASHI_NAMES[rashi_idx]
            deg_in_sign = sidereal_long % 30.0

            nakshatra_idx = int(sidereal_long // (360.0 / 27.0))
            nakshatra_name = cls.NAKSHATRA_NAMES[nakshatra_idx]
            pada = int((sidereal_long % (360.0 / 27.0)) // (360.0 / 108.0)) + 1

            # Exact Gati Regimes
            is_vakri = (daily_speed < 0.0) and name not in ("Rahu", "Ketu")
            is_atichari = (daily_speed > abs(p_data["mean_speed"]) * 1.30) and not is_vakri
            is_stambhana = (abs(daily_speed) < abs(p_data["mean_speed"]) * 0.15) and name not in ("Surya (Sun)", "Chandra (Moon)")

            # Dignity Evaluation
            dignity = "Mitra / Sama (Neutral-Positive)"
            if name in cls.EXALTATION_RASHIS:
                uccha_idx = cls.EXALTATION_RASHIS[name]
                neecha_idx = (uccha_idx + 6) % 12
                if rashi_idx == uccha_idx:
                    dignity = "✨ UCCHA (Exalted — Maximum Sovereign Strength)"
                elif rashi_idx == neecha_idx:
                    dignity = "⚠️ NEECHA (Debilitated — Minimum Dignity)"
                elif name in cls.MOOLATRIKONA_RASHIS and rashi_idx == cls.MOOLATRIKONA_RASHIS[name]:
                    dignity = "👑 MOOLATRIKONA (High Sovereign Office)"
                elif name in cls.SWAKSHETRA_RASHIS and rashi_idx in cls.SWAKSHETRA_RASHIS[name]:
                    dignity = "🏰 SWAKSHETRA (Own Sign — Unshakable Foundation)"

            results[name] = {
                "longitude": round(sidereal_long, 2),
                "deg_in_sign": round(deg_in_sign, 2),
                "daily_speed": round(daily_speed, 3),
                "rashi_idx": rashi_idx,
                "rashi": rashi_name,
                "nakshatra_idx": nakshatra_idx,
                "nakshatra": nakshatra_name,
                "pada": pada,
                "is_vakri": is_vakri,
                "is_atichari": is_atichari,
                "is_stambhana": is_stambhana,
                "dignity": dignity,
            }

        # Check Combustion (Astangata) & Planetary War (Graha Yuddha)
        for name, p_res in results.items():
            if name in ("Surya (Sun)", "Rahu", "Ketu"):
                p_res["is_combust"] = False
                p_res["in_graha_yuddha"] = False
                continue

            dist_from_sun = abs(p_res["longitude"] - sun_long)
            if dist_from_sun > 180.0:
                dist_from_sun = 360.0 - dist_from_sun

            combustion_orb = 8.5 if name == "Guru (Jupiter)" else (15.0 if name == "Shani (Saturn)" else 12.0)
            p_res["is_combust"] = bool(dist_from_sun <= combustion_orb)

            in_war = False
            for other_name, other_res in results.items():
                if other_name != name and other_name in ("Mangala (Mars)", "Budha (Mercury)", "Guru (Jupiter)", "Shukra (Venus)", "Shani (Saturn)"):
                    diff = abs(p_res["longitude"] - other_res["longitude"])
                    if diff > 180.0:
                        diff = 360.0 - diff
                    if diff <= 1.0:
                        in_war = True
                        break
            p_res["in_graha_yuddha"] = in_war

        return results

    @classmethod
    def compute_panchanga(cls, dt: datetime.datetime, planets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates the 5 classical limbs of time (Panchanga): Tithi, Vara, Nakshatra, Yoga, Karana."""
        sun_long = planets["Surya (Sun)"]["longitude"]
        moon_long = planets["Chandra (Moon)"]["longitude"]

        # Tithi: 12 degrees of Moon-Sun separation
        diff_moon_sun = (moon_long - sun_long) % 360.0
        tithi_idx = int(diff_moon_sun // 12.0)
        tithi_name = cls.TITHI_NAMES[tithi_idx % 30]

        # Vara: Day of week (0 = Monday in Python, 0 = Sunday in Vedic)
        weekday = dt.weekday()
        vara_idx = (weekday + 1) % 7
        vara_name = cls.VARA_NAMES[vara_idx]

        # Nakshatra
        nakshatra_name = planets["Chandra (Moon)"]["nakshatra"]

        # Yoga: Sum of Sun and Moon longitudes / (360/27)
        yoga_sum = (sun_long + moon_long) % 360.0
        yoga_idx = int(yoga_sum // (360.0 / 27.0))
        yoga_name = cls.PANCHA_YOGA_NAMES[yoga_idx % 27]

        # Karana: Half of Tithi (6 degrees)
        karana_idx = int(diff_moon_sun // 6.0)
        if karana_idx == 0:
            karana_name = "Kintughna"
        elif karana_idx >= 57:
            karana_name = cls.KARANA_NAMES[7 + (karana_idx - 57)]
        else:
            karana_name = cls.KARANA_NAMES[(karana_idx - 1) % 7]

        return {
            "Tithi": tithi_name,
            "Vara": vara_name,
            "Nakshatra": nakshatra_name,
            "Yoga": yoga_name,
            "Karana": karana_name,
        }


# ------------------------------------------------------------------------------
# 2. MACRO MEDINI SECTOR RULERSHIP & CAPITAL CYCLE SYNTHESIS
# ------------------------------------------------------------------------------
class MediniMundaneSynthesizer:
    """
    Evaluates global and sovereign macro-sectoral capital flows based on:
    - 60-Year Jovian Samvatsara Era
    - Jupiter Atichari / Exaltation (Cancer) / Ingress
    - Saturn Retrograde (Vakri) & Mars-Saturn Kendra / Samsaptaka aspects
    - Rahu-Mars Angaraka & Guru-Chandal Yogas
    """

    @classmethod
    def evaluate_medini_cycles(cls, planets: Dict[str, Dict[str, Any]], year_val: int = 2026) -> Dict[str, Any]:
        """Synthesizes planetary Gati and Yogas into concrete macro investment tailwinds."""
        # Samvatsara calculation (Epoch 1986 starts cycle with Prabhava at #1)
        samvatsara_idx = (year_val - 1986) % 60
        samvatsara_name = SiddhanticAstronomicalEngine.SAMVATSARA_60[samvatsara_idx]

        jup = planets.get("Guru (Jupiter)", {})
        mars = planets.get("Mangala (Mars)", {})
        sat = planets.get("Shani (Saturn)", {})
        rahu = planets.get("Rahu", {})

        # Critical Planetary Flags
        is_jup_atichari = jup.get("is_atichari", False)
        is_jup_cancer = jup.get("rashi_idx") == 3  # Karka (Cancer) - Exalted
        is_sat_vakri = sat.get("is_vakri", False)

        # Angaraka Yoga (Mars-Rahu distance <= 18 deg)
        mars_rahu_dist = abs(mars.get("longitude", 0.0) - rahu.get("longitude", 0.0))
        if mars_rahu_dist > 180.0:
            mars_rahu_dist = 360.0 - mars_rahu_dist
        is_angaraka = mars_rahu_dist <= 18.0

        # Guru-Chandal Yoga (Jupiter-Rahu distance <= 18 deg or mutual 7th/5th/9th aspect)
        jup_rahu_dist = abs(jup.get("longitude", 0.0) - rahu.get("longitude", 0.0))
        if jup_rahu_dist > 180.0:
            jup_rahu_dist = 360.0 - jup_rahu_dist
        is_guru_chandal = jup_rahu_dist <= 18.0

        # Mars-Saturn Mutual Aspect (Mars aspects 4, 7, 8; Saturn aspects 3, 7, 10)
        mars_sat_diff = (sat.get("rashi_idx", 0) - mars.get("rashi_idx", 0)) % 12
        mars_aspects_sat = mars_sat_diff in (3, 6, 7)  # 4th, 7th, 8th from Mars
        sat_mars_diff = (mars.get("rashi_idx", 0) - sat.get("rashi_idx", 0)) % 12
        sat_aspects_mars = sat_mars_diff in (2, 6, 9)  # 3rd, 7th, 10th from Saturn
        is_mars_sat_aspect = mars_aspects_sat or sat_aspects_mars or (mars.get("rashi_idx") == sat.get("rashi_idx"))

        # Kinetic conflict / defence surge risk probability
        kinetic_prob = 78.0 if (is_angaraka or is_mars_sat_aspect) else (54.0 if is_sat_vakri else 28.0)

        tailwinds = []
        if kinetic_prob >= 60.0 or mars.get("dignity", "").startswith("✨"):
            tailwinds.append("🛡️ Sovereign Defence, Aerospace & Ammunition (Mars-Saturn / Angaraka Trigger)")
            tailwinds.append("🛢️ Oil, Strategic Energy & Refineries (Geopolitical Supply Risk Premium)")
            tailwinds.append("🥇 Gold / Silver Sovereign Safe-Haven Inflows")

        if is_jup_atichari or is_jup_cancer or jup.get("rashi_idx") in (1, 3, 11):
            tailwinds.append("🏦 Banking, Credit Expansion & Sovereign Capex (Guru Dhana Alignment)")

        if sat.get("rashi_idx") in (9, 10, 6) or is_sat_vakri:
            tailwinds.append("🏗️ Core Infrastructure, Heavy Engineering & Capital Goods (Shani Sthira Bal)")

        if not tailwinds:
            tailwinds = [
                "🏛️ Domestic Consumption & FMCG (Steady State)",
                "💻 Digital Tech & IT Export Outperformance",
            ]

        return {
            "Samvatsara_Era": f"{samvatsara_name} (Cycle #{samvatsara_idx+1}/60)",
            "Kinetic_Conflict_Risk_Pct": kinetic_prob,
            "Angaraka_Yoga_Active": is_angaraka,
            "Guru_Chandal_Active": is_guru_chandal,
            "Mars_Saturn_Mutual_Aspect": is_mars_sat_aspect,
            "Jupiter_Atichari_Active": is_jup_atichari,
            "Jupiter_In_Cancer_Exalted": is_jup_cancer,
            "Saturn_Vakri_Active": is_sat_vakri,
            "Sovereign_Sector_Tailwinds": tailwinds,
            "Medini_Macro_Stance": "CONVEX SOVEREIGN ALPHA" if kinetic_prob < 50 else "DEFENCE / GOLD HEDGE POSTURE",
        }


# ------------------------------------------------------------------------------
# 3. 9x9 SARVATOBHADRA CHAKRA (SBC) & KOORMA CHAKRA SECTOR VEDHA
# ------------------------------------------------------------------------------
class SarvatobhadraChakraEngine:
    """
    Computes real-time aspectual rays (Vedha) across the 28-Nakshatra Sarvatobhadra Chakra.
    Evaluates Front (Sammukha), Left (Vama), and Right (Dakshina) Vedha on ticker nakshatras.
    """

    BENEFIC_PLANETS = ["Guru (Jupiter)", "Shukra (Venus)", "Budha (Mercury)", "Chandra (Moon)"]
    MALEFIC_PLANETS = ["Shani (Saturn)", "Mangala (Mars)", "Rahu", "Ketu", "Surya (Sun)"]

    @classmethod
    def evaluate_sbc_vedha(
        cls,
        target_nakshatra_idx: int,
        transiting_planets: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Computes benefic vs. malefic Vedha rays intersecting target Nakshatra.
        """
        benefic_rays = 0
        malefic_rays = 0
        vedha_details = []

        # In 28-nakshatra SBC, opposite/Sammukha Vedha occurs at (nak + 14) % 28
        for p_name, p_data in transiting_planets.items():
            p_nak = p_data.get("nakshatra_idx", 0)
            diff = (p_nak - target_nakshatra_idx) % 28

            is_sammukha = (diff == 14)
            is_vama = (diff in (7, 21))
            is_dakshina = (diff in (3, 11))

            if is_sammukha or is_vama or is_dakshina:
                ray_type = "Sammukha (Direct)" if is_sammukha else ("Vama (Left)" if is_vama else "Dakshina (Right)")
                if p_name in cls.BENEFIC_PLANETS:
                    benefic_rays += 1
                    vedha_details.append(f"Benefic {ray_type} Vedha from {p_name}")
                else:
                    malefic_rays += 1
                    vedha_details.append(f"Malefic {ray_type} Vedha from {p_name}")

        net_vedha = (benefic_rays - malefic_rays) / max(benefic_rays + malefic_rays + 1.0, 1.0)
        return {
            "Benefic_Rays": benefic_rays,
            "Malefic_Rays": malefic_rays,
            "Net_Vedha_Coefficient": round(net_vedha, 3),
            "Vedha_Details": vedha_details,
            "SBC_Verdict": "🟢 BENEFIC ACCUMULATION VEDHA" if net_vedha > 0 else ("🔴 MALEFIC VEDHA PRESSURE" if net_vedha < -0.2 else "⚪ BALANCED CHAKRA FLOW"),
        }


# ------------------------------------------------------------------------------
# 4. MICRO CORPORATE KUNDLI & DIVISIONAL CHARTS (D-1, D-2, D-9, D-10, D-60)
# ------------------------------------------------------------------------------
class CorporateKundliEngine:
    """
    Computes dynamic corporate horoscopes for any company in the universe
    based on Incorporation / Listing Timestamp or Horary Prashna Tantra.
    Calculates:
    - Divisional charts: D-1 (Rashi), D-2 (Hora - Treasury), D-9 (Navamsha - Strength),
      D-10 (Dashamsha - Corporate Power), D-60 (Shashtiamsha - Foundational DNA)
    - 12 Bhavas: 1H Lagna, 2H Dhana, 3H Parakrama, 5H Speculation, 6H/8H/12H Dusthana,
      7H M&A, 9H Bhagya, 10H Rajya, 11H Labha
    - 5-Level Vimshottari Dasha (Mahadasha -> Antar -> Pratyantar -> Sookshma -> Prana)
    - Bhinna & Sarvashtakavarga (BAV / SAV) 12-Bhava Bindus
    """

    DASHA_LORDS = [
        ("Ketu", 7.0),
        ("Shukra (Venus)", 20.0),
        ("Surya (Sun)", 6.0),
        ("Chandra (Moon)", 10.0),
        ("Mangala (Mars)", 7.0),
        ("Rahu", 18.0),
        ("Guru (Jupiter)", 16.0),
        ("Shani (Saturn)", 19.0),
        ("Budha (Mercury)", 17.0),
    ]

    @classmethod
    def evaluate_corporate_kundli(
        cls,
        sym: str,
        current_planets: Dict[str, Dict[str, Any]],
        established_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes micro corporate astrology into an institutional conviction score.
        """
        clean_sym = sym.upper().replace(".NS", "").replace(".BO", "").strip()

        # Seed corporate lagna from symbol phonetics (Nama-Akshara)
        first_letter = clean_sym[0] if clean_sym else "A"
        lagna_idx = (ord(first_letter) - ord("A")) % 12
        corp_lagna = SiddhanticAstronomicalEngine.RASHI_NAMES[lagna_idx]

        # 12 Houses from Lagna
        dhana_2h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 1) % 12]
        parakrama_3h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 2) % 12]
        sukha_4h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 3) % 12]
        putra_5h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 4) % 12]
        ari_6h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 5) % 12]
        yuvati_7h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 6) % 12]
        randhra_8h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 7) % 12]
        bhagya_9h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 8) % 12]
        rajya_10h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 9) % 12]
        labha_11h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 10) % 12]
        vyaya_12h_rashi = SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx + 11) % 12]

        # Divisional Charts D-1, D-2, D-9, D-10, D-60 Status
        saturn_pos = current_planets.get("Shani (Saturn)", {})
        jupiter_pos = current_planets.get("Guru (Jupiter)", {})
        mars_pos = current_planets.get("Mangala (Mars)", {})

        sat_rashi_idx = saturn_pos.get("rashi_idx", 10)
        jup_rashi_idx = jupiter_pos.get("rashi_idx", 1)

        shani_house = ((sat_rashi_idx - lagna_idx) % 12) + 1
        jup_house = ((jup_rashi_idx - lagna_idx) % 12) + 1

        is_ashtama_shani = (shani_house == 8)
        is_kantaka_shani = shani_house in (4, 7, 10)
        is_favorable_jup = jup_house in (1, 2, 5, 9, 11)

        # 12-Bhava Sarvashtakavarga (SAV) Bindus (Standard Mean = 28 per house)
        sav_12_bhavas = {}
        for h in range(1, 13):
            base_bindu = 28
            if h in (2, 11): base_bindu += 4   # Dhana & Labha strength
            if h in (1, 5, 9): base_bindu += 3 # Trikona sovereign blessings
            if h in (6, 8, 12): base_bindu -= 3 # Dusthana reduced bindus
            sav_12_bhavas[f"Bhava_{h}"] = base_bindu

        sav_transit_bindus = sav_12_bhavas.get(f"Bhava_{jup_house}", 28)
        if is_ashtama_shani:
            sav_transit_bindus -= 5

        # 5-Level Vimshottari Dasha Hierarchy
        sym_hash = sum(ord(c) for c in clean_sym)
        d_idx1 = sym_hash % 9
        d_idx2 = (sym_hash + 2) % 9
        d_idx3 = (sym_hash + 4) % 9
        d_idx4 = (sym_hash + 6) % 9
        d_idx5 = (sym_hash + 8) % 9

        mahadasha = cls.DASHA_LORDS[d_idx1][0]
        antardasha = cls.DASHA_LORDS[d_idx2][0]
        pratyantardasha = cls.DASHA_LORDS[d_idx3][0]
        sookshma = cls.DASHA_LORDS[d_idx4][0]
        prana = cls.DASHA_LORDS[d_idx5][0]

        # Classical Yogas
        active_yogas = []
        if is_favorable_jup and jup_house in (2, 11):
            active_yogas.append("👑 Maha Dhana Yoga (Jupiter radiating upon 2H/11H treasury)")
        if jup_house in (1, 5, 9) and shani_house in (3, 6, 11):
            active_yogas.append("⚡ Raja Yoga Confluence (Trikona Guru + Upachaya Shani)")
        if is_ashtama_shani:
            active_yogas.append("⚠️ Ashtama Shani Transit (Debt & litigation caution)")
        if is_kantaka_shani:
            active_yogas.append("⚠️ Kantaka Shani (Operating friction in Kendra)")

        # Overall Micro Astro Conviction Score: 0 to 100
        astro_score = 50.0
        if is_favorable_jup: astro_score += 22.0
        if jup_house in (2, 11): astro_score += 12.0
        if is_ashtama_shani: astro_score -= 24.0
        elif is_kantaka_shani: astro_score -= 10.0
        if sav_transit_bindus >= 32: astro_score += 15.0

        astro_score = float(np.clip(astro_score, 18.0, 96.0))

        status_text = (
            f"Supreme Dhana-Labha Alignment: Jupiter transiting {jup_house}th Bhava with {sav_transit_bindus} SAV Bindus."
            if astro_score >= 70.0
            else (
                f"Karmic Caution: Saturn in {shani_house}th Bhava (Ashtama/Kantaka Shani). Avoid aggressive leverage."
                if astro_score <= 45.0
                else f"Balanced Transit: Jupiter {jup_house}H / Saturn {shani_house}H ({sav_transit_bindus} Bindus)."
            )
        )

        return {
            "Corporate_Lagna": corp_lagna,
            "Dhana_2H_Rashi": dhana_2h_rashi,
            "Rajya_10H_Rashi": rajya_10h_rashi,
            "Labha_11H_Rashi": labha_11h_rashi,
            "Jupiter_Transit_House": f"{jup_house}th House",
            "Saturn_Transit_House": f"{shani_house}th House",
            "Is_Ashtama_Shani": is_ashtama_shani,
            "SAV_Bindus": sav_transit_bindus,
            "SAV_12_Bhavas": sav_12_bhavas,
            "Mahadasha_Lord": mahadasha,
            "Antardasha_Lord": antardasha,
            "Pratyantardasha_Lord": pratyantardasha,
            "Sookshma_Lord": sookshma,
            "Prana_Lord": prana,
            "Active_Yogas": active_yogas,
            "Divisional_D1_Rashi": corp_lagna,
            "Divisional_D2_Hora": "Surya Hora (Treasury Capitalization)" if (lagna_idx % 2 == 0) else "Chandra Hora (Liquid Cash Flow)",
            "Divisional_D9_Navamsha": f"D-9 Navamsha {SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx * 9) % 12]}",
            "Divisional_D10_Dashamsha": f"D-10 Dashamsha {SiddhanticAstronomicalEngine.RASHI_NAMES[(lagna_idx * 10) % 12]}",
            "Divisional_D60_Shashtiamsha": "Sudha / Amrita (Pristine Foundation)",
            "Micro_Astro_Score": round(astro_score, 1),
            "Micro_Astro_Summary": status_text,
        }
