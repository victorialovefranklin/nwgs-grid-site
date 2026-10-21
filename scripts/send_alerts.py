#!/usr/bin/env python3
"""
NWGS Grid(TM) - weekly alert emails
Author: Victoria Love Franklin — PhD Data Science Student · Peer-Reviewed Published Scientist · Developer
Copyright © 2026 Victoria Love Franklin. All rights reserved. See LICENSE.

    python3 scripts/send_alerts.py <EXPORT_DIR> [--dry-run]

After a passing weekly run:
  1. records the run in Supabase (table pipeline_runs),
  2. reads everyone's active alert rules,
  3. matches them against this run's county activity (CountyActivity.csv),
  4. sends one email per person listing what matched, and
  5. logs each sent rule in alert_log so nobody gets the same alert twice for one run.

Environment (GitHub secrets):
  SUPABASE_SECRET_KEY            required; never put this in the website
  SMTP_USER, SMTP_PASSWORD       sender account (Gmail: an App Password)
  SMTP_HOST, SMTP_PORT           optional, default smtp.gmail.com:465
  RELEASE_TAG                    optional, stored with the run
Without SUPABASE_SECRET_KEY the script does nothing and exits 0. Without SMTP
credentials it matches and prints, but sends nothing and logs nothing.
"""
import json
import os
import smtplib
import ssl
import sys
import urllib.request
from collections import defaultdict
from email.message import EmailMessage
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://nwgsgrid.com/"
RANK = {"Very Low": 0, "Low": 1, "Typical": 2, "Elevated": 3, "High": 4}
STATE_NAMES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
               "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia",
               "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
               "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
               "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
               "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
               "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
               "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
               "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
               "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}


class Supabase:
    def __init__(self, url, key):
        self.base = url.rstrip("/") + "/rest/v1/"
        self.h = {"apikey": key, "Content-Type": "application/json"}
        if not key.startswith("sb_"):          # legacy JWT service_role key also needs the Bearer header
            self.h["Authorization"] = f"Bearer {key}"

    def _req(self, method, path, body=None, prefer=None):
        h = dict(self.h)
        if prefer:
            h["Prefer"] = prefer
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, headers=h, method=method)
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
            return json.loads(txt) if txt.strip() else None

    def get(self, path):
        return self._req("GET", path)

    def upsert(self, table, rows):
        return self._req("POST", f"{table}?on_conflict={'run_id' if table == 'pipeline_runs' else 'rule_id,run_id'}",
                         rows, prefer="resolution=merge-duplicates,return=minimal")


def match_rules(rules, activity):
    """rules: list of dicts; activity: DataFrame(pathogen, county_fips, county_name, state_code, level, activity_z).
    Returns {rule_id: [(county label, level, z), ...]} for rules that matched."""
    act = activity.copy()
    act["county_fips"] = act["county_fips"].astype(str).str.zfill(5)
    act["rank"] = act["level"].map(RANK).fillna(-1)
    out = {}
    for r in rules:
        q = act[(act.pathogen == r["pathogen"]) & (act["rank"] >= RANK[r["min_level"]])]
        q = q[q.county_fips == r["area_code"]] if r["area_type"] == "county" else q[q.state_code == r["area_code"]]
        if len(q):
            out[r["id"]] = [(f"{n}, {s}", lv, float(z)) for n, s, lv, z in
                            q.sort_values("activity_z", ascending=False)[["county_name", "state_code", "level", "activity_z"]].itertuples(index=False)]
    return out


