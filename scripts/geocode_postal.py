#!/usr/bin/env python3
"""
Fills in missing `code_postal` for a places JSON file (data.json,
acr/data-acr.json, wikidata/data-wikidata.json — anything sharing the same
`lat`/`lon`/`code_postal` fields), by reverse-geocoding each place's
coordinates against the French national address API (same api-adresse.
data.gouv.fr endpoint already used elsewhere in this project for the
"search a city" fallback).

Only touches entries that already have coordinates and don't already have
a postal code — never overwrites anything, never guesses for places with
no lat/lon.

Usage: python3 scripts/geocode_postal.py acr/data-acr.json
       python3 scripts/geocode_postal.py wikidata/data-wikidata.json
"""
import json
import sys
import time
import urllib.error
import urllib.request

REVERSE_URL = "https://api-adresse.data.gouv.fr/reverse/?lon={lon}&lat={lat}"


def reverse_geocode(lat, lon, retries=3):
    url = REVERSE_URL.format(lat=lat, lon=lon)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.load(resp)
            features = data.get("features") or []
            return features[0]["properties"]["postcode"] if features else None
        except (OSError, KeyError, IndexError):
            # OSError covers both urllib.error.URLError and the raw
            # socket.timeout that http.client can raise directly (in
            # Python <3.10 that's not the same class as the builtin
            # TimeoutError, so catching just TimeoutError missed it —
            # found the hard way when a run died silently 200 lieux in).
            if attempt < retries - 1:
                time.sleep(2)
                continue
            return None


def main():
    if len(sys.argv) != 2:
        print("usage: python3 scripts/geocode_postal.py <chemin-vers-fichier.json>")
        sys.exit(1)
    path = sys.argv[1]

    with open(path, encoding="utf-8") as f:
        places = json.load(f)

    todo = [p for p in places if p.get("lat") is not None and not p.get("code_postal")]
    print(f"{len(todo)} lieux à géocoder (sur {len(places)} au total)")

    filled = 0
    for i, p in enumerate(todo):
        postcode = reverse_geocode(p["lat"], p["lon"])
        if postcode:
            p["code_postal"] = postcode
            filled += 1
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(todo)} traités, {filled} trouvés...")
            # save incrementally — a crash mid-run (a flaky public endpoint
            # timed out once already) shouldn't throw away everything found
            # so far.
            with open(path, "w", encoding="utf-8") as f:
                json.dump(places, f, ensure_ascii=False, separators=(",", ": "))
        time.sleep(0.1)  # stay polite to the shared public endpoint

    with open(path, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, separators=(",", ": "))

    print(f"\n{filled}/{len(todo)} codes postaux trouvés et écrits dans {path}")


if __name__ == "__main__":
    main()
