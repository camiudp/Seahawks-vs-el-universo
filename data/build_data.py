#!/usr/bin/env python3
"""
Build the dataset for the 'Seahawks vs el Universo' spurious-correlations site.

Seahawks game logs: transcribed from Wikipedia season articles
  (en.wikipedia.org/wiki/2021..2025_Seattle_Seahawks_season), verified against
  each season's final W-L record in the infobox.

External series:
  - snow: NH monthly snow cover extent (km^2) - Rutgers Global Snow Lab
          (climate.rutgers.edu/snowcover/files/moncov.nhland.txt)
  - btc:  Bitcoin price in USD, first-of-month - officialdata.org/bitcoin-price
  - launches: global rocket launches that month (all types) - The Space Devs
          Launch Library 2 API (ll.thespacedevs.com), count field per month
  - moon: % of the Moon illuminated on the exact game date, computed locally
          via a standard synodic-month approximation (no API needed)
"""
import json
import math
from datetime import date

# ---------------------------------------------------------------------------
# 1. Seahawks game logs, 2021-2025 regular seasons
# fields: season, week, date(ISO), opponent, home(bool), result(W/L), pf, pa
# ---------------------------------------------------------------------------
GAMES_RAW = [
    # season, week, date, opponent, home, result, pf, pa
    (2021, 1, "2021-09-12", "at Indianapolis Colts", False, "W", 28, 16),
    (2021, 2, "2021-09-19", "Tennessee Titans", True, "L", 30, 33),
    (2021, 3, "2021-09-26", "at Minnesota Vikings", False, "L", 17, 30),
    (2021, 4, "2021-10-03", "at San Francisco 49ers", False, "W", 28, 21),
    (2021, 5, "2021-10-07", "Los Angeles Rams", True, "L", 17, 26),
    (2021, 6, "2021-10-17", "at Pittsburgh Steelers", False, "L", 20, 23),
    (2021, 7, "2021-10-25", "New Orleans Saints", True, "L", 10, 13),
    (2021, 8, "2021-10-31", "Jacksonville Jaguars", True, "W", 31, 7),
    (2021, 10, "2021-11-14", "at Green Bay Packers", False, "L", 0, 17),
    (2021, 11, "2021-11-21", "Arizona Cardinals", True, "L", 13, 23),
    (2021, 12, "2021-11-29", "at Washington Football Team", False, "L", 15, 17),
    (2021, 13, "2021-12-05", "San Francisco 49ers", True, "W", 30, 23),
    (2021, 14, "2021-12-12", "at Houston Texans", False, "W", 33, 13),
    (2021, 15, "2021-12-21", "at Los Angeles Rams", False, "L", 10, 20),
    (2021, 16, "2021-12-26", "Chicago Bears", True, "L", 24, 25),
    (2021, 17, "2022-01-02", "Detroit Lions", True, "W", 51, 29),
    (2021, 18, "2022-01-09", "at Arizona Cardinals", False, "W", 38, 30),

    (2022, 1, "2022-09-12", "Denver Broncos", True, "W", 17, 16),
    (2022, 2, "2022-09-18", "at San Francisco 49ers", False, "L", 7, 27),
    (2022, 3, "2022-09-25", "Atlanta Falcons", True, "L", 23, 27),
    (2022, 4, "2022-10-02", "at Detroit Lions", False, "W", 48, 45),
    (2022, 5, "2022-10-09", "at New Orleans Saints", False, "L", 32, 39),
    (2022, 6, "2022-10-16", "Arizona Cardinals", True, "W", 19, 9),
    (2022, 7, "2022-10-23", "at Los Angeles Chargers", False, "W", 37, 23),
    (2022, 8, "2022-10-30", "New York Giants", True, "W", 27, 13),
    (2022, 9, "2022-11-06", "at Arizona Cardinals", False, "W", 31, 21),
    (2022, 10, "2022-11-13", "at Tampa Bay Buccaneers", False, "L", 16, 21),
    (2022, 12, "2022-11-27", "Las Vegas Raiders", True, "L", 34, 40),
    (2022, 13, "2022-12-04", "at Los Angeles Rams", False, "W", 27, 23),
    (2022, 14, "2022-12-11", "Carolina Panthers", True, "L", 24, 30),
    (2022, 15, "2022-12-15", "San Francisco 49ers", True, "L", 13, 21),
    (2022, 16, "2022-12-24", "at Kansas City Chiefs", False, "L", 10, 24),
    (2022, 17, "2023-01-01", "New York Jets", True, "W", 23, 6),
    (2022, 18, "2023-01-08", "Los Angeles Rams", True, "W", 19, 16),

    (2023, 1, "2023-09-10", "Los Angeles Rams", True, "L", 13, 30),
    (2023, 2, "2023-09-17", "Detroit Lions", True, "W", 37, 31),
    (2023, 3, "2023-09-24", "Carolina Panthers", True, "W", 37, 27),
    (2023, 4, "2023-10-02", "New York Giants", True, "W", 24, 3),
    (2023, 6, "2023-10-15", "Cincinnati Bengals", True, "L", 13, 17),
    (2023, 7, "2023-10-22", "Arizona Cardinals", True, "W", 20, 10),
    (2023, 8, "2023-10-29", "Cleveland Browns", True, "W", 24, 20),
    (2023, 9, "2023-11-05", "Baltimore Ravens", True, "L", 3, 37),
    (2023, 10, "2023-11-12", "Washington Commanders", True, "W", 29, 26),
    (2023, 11, "2023-11-19", "Los Angeles Rams", True, "L", 16, 17),
    (2023, 12, "2023-11-23", "San Francisco 49ers", True, "L", 13, 31),
    (2023, 13, "2023-11-30", "Dallas Cowboys", True, "L", 35, 41),
    (2023, 14, "2023-12-10", "San Francisco 49ers", True, "L", 16, 28),
    (2023, 15, "2023-12-18", "Philadelphia Eagles", True, "W", 20, 17),
    (2023, 16, "2023-12-24", "Tennessee Titans", True, "W", 20, 17),
    (2023, 17, "2023-12-31", "Pittsburgh Steelers", True, "L", 23, 30),
    (2023, 18, "2024-01-07", "Arizona Cardinals", True, "W", 21, 20),

    (2024, 1, "2024-09-08", "Denver Broncos", True, "W", 26, 20),
    (2024, 2, "2024-09-15", "at New England Patriots", False, "W", 23, 20),
    (2024, 3, "2024-09-22", "Miami Dolphins", True, "W", 24, 3),
    (2024, 4, "2024-09-30", "at Detroit Lions", False, "L", 29, 42),
    (2024, 5, "2024-10-06", "New York Giants", True, "L", 20, 29),
    (2024, 6, "2024-10-10", "San Francisco 49ers", True, "L", 24, 36),
    (2024, 7, "2024-10-20", "at Atlanta Falcons", False, "W", 34, 14),
    (2024, 8, "2024-10-27", "Buffalo Bills", True, "L", 10, 31),
    (2024, 9, "2024-11-03", "Los Angeles Rams", True, "L", 20, 26),
    (2024, 11, "2024-11-17", "at San Francisco 49ers", False, "W", 20, 17),
    (2024, 12, "2024-11-24", "Arizona Cardinals", True, "W", 16, 6),
    (2024, 13, "2024-12-01", "at New York Jets", False, "W", 26, 21),
    (2024, 14, "2024-12-08", "at Arizona Cardinals", False, "W", 30, 18),
    (2024, 15, "2024-12-15", "Green Bay Packers", True, "L", 13, 30),
    (2024, 16, "2024-12-22", "Minnesota Vikings", True, "L", 24, 27),
    (2024, 17, "2024-12-26", "at Chicago Bears", False, "W", 6, 3),
    (2024, 18, "2025-01-05", "at Los Angeles Rams", False, "W", 30, 25),

    (2025, 1, "2025-09-07", "San Francisco 49ers", True, "L", 13, 17),
    (2025, 2, "2025-09-14", "at Pittsburgh Steelers", False, "W", 31, 17),
    (2025, 3, "2025-09-21", "New Orleans Saints", True, "W", 44, 13),
    (2025, 4, "2025-09-25", "at Arizona Cardinals", False, "W", 23, 20),
    (2025, 5, "2025-10-05", "Tampa Bay Buccaneers", True, "L", 35, 38),
    (2025, 6, "2025-10-12", "at Jacksonville Jaguars", False, "W", 20, 12),
    (2025, 7, "2025-10-20", "Houston Texans", True, "W", 27, 19),
    (2025, 9, "2025-11-02", "at Washington Commanders", False, "W", 38, 14),
    (2025, 10, "2025-11-09", "Arizona Cardinals", True, "W", 44, 22),
    (2025, 11, "2025-11-16", "at Los Angeles Rams", False, "L", 19, 21),
    (2025, 12, "2025-11-23", "at Tennessee Titans", False, "W", 30, 24),
    (2025, 13, "2025-11-30", "Minnesota Vikings", True, "W", 26, 0),
    (2025, 14, "2025-12-07", "at Atlanta Falcons", False, "W", 37, 9),
    (2025, 15, "2025-12-14", "Indianapolis Colts", True, "W", 18, 16),
    (2025, 16, "2025-12-18", "Los Angeles Rams", True, "W", 38, 37),
    (2025, 17, "2025-12-28", "at Carolina Panthers", False, "W", 27, 10),
    (2025, 18, "2026-01-03", "at San Francisco 49ers", False, "W", 13, 3),
]

