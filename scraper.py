import requests
import json
import os
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")

def get_schedule():
    url = f"https://api-web.nhle.com/v1/schedule/{TODAY}"
    r = requests.get(url, timeout=10)
    return r.json()

def get_lineup(game_id):
    url = f"https://api-web.nhle.com/v1/game/{game_id}/landing"
    r = requests.get(url, timeout=10)
    return r.json()

def get_injuries():
    url = "https://www.rotowire.com/hockey/tables/injury-report.php?league=NHL&table=active"
    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    try:
        return r.json()
    except:
        return []

def get_standings():
    url = "https://api-web.nhle.com/v1/standings/now"
    r = requests.get(url, timeout=10)
    return r.json()

def extract_goalie(landing, side):
    try:
        roster = landing.get("matchup", {}).get(f"{side}Team", {}).get("roster", [])
        for p in roster:
            if p.get("positionCode") == "G":
                name = p.get("name", {}).get("default", "TBD")
                sv = p.get("seasonStats", {}).get("savePctg", 0)
                gaa = p.get("seasonStats", {}).get("goalsAgainstAverage", 0)
                return {"name": name, "sv": f"{sv:.3f}", "gaa": f"{gaa:.2f}"}
    except:
        pass
    return {"name": "TBD", "sv": ".000", "gaa": "0.00"}

def extract_pp_line(landing, side):
    try:
        lines = landing.get("matchup", {}).get(f"{side}Team", {}).get("powerPlayLines", [])
        if lines:
            pp1 = lines[0].get("forwards", []) + lines[0].get("defense", [])
            names = [p.get("name", {}).get("default", "").split(" ")[-1] for p in pp1]
            return "PP1: " + " · ".join(names[:5])
    except:
        pass
    return "PP1: TBD"

def fetch_all():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching NHL data for {TODAY}...")
    schedule = get_schedule()
    injuries = get_injuries()
    standings = get_standings()

    games = []
    try:
        day = schedule["gameWeek"][0]["games"]
    except:
        day = []

    for g in day:
        game_id = g["id"]
        away = g["awayTeam"]["abbrev"]
        home = g["homeTeam"]["abbrev"]
        away_full = g["awayTeam"].get("commonName", {}).get("default", away)
        home_full = g["homeTeam"].get("commonName", {}).get("default", home)
        start_utc = g.get("startTimeUTC", "")
        print(f"  -> {away} @ {home} (game {game_id})")
        try:
            landing = get_lineup(game_id)
        except:
            landing = {}
        keeper_away = extract_goalie(landing, "away")
        keeper_home = extract_goalie(landing, "home")
        inj_away = [i for i in injuries if i.get("team") == away]
        inj_home = [i for i in injuries if i.get("team") == home]
        pp_away = extract_pp_line(landing, "away")
        pp_home = extract_pp_line(landing, "home")
        games.append({
            "game_id": game_id,
            "start_utc": start_utc,
            "away_code": away,
            "home_code": home,
            "away_full": away_full,
            "home_full": home_full,
            "keeper_away": keeper_away,
            "keeper_home": keeper_home,
            "injuries_away": inj_away,
            "injuries_home": inj_home,
            "pp_away": pp_away,
            "pp_home": pp_home,
        })

    data = {
        "date": TODAY,
        "updated_at": datetime.now().isoformat(),
        "games": games,
        "standings": standings,
    }
    os.makedirs("data", exist_ok=True)
    with open("data/nhl_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] {len(games)} games saved -> data/nhl_data.json")
    return data

if __name__ == "__main__":
    fetch_all()