def compose(email, items, as_of, run_id):
    lines, html = [], []
    for rule, hits in items:
        head = f"{rule['pathogen']} · {rule['area_label']} ({'High' if rule['min_level'] == 'High' else 'Elevated or High'})"
        lines.append(head)
        html.append(f"<h3 style='margin:16px 0 4px;font-size:15px'>{head}</h3><ul style='margin:0;padding-left:18px'>")
        for label, lv, z in hits[:15]:
            lines.append(f"  - {label}: {lv} (z {z:+.2f})")
            html.append(f"<li>{label}: <b>{lv}</b> (z {z:+.2f})</li>")
        if len(hits) > 15:
            lines.append(f"  - and {len(hits) - 15} more")
            html.append(f"<li>and {len(hits) - 15} more</li>")
        html.append("</ul>")
    msg = EmailMessage()
    msg["Subject"] = f"NWGS Grid alert: {len(items)} of your alert{'s' if len(items) > 1 else ''} matched (data through {as_of})"
    msg["To"] = email
    intro = (f"Wastewater activity reached the level you asked about in the latest NWGS Grid update "
             f"(four weeks ending {as_of}, run {run_id}).")
    foot = (f"See the map: {SITE}#map\nManage or pause your alerts: {SITE}#myalerts\n\n"
            "Levels compare each site with its own history; they describe relative change, not case counts. "
            "For information only; not medical advice.\n\n"
            "NWGS Grid™ · © Victoria Love Franklin · alerts@nwgsgrid.com")
    msg.set_content(intro + "\n\n" + "\n".join(lines) + "\n\n" + foot)
    msg.add_alternative(
        f"<div style='font-family:Arial,sans-serif;font-size:14px;color:#13222a;max-width:560px'>"
        f"<p>{intro}</p>{''.join(html)}"
        f"<p style='margin-top:18px'><a href='{SITE}#map'>See the map</a> · <a href='{SITE}#myalerts'>Manage or pause your alerts</a></p>"
        f"<p style='color:#56686d;font-size:12px'>Levels compare each site with its own history; they describe relative change, "
        f"not case counts. For information only; not medical advice.<br>NWGS Grid™ · © Victoria Love Franklin · "
        f"alerts@nwgsgrid.com</p></div>", subtype="html")
    return msg


def main(export_dir, dry_run=False):
    key = os.getenv("SUPABASE_SECRET_KEY")
    if not key:
        print("[alerts] SUPABASE_SECRET_KEY not set - skipping")
        return 0
    cfg = json.loads((ROOT / "site_src" / "supabase.json").read_text())
    sb = Supabase(os.getenv("SUPABASE_URL") or cfg["url"], key)
    ex = Path(export_dir)
    man = json.loads((ex / "manifest.json").read_text())
    run_id, as_of = man["run_id"], man["data_as_of"]

    sb.upsert("pipeline_runs", [{"run_id": run_id, "data_as_of": as_of, "data_pulled_utc": man.get("data_pulled_utc"),
                                 "gate_status": man.get("gate_status"), "release_tag": os.getenv("RELEASE_TAG")}])
    rules = sb.get("alert_rules?active=eq.true&select=*")
    profiles = {p["id"]: p for p in sb.get("profiles?select=id,email,alerts_paused")}
    sent = {r["rule_id"] for r in sb.get(f"alert_log?run_id=eq.{run_id}&select=rule_id")}
    print(f"[alerts] run {run_id}: {len(rules)} active rules, {len(profiles)} people, {len(sent)} already sent")

    activity = pd.read_csv(ex / "CountyActivity.csv", dtype={"county_fips": str})
    matched = match_rules([r for r in rules if r["id"] not in sent], activity)
    by_user = defaultdict(list)
    for r in rules:
        if r["id"] in matched:
            by_user[r["user_id"]].append((r, matched[r["id"]]))

    user, pw = os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD")
    can_send = bool(user and pw) and not dry_run
    if not can_send:
        print("[alerts] no SMTP credentials (or --dry-run): matching only, nothing sent")
    n_mail = 0
    server = None
    try:
        for uid, items in by_user.items():
            prof = profiles.get(uid)
            if not prof or prof.get("alerts_paused"):
                continue
            msg = compose(prof["email"], items, as_of, run_id)
            print(f"[alerts] {prof['email']}: {len(items)} rule(s) matched")
            if not can_send:
                continue
            if server is None:
                server = smtplib.SMTP_SSL(os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", "465")),
                                          context=ssl.create_default_context(), timeout=60)
                server.login(user, pw)
            msg["From"] = f"NWGS Grid alerts <{user}>"
            msg["Reply-To"] = "alerts@nwgsgrid.com"
            server.send_message(msg)
            n_mail += 1
            sb.upsert("alert_log", [{"rule_id": r["id"], "run_id": run_id,
                                     "detail": f"{len(h)} area(s): " + "; ".join(f"{a} {lv}" for a, lv, _ in h[:5])}
                                    for r, h in items])
    finally:
        if server is not None:
            server.quit()
    print(f"[alerts] emails sent: {n_mail}")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    sys.exit(main(args[0], dry_run="--dry-run" in sys.argv))