# sanity check against known final records
EXPECTED_RECORDS = {2021: (7, 10), 2022: (9, 8), 2023: (9, 8), 2024: (10, 7), 2025: (14, 3)}

# ---------------------------------------------------------------------------
# 2. External monthly series (year, month) -> value
# ---------------------------------------------------------------------------
SNOW_NH_KM2 = {
    (2021, 9): 5585195, (2021, 10): 18137454, (2021, 11): 35448095, (2021, 12): 44512782,
    (2022, 1): 47287711,
    (2022, 9): 5930433, (2022, 10): 18660476, (2022, 11): 37745422, (2022, 12): 43559834,
    (2023, 1): 46265979,
    (2023, 9): 5353861, (2023, 10): 18732519, (2023, 11): 35586043, (2023, 12): 42472548,
    (2024, 1): 46886400,
    (2024, 9): 4938211, (2024, 10): 18883733, (2024, 11): 34319511, (2024, 12): 42735811,
    (2025, 1): 45017589,
    (2025, 9): 5737535, (2025, 10): 17997424, (2025, 11): 33119288, (2025, 12): 41875221,
    (2026, 1): 46924814,
}

BTC_USD_FIRST_OF_MONTH = {
    (2021, 9): 48847.03, (2021, 10): 48116.94, (2021, 11): 61004.41, (2021, 12): 57229.83,
    (2022, 1): 47686.81,
    (2022, 9): 20127.14, (2022, 10): 19312.10, (2022, 11): 20485.27, (2022, 12): 16967.13,
    (2023, 1): 16625.08,
    (2023, 9): 25800.72, (2023, 10): 27983.75, (2023, 11): 35437.25, (2023, 12): 38688.75,
    (2024, 1): 44167.33,
    (2024, 9): 57325.49, (2024, 10): 60837.01, (2024, 11): 69482.47, (2024, 12): 97279.79,
    (2025, 1): 94419.76,
    (2025, 9): 109250.59, (2025, 10): 118648.93, (2025, 11): 110064.02, (2025, 12): 86321.57,
    (2026, 1): 88731.98,
}

