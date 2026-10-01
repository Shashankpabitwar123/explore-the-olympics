"""Reconcile the published Tableau extract with the source CSVs and export summaries.

Run from any directory: python scripts/check_and_export.py
No network access or Tableau Desktop is needed.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from tableauhyperapi import Connection, HyperProcess, Telemetry

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "tableau/Explore_the_Olympics.twbx"


def read_csv(name):
    with (ROOT / f"data/source/{name}.csv").open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def export_csv(name, rows):
    path = ROOT / "data/summary" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    checks = []

    def check(name, condition):
        if not condition:
            raise ValueError(f"Check failed: {name}")
        checks.append(name)

    raw = {name: read_csv(name) for name in
           ("editions", "events", "awards", "countries", "roster_members")}
    for name, key in (("editions", "id"), ("events", "id"),
                      ("awards", "id"), ("countries", "noc")):
        check(f"{name}: unique nonempty keys",
              len({r[key] for r in raw[name]}) == len(raw[name])
              and all(r[key] for r in raw[name]))
    editions = {r["id"]: r for r in raw["editions"]}
    events = {r["id"]: r for r in raw["events"]}
    awards = {r["id"]: r for r in raw["awards"]}
    countries = {r["noc"]: r["name"] for r in raw["countries"]}
    check("events reference existing editions", all(r["edition"] in editions for r in events.values()))
    check("awards reference matching events and editions", all(
        r["event_id"] in events and r["edition"] == events[r["event_id"]]["edition"]
        for r in awards.values()))
    check("award delegation codes exist", all(r["noc"] in countries for r in awards.values()))
    check("medal codes are gold, silver or bronze", all(r["medal"] in {"1", "2", "3"} for r in awards.values()))
    check("roster members reference matching awards and events", all(
        r["award_id"] in awards and r["event_id"] == awards[r["award_id"]]["event_id"]
        for r in raw["roster_members"]))

    with zipfile.ZipFile(WORKBOOK) as archive, tempfile.TemporaryDirectory() as tmp:
        check("workbook ZIP integrity", archive.testzip() is None)
        xml = ET.fromstring(archive.read(next(n for n in archive.namelist() if n.endswith(".twb"))))
        targets = {c.get("dbname") for c in xml.findall('.//connection[@class="hyper"]')}
        check("one connected, embedded extract", len(targets) == 1 and targets <= set(archive.namelist()))
        extract = Path(tmp) / "published.hyper"
        extract.write_bytes(archive.read(next(iter(targets))))
        with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
                          parameters={"log_dir": tmp}) as hp:
            with Connection(hp.endpoint, extract) as conn:
                table = conn.catalog.get_table_names("Extract")[0]
                columns = [c.name.unescaped for c in conn.catalog.get_table_definition(table).columns]
                rows = [dict(zip(columns, row)) for row in conn.execute_list_query(f"SELECT * FROM {table}")]

    by_type = defaultdict(list)
    for row in rows:
        by_type[row["RowType"]].append(row)
    packaged_awards = {r["AwardID"]: r for r in by_type["Award"]}
    check("every source award appears exactly once in the extract",
          set(packaged_awards) == set(awards) and len(by_type["Award"]) == len(awards))
    check("all award event IDs, medals and delegations match", all(
        r["EventID"] == awards[k]["event_id"] and str(r["Medal"]) == awards[k]["medal"]
        and r["NOC"] == awards[k]["noc"] for k, r in packaged_awards.items()))
    check("winner names match, with country fallback for blank team names", all(
        r["Winner"] == (awards[k]["winner"] or r["Country"]) for k, r in packaged_awards.items()))
    check("team flags match the source", all(
        bool(r["Team"]) == (awards[k]["is_team"] == "True") for k, r in packaged_awards.items()))
    packaged_events = {r["EventID"]: r for r in by_type["Event"]}
    check("all source events appear in the extract", set(packaged_events) == set(events))
    check("every event control preserves edition, sport and category", all(
        all(r[a] == events[r["EventID"]][b] for a, b in
            (("Edition", "edition"), ("Sport", "sport"), ("Category", "category")))
        for r in by_type["Event"]))
    check("four control vertices per event", all(
        n == 4 for n in Counter(r["EventID"] for r in by_type["Event"]).values()))
    label_changes = [{"event_id": k, "source_label": events[k]["label"], "display_label": r["Label"]}
                     for k, r in packaged_events.items() if r["Label"] != events[k]["label"]]
    check("display label changes are historical hurdle distances", all(
        r["source_label"] == "100 / 80 m Hurdles" and
        r["display_label"] in {"80 m Hurdles", "100 m Hurdles"} for r in label_changes))
    result_text = defaultdict(list)
    for r in by_type["ResultLine"]:
        result_text[r["AwardID"]].append(r["Label"] or "")
    normalized = lambda s: " ".join(s.split())
    haystacks = {k: normalized(" ".join(result_text[k]) + " " + r["Winner"])
                for k, r in packaged_awards.items()}
    check("all recorded roster names survive in result labels", all(
        normalized(r["member_name"]) in haystacks[r["award_id"]] for r in raw["roster_members"]))
    check("all edition IDs appear in edition controls",
          {r["Edition"] for r in by_type["Edition"]} == set(editions))
    podium = sorted((str(r["Medal"]), r["Winner"]) for r in by_type["Award"]
                    if r["EventID"] == "63-2013815")
    check("Paris 2024 women's 100 m podium matches", podium == [
        ("1", "Julien Alfred"), ("2", "Sha'Carri Richardson"), ("3", "Melissa Jefferson")])

    summary = []
    for edition in sorted(editions.values(), key=lambda r: (int(r["year"]), r["season"])):
        ee = [r for r in events.values() if r["edition"] == edition["id"]]
        aa = [r for r in awards.values() if r["edition"] == edition["id"]]
        summary.append({"edition_id": edition["id"], "name": edition["name"],
                        "year": edition["year"], "season": edition["season"],
                        "host": edition["host"], "events": len(ee),
                        "sports": len({r["sport"] for r in ee}), "medal_awards": len(aa),
                        "gold": sum(r["medal"] == "1" for r in aa),
                        "silver": sum(r["medal"] == "2" for r in aa),
                        "bronze": sum(r["medal"] == "3" for r in aa)})
    check("edition summary reconciles to events and awards",
          sum(r["events"] for r in summary) == len(events) and
          sum(r["medal_awards"] for r in summary) == len(awards))
    export_csv("editions.csv", summary)
    export_csv("paris-2024-womens-100m.csv", [
        {"medal": {"1": "Gold", "2": "Silver", "3": "Bronze"}[medal], "winner": name,
         "country": next(r["Country"] for r in by_type["Award"] if r["EventID"] == "63-2013815" and r["Winner"] == name)}
        for medal, name in podium])
    report = {"status": "passed", "checks_passed": len(checks), "checks": checks,
              "workbook_sha256": hashlib.sha256(WORKBOOK.read_bytes()).hexdigest(),
              "source_rows": {k: len(v) for k, v in raw.items()},
              "extract_rows": len(rows), "extract_row_types": {k: len(v) for k, v in sorted(by_type.items())},
              "hurdle_label_changes": label_changes,
              "scope": "Checks the saved sources and published extract. Does not independently verify every source fact or automate Tableau interactions."}
    (ROOT / "validation").mkdir(exist_ok=True)
    (ROOT / "validation/check-results.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"Passed {len(checks)} checks; reconciled {len(awards):,} awards and {len(events):,} events.")


if __name__ == "__main__":
    main()
