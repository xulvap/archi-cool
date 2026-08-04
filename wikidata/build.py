#!/usr/bin/env python3
"""
Builds wikidata/data-wikidata.json — a third candidate base for archi.cool,
alongside data.json (MH) and acr/data-acr.json (ACR label).

Why Wikidata: unlike ACR, style isn't something we have to guess here — it's
a real Wikidata property (P149, "architectural style"), so every place this
script pulls already comes with the right style attached. That was the
single biggest bottleneck on the ACR base (only ~23% of 1824 places got a
confident style after a full manual pass). The trade-off is scale: Wikidata
only has ~300-900 France-tagged places per category, vs. ACR's 1824.

Queries four style categories directly (P149 = style) — Modernisme,
Art Déco, Brutalisme, Post-modernisme — plus "usine" (factory, P31/P279*
instance-of-subclass-of) as a proxy for Industriel et rationaliste, since
Wikidata barely uses a dedicated "industrial architecture" style tag (only
3 results) but does reliably type buildings as factories.

Cross-references every result's Mérimée ID (P380, wdt:P380 — confirmed to
be the exact same "PA" reference scheme as data.json's `ref` field) against
the site's existing 241 places, so anything already on the map is flagged
and excluded rather than duplicated.

Usage: python3 wikidata/build.py
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
MH_PATH = HERE.parent / "data.json"
OUT_PATH = HERE / "data-wikidata.json"

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
UA = "archi-cool-data-prep/1.0 (https://github.com/xulvap/archi-cool)"

# Wikidata QIDs for the style property (P149) -> our taxonomy label.
STYLE_QIDS = {
    "Q245188": "Modernisme",            # modern architecture
    "Q12720942": "Art Déco",            # Art Deco architecture
    "Q994776": "Brutalisme",            # brutalism
    "Q595448": "Post-modernisme",       # postmodern architecture
}
FACTORY_QID = "Q83405"  # factory — used via P31/P279* as a proxy for Industriel et rationaliste


def run_sparql(query, max_retries=5):
    url = SPARQL_ENDPOINT + "?" + urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(url, headers={"Accept": "application/sparql-results+json", "User-Agent": UA})
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = int(e.headers.get("Retry-After", 10)) if e.headers else 10
                print(f"  (429, on attend {wait}s...)")
                time.sleep(wait)
                continue
            raise


def query_style(style_qid):
    """One row per item, architects/images already aggregated with GROUP_CONCAT
    so we don't get row-per-architect duplicates like the raw exploratory
    query did."""
    query = f"""
    SELECT ?item ?itemLabel ?coord ?communeLabel ?inception ?merimee
           (GROUP_CONCAT(DISTINCT ?architectLabel; separator=", ") AS ?architectes)
           (SAMPLE(?image) AS ?img)
    WHERE {{
      ?item wdt:P149 wd:{style_qid} .
      ?item wdt:P17 wd:Q142 .
      ?item wdt:P625 ?coord .
      OPTIONAL {{ ?item wdt:P131 ?commune . }}
      OPTIONAL {{ ?item wdt:P571 ?inception . }}
      OPTIONAL {{ ?item wdt:P380 ?merimee . }}
      OPTIONAL {{ ?item wdt:P84 ?architect . ?architect rdfs:label ?architectLabel . FILTER(LANG(?architectLabel)="fr") }}
      OPTIONAL {{ ?item wdt:P18 ?image . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
    }}
    GROUP BY ?item ?itemLabel ?coord ?communeLabel ?inception ?merimee
    """
    return run_sparql(query)["results"]["bindings"]


def query_factories():
    query = f"""
    SELECT ?item ?itemLabel ?coord ?communeLabel ?inception ?merimee
           (GROUP_CONCAT(DISTINCT ?architectLabel; separator=", ") AS ?architectes)
           (SAMPLE(?image) AS ?img)
    WHERE {{
      ?item wdt:P31/wdt:P279* wd:{FACTORY_QID} .
      ?item wdt:P17 wd:Q142 .
      ?item wdt:P625 ?coord .
      OPTIONAL {{ ?item wdt:P131 ?commune . }}
      OPTIONAL {{ ?item wdt:P571 ?inception . }}
      OPTIONAL {{ ?item wdt:P380 ?merimee . }}
      OPTIONAL {{ ?item wdt:P84 ?architect . ?architect rdfs:label ?architectLabel . FILTER(LANG(?architectLabel)="fr") }}
      OPTIONAL {{ ?item wdt:P18 ?image . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
    }}
    GROUP BY ?item ?itemLabel ?coord ?communeLabel ?inception ?merimee
    """
    return run_sparql(query)["results"]["bindings"]


def parse_coord(point_wkt):
    # "Point(2.300724647 48.868789967)" -> (lat, lon); returns None if the
    # geometry isn't a clean single point (e.g. some factory entries carry
    # oddly-formed coordinates that don't split into exactly two parts).
    inner = point_wkt.strip().removeprefix("Point(").removesuffix(")")
    parts = inner.split(" ")
    if len(parts) != 2:
        return None
    lon_s, lat_s = parts
    try:
        return float(lat_s), float(lon_s)
    except ValueError:
        return None


def qid_from_uri(uri):
    return uri.rsplit("/", 1)[-1]


def transform(binding, style, existing_refs):
    qid = qid_from_uri(binding["item"]["value"])
    ref = f"WD{qid}"
    merimee = binding.get("merimee", {}).get("value")
    already_on_site = merimee in existing_refs if merimee else False
    coord = parse_coord(binding["coord"]["value"])
    if coord is None:
        return None
    lat, lon = coord
    inception = binding.get("inception", {}).get("value")
    annee = int(inception[:4]) if inception else None
    decennie = f"Années {(annee//10)*10}" if annee else "Non renseignée"

    return {
        "ref": ref,
        "nom": binding.get("itemLabel", {}).get("value"),
        "nom_officiel": binding.get("itemLabel", {}).get("value"),
        "architecte": binding.get("architectes", {}).get("value") or None,
        "commune": binding.get("communeLabel", {}).get("value"),
        "dept": None,          # TODO: needs a P131 chain walk or reverse geocode
        "region": None,        # TODO: same
        "protection": None,
        "statut": None,
        "siecle": None,
        "annee": annee,
        "decennie": decennie,
        "lat": lat,
        "lon": lon,
        "precision_coord": "exact",
        "domaine": None,
        "styles": [style],     # already known — Wikidata's own P149, not guessed
        "proprietaire": None,
        "proprietaire_detail": None,
        "lien_pop": f"https://www.pop.culture.gouv.fr/notice/merimee/{merimee}" if merimee else None,
        "lien_source": f"https://www.wikidata.org/wiki/{qid}",
        "historique": None,
        "image": None,         # TODO: photo pass — see wikidata_image_url below
        "adresse": None,
        "code_postal": None,
        "visite_statut": None,
        # Extra field, not part of the shared site schema — strip before
        # merging into data.json. A real Wikimedia Commons *photograph* (not
        # the site's stylised line-art), kept here only so a future photo
        # pass knows a reference image already exists for this place.
        "wikidata_image_url": binding.get("img", {}).get("value"),
        # Extra field, not part of the shared schema — true if this place's
        # Mérimée ref already matches one of the 241 places on the live map.
        "deja_sur_le_site": already_on_site,
    }


def main():
    mh = json.load(open(MH_PATH, encoding="utf-8"))
    existing_refs = {d["ref"] for d in mh}

    by_ref = {}
    for style_qid, style_label in STYLE_QIDS.items():
        print(f"Requête Wikidata : {style_label} ...")
        for b in query_style(style_qid):
            place = transform(b, style_label, existing_refs)
            if place is None:
                continue
            # a place can legitimately show up under >1 style query; merge styles
            if place["ref"] in by_ref:
                if style_label not in by_ref[place["ref"]]["styles"]:
                    by_ref[place["ref"]]["styles"].append(style_label)
            else:
                by_ref[place["ref"]] = place
        time.sleep(1)  # be polite to the shared public endpoint

    print("Requête Wikidata : usines (proxy Industriel et rationaliste) ...")
    factory_raw = 0
    factory_kept = 0
    for b in query_factories():
        factory_raw += 1
        place = transform(b, "Industriel et rationaliste", existing_refs)
        if place is None:
            continue
        # "usine" (P31/P279* factory) spans everything from medieval mills to
        # 2020s plants — being a factory says nothing about matching the
        # Industriel et rationaliste aesthetic. Undated entries (most of
        # them: ~700/915) can't be trusted at all here, and only a dated,
        # plausibly-20th-century one is worth treating as even a weak style
        # signal, same spirit as ACR's "leave unclassified rather than
        # guess" rule.
        if not place["annee"] or not (1880 <= place["annee"] <= 1990):
            continue
        factory_kept += 1
        if place["ref"] in by_ref:
            if "Industriel et rationaliste" not in by_ref[place["ref"]]["styles"]:
                by_ref[place["ref"]]["styles"].append("Industriel et rationaliste")
        else:
            by_ref[place["ref"]] = place

    places = list(by_ref.values())
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, separators=(",", ": "))

    already = sum(1 for p in places if p["deja_sur_le_site"])
    with_photo = sum(1 for p in places if p["wikidata_image_url"])
    print(f"\nusines : {factory_raw} trouvées, {factory_kept} gardées (datées 1880-1990)")
    print(f"\n{len(places)} lieux uniques écrits dans {OUT_PATH}")
    print(f"  déjà sur le site (data.json) : {already}")
    print(f"  nouveaux : {len(places) - already}")
    print(f"  avec une photo Wikimedia Commons disponible : {with_photo}")


if __name__ == "__main__":
    main()