ROCKET_LAUNCHES = {
    (2021, 9): 12, (2021, 10): 12, (2021, 11): 16, (2021, 12): 24,
    (2022, 1): 8,
    (2022, 9): 17, (2022, 10): 23, (2022, 11): 20, (2022, 12): 18,
    (2023, 1): 16,
    (2023, 9): 24, (2023, 10): 20, (2023, 11): 17, (2023, 12): 30,
    (2024, 1): 23,
    (2024, 9): 23, (2024, 10): 21, (2024, 11): 32, (2024, 12): 31,
    (2025, 1): 22,
    (2025, 9): 32, (2025, 10): 28, (2025, 11): 32, (2025, 12): 41,
    (2026, 1): 25,
}


def moon_illumination_pct(d: date) -> float:
    """Approximate % of the Moon's visible disk illuminated on date d.

    Classic synodic-month approximation: phase = days since a known new
    moon, mod the synodic month length (29.53058867 days). Illuminated
    fraction = (1 - cos(2*pi*phase/synodic)) / 2. Accurate to within ~1-2%
    of precise ephemeris values, which is plenty for this.
    """
    synodic = 29.53058867
    known_new_moon = date(2000, 1, 6)  # a reference new moon (UTC)
    days = (d - known_new_moon).days
    phase = (days % synodic + synodic) % synodic
    frac = (1 - math.cos(2 * math.pi * phase / synodic)) / 2
    return round(frac * 100, 1)


