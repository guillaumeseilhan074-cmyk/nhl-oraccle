import json
import os
from datetime import datetime, timedelta

def load_data():
    with open("data/nhl_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def time_to_paris(utc_str):
    try:
        dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        paris = dt + timedelta(hours=1)
        return paris.strftime("%Hh%M")
    except:
        return "--"

def badge(status):
    if "DTD" in status:
        return '<span class="badge-dtd">DTD</span>'
    elif "IR-LT" in status:
        return '<span class="badge-irs">IR-LT</span>'
    elif "OUT" in status or "IR" in status:
        return '<span class="badge-inj">OUT</span>'
    return ""

def gen_injuries(injuries):
    if not injuries:
        return '<span class="no-absent">Aucun absent confirmé</span>'
    html = ""
    for inj in injuries[:6]:
        name = inj.get("player", "?")
        status = inj.get("status", "OUT")
        detail = inj.get("injury", "")
        html += f'''<div class="absent-item"><span class="absent-name">{name}</span>{badge(status)}<span class="absent-reason">{detail}</span></div>'''
    return html

def gen_card(game):
    away = game["away_code"]
    home = game["home_code"]
    away_full = game["away_full"]
    home_full = game["home_full"]
    t = time_to_paris(game["start_utc"])
    ka = game["keeper_away"]
    kh = game["keeper_home"]
    inj_a = gen_injuries(game["injuries_away"])
    inj_h = gen_injuries(game["injuries_home"])
    pp_a = game["pp_away"]
    pp_h = game["pp_home"]
    gid = game["game_id"]

    return f"""
<div class="card" id="game-{gid}">
  <div class="card-header">
    <div class="teams-row">
      <div class="team-block"><div class="team-code">{away}</div><div class="team-full">{away_full}</div></div>
      <div class="vs-block"><span class="vs-at">@</span><span class="vs-time">{t}</span></div>
      <div class="team-block" style="text-align:right"><div class="team-code">{home}</div><div class="team-full">{home_full}</div></div>
    </div>
  </div>
  <div class="card-body">
    <div class="keepers-row">
      <div class="keeper-block">
        <div class="keeper-label">{away} · GARDIEN EXTÉRIEUR</div>
        <div class="keeper-name">{ka["name"]}</div>
        <div class="keeper-stats">
          <span class="stat-chip good">SV% {ka["sv"]}</span>
          <span class="stat-chip avg">GAA {ka["gaa"]}</span>
          <span class="stat-chip neutral">{pp_a[:40]}</span>
        </div>
      </div>
      <div class="keeper-block">
        <div class="keeper-label">{home} · GARDIEN DOMICILE</div>
        <div class="keeper-name">{kh["name"]}</div>
        <div class="keeper-stats">
          <span class="stat-chip good">SV% {kh["sv"]}</span>
          <span class="stat-chip avg">GAA {kh["gaa"]}</span>
          <span class="stat-chip neutral">{pp_h[:40]}</span>
        </div>
      </div>
    </div>
    <div class="absents-row">
      <div class="absent-block"><div class="absent-label">Absents {away}</div>{inj_a}</div>
      <div class="absent-block"><div class="absent-label">Absents {home}</div>{inj_h}</div>
    </div>
  </div>
  <div class="card-toggle" onclick="var b=this.previousElementSibling;b.classList.toggle('collapsed');this.textContent=b.classList.contains('collapsed')?'▶ Développer':'▼ Réduire'">▼ Réduire</div>
</div>"""

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f5f0;color:#1a1a1a;font-size:14px}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;background:#fff;border-bottom:1px solid #e0e0e0;position:sticky;top:0;z-index:100}
.brand{font-size:20px;font-weight:700}.brand span{color:#e85d04}
.update-badge{font-size:11px;background:#e8f5e9;border:1px solid #a5d6a7;border-radius:20px;padding:3px 10px;color:#2e7d32}
.content{padding:16px 20px;max-width:1000px;margin:0 auto;display:flex;flex-direction:column;gap:14px}
.card{background:#fff;border:1.5px solid #e0e0e0;border-radius:14px;overflow:hidden}
.card:hover{border-color:#bbb;box-shadow:0 4px 20px rgba(0,0,0,.07)}
.card-header{padding:14px 18px 10px;border-bottom:1px solid #f0f0ec}
.teams-row{display:flex;align-items:center;justify-content:space-between}
.team-code{font-size:28px;font-weight:800}.team-full{font-size:11px;color:#888;margin-top:2px}
.vs-block{display:flex;flex-direction:column;align-items:center;gap:4px}
.vs-time{background:#1a1a1a;color:#fff;border-radius:6px;padding:4px 10px;font-size:13px;font-weight:600}
.vs-at{font-size:11px;color:#aaa}
.keepers-row,.absents-row{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#f0f0ec;border-top:1px solid #f0f0ec}
.keeper-block,.absent-block{background:#fff;padding:10px 16px}
.keeper-label,.absent-label{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#aaa;margin-bottom:4px}
.keeper-name{font-size:15px;font-weight:700;margin-bottom:6px}
.keeper-stats{display:flex;flex-wrap:wrap;gap:5px}
.stat-chip{font-size:11px;padding:2px 8px;border-radius:4px;border:1px solid #e0e0e0;background:#fafaf8;color:#444}
.stat-chip.good{border-color:#a5d6a7;background:#f1f8e9;color:#2e7d32}
.stat-chip.avg{border-color:#ffe082;background:#fffde7;color:#f57f17}
.absent-item{display:inline-flex;align-items:center;gap:4px;margin-right:8px;margin-bottom:3px}
.absent-name{font-size:12px;font-weight:600}
.badge-dtd{background:#fff8e1;color:#f57f17;border:1px solid #ffe082;border-radius:4px;padding:1px 5px;font-size:10px;font-weight:700}
.badge-inj{background:#ffebee;color:#c62828;border:1px solid #ffcdd2;border-radius:4px;padding:1px 5px;font-size:10px;font-weight:700}
.badge-irs{background:#f3e5f5;color:#7b1fa2;border:1px solid #e1bee7;border-radius:4px;padding:1px 5px;font-size:10px;font-weight:700}
.no-absent{font-size:12px;color:#bbb;font-style:italic}
.absent-reason{font-size:10px;color:#aaa}
.card-toggle{padding:6px 16px;border-top:1px solid #f5f5f0;font-size:11px;color:#aaa;cursor:pointer;text-align:center;background:#fafaf8}
.card-body.collapsed{display:none}
"""

def build():
    data = load_data()
    updated = data.get("updated_at", "")[:16].replace("T", " ")
    date = data.get("date", "")
    games = data.get("games", [])
    cards_html = "\n".join(gen_card(g) for g in games)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta http-equiv="refresh" content="1800"/>
<title>NHL Oracle – {date}</title>
<style>{CSS}</style>
</head>
<body>
<div class="topbar">
  <div><span class="brand">NHL <span>Oracle</span></span></div>
  <span class="update-badge">✓ Mis à jour : {updated}</span>
</div>
<div class="content">{cards_html}</div>
</body>
</html>"""

    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] public/index.html generated — {len(games)} games")

if __name__ == "__main__":
    build()