def month_key(iso_date: str):
    y, m, _ = iso_date.split("-")
    return (int(y), int(m))


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return cov / math.sqrt(vx * vy)


def main():
    games = []
    records = {}
    for season, week, d, opp, home, result, pf, pa in GAMES_RAW:
        mk = month_key(d)
        g = {
            "season": season,
            "week": week,
            "date": d,
            "opponent": opp,
            "home": home,
            "result": result,
            "win": 1 if result == "W" else 0,
            "pf": pf,
            "pa": pa,
            "margin": pf - pa,
            "snow_km2": SNOW_NH_KM2.get(mk),
            "btc_usd": BTC_USD_FIRST_OF_MONTH.get(mk),
            "launches": ROCKET_LAUNCHES.get(mk),
            "moon_pct": moon_illumination_pct(date(*[int(x) for x in d.split("-")])),
        }
        games.append(g)
        rec = records.setdefault(season, {"w": 0, "l": 0})
        rec["w" if result == "W" else "l"] += 1

    for season, (w, l) in EXPECTED_RECORDS.items():
        assert records[season]["w"] == w and records[season]["l"] == l, (
            f"Season {season} record mismatch: got {records[season]}, expected {w}-{l}"
        )

    # sanity: no missing joins
    for g in games:
        for k in ("snow_km2", "btc_usd", "launches", "moon_pct"):
            assert g[k] is not None, f"missing {k} for {g['date']}"

    metrics = {
        "snow_km2": [g["snow_km2"] for g in games],
        "btc_usd": [g["btc_usd"] for g in games],
        "launches": [g["launches"] for g in games],
        "moon_pct": [g["moon_pct"] for g in games],
    }
    wins = [g["win"] for g in games]
    margins = [g["margin"] for g in games]

    correlations = {}
    for name, series in metrics.items():
        correlations[name] = {
            "r_win": round(pearson(series, wins), 3),
            "r_margin": round(pearson(series, margins), 3),
        }

    summary = {}
    for name, series in metrics.items():
        win_vals = [v for v, w in zip(series, wins) if w == 1]
        loss_vals = [v for v, w in zip(series, wins) if w == 0]
        summary[name] = {
            "avg_on_win": round(sum(win_vals) / len(win_vals), 2),
            "avg_on_loss": round(sum(loss_vals) / len(loss_vals), 2),
        }

    out = {
        "games": games,
        "records": {str(k): v for k, v in records.items()},
        "correlations": correlations,
        "summary": summary,
        "sources": {
            "games": "Wikipedia season articles (en.wikipedia.org/wiki/<year>_Seattle_Seahawks_season)",
            "snow_km2": "Rutgers University Global Snow Lab, NH monthly snow cover extent (climate.rutgers.edu/snowcover)",
            "btc_usd": "officialdata.org/bitcoin-price, first-of-month price",
            "launches": "The Space Devs Launch Library 2 (ll.thespacedevs.com), monthly launch count",
            "moon_pct": "Computed locally from synodic month approximation (no API)",
        },
    }

    with open("seahawks_universe.json", "w") as f:
        json.dump(out, f, indent=2)

    print("Records:", records)
    print("Correlations:")
    for k, v in correlations.items():
        print(" ", k, v)
    print("Summary (avg on win vs loss):")
    for k, v in summary.items():
        print(" ", k, v)
    print(f"\nWrote seahawks_universe.json with {len(games)} games")


if __name__ == "__main__":
    main()
