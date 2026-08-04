#!/usr/bin/env python3
"""
Builds acr/data-acr.json from the official "Architecture contemporaine remarquable"
(ACR) dataset (Ministère de la Culture, data.gouv.fr) — the mechanical/deterministic
half of preparing this as the next database for archi.cool, in the same schema as
the site's existing data.json (built from the Monuments Historiques list).

What this script does NOT do (left for a follow-up curatorial pass, same as the
original 241-place dataset needed):
  - `styles` (Modernisme / Brutalisme / Art Déco / Industriel et rationaliste) is left
    as an empty list — the source has no style field, this requires actual
    architectural judgement per building, the same way the original 241 were tagged.
  - `nom` is a straight copy of `nom_officiel` for now — the existing data.json's
    `nom` is often a hand-edited, shortened/disambiguated version of the raw Mérimée
    title (see e.g. PA33000142 "Maison, 14 rue Le Corbusier" vs its nom_officiel
    "Maison de type gratte-ciel") — that editorial pass hasn't been done here yet.
  - `visite_statut` is left unset (same as most of the original dataset).
  - `image` is left unset — photos need sourcing the same way as photos-a-faire.xlsx.
  - `code_postal` is left unset — the ACR CSV has no postal code field, only INSEE
    commune code (not the same thing).
  - Rows with no coordinates (~14% of the source) are kept but with lat/lon null and
    precision_coord "manquant" — they need geocoding before they can appear on the map.

Re-run any time: `python3 acr/build.py` (source CSV is re-downloaded fresh each time).
"""
import csv
import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
CSV_URL = "https://www.data.gouv.fr/api/1/datasets/r/80b6ac20-41b1-400c-8860-af201ff7dcb6"
CSV_PATH = HERE / "acr-source.csv"
OUT_PATH = HERE / "data-acr.json"

ROLE_PAREN_RE = re.compile(r"\s*\([^)]*\)")
YEAR_RE = re.compile(r"\b(1[7-9]\d{2}|20[0-2]\d)\b")


def download_csv():
    print(f"Downloading {CSV_URL} ...")
    urllib.request.urlretrieve(CSV_URL, CSV_PATH)
    print(f"Saved to {CSV_PATH} ({CSV_PATH.stat().st_size / 1e6:.1f} MB)")


def clean_text(s):
    if not s:
        return None
    s = s.strip().strip('"').strip()
    return s or None


def clean_architecte(raw):
    """'Dikansky Georges (architecte);Michaut Albert (architecte maître d'œuvre)'
    -> 'Dikansky Georges, Michaut Albert' — strips role annotations, keeps raw
    Mérimée "Last First" order (same convention as the existing dataset), the
    client-side formatArchitecte() already reformats this for display."""
    if not raw or not raw.strip():
        return None
    parts = [ROLE_PAREN_RE.sub("", p).strip() for p in raw.split(";")]
    parts = [p for p in parts if p]
    return ", ".join(parts) if parts else None


def normalize_siecle(raw):
    if not raw:
        return None
    m = re.search(r"(1\d|2\d)e siècle", raw)
    return f"{m.group(1)}e s." if m else raw


def extract_annee(raw):
    if not raw:
        return None
    years = [int(y) for y in YEAR_RE.findall(raw)]
    return min(years) if years else None


def decennie_for(annee):
    if not annee:
        return "Non renseignée"
    decade = (annee // 10) * 10
    return f"Années {decade}"


def parse_coords(raw):
    if not raw or "," not in raw:
        return None, None
    try:
        lat_s, lon_s = raw.split(",", 1)
        return float(lat_s), float(lon_s)
    except ValueError:
        return None, None


def domaine_from_denominations(raw):
    if not raw:
        return None
    first = raw.split(";")[0].strip()
    return first or None


def build_protection(date_label):
    if not date_label or not date_label.strip():
        return "Labellisé Architecture contemporaine remarquable"
    return f"{date_label.strip()} : labellisé Architecture contemporaine remarquable"


def transform(row):
    ref = row["Reference_de_la_notice"].strip()
    nom_officiel = clean_text(row["Titre_courant"])
    lat, lon = parse_coords(row["Coordonnees"])
    annee = extract_annee(row["Datation_de_l_edifice"])
    historique = clean_text(row["Description_historique"]) or clean_text(row["Description_de_l_edifice"])

    return {
        "ref": ref,
        "nom": nom_officiel,          # TODO curatorial pass: shorten/disambiguate like the MH set
        "nom_officiel": nom_officiel,
        "architecte": clean_architecte(row["Auteur_de_l_edifice"]),
        "commune": clean_text(row["Commune_forme_editoriale"]) or clean_text(row["Commune"]),
        "dept": clean_text(row["Departement_en_lettres"]),
        "region": clean_text(row["Region"]),
        "protection": build_protection(row["Date_de_Label"]),
        "statut": "labellisé ACR",
        "siecle": normalize_siecle(row["Siecle_de_la_campagne_principale_de_construction"]),
        "annee": annee,
        "decennie": decennie_for(annee),
        "lat": lat,
        "lon": lon,
        "precision_coord": "exact" if lat is not None else "manquant",
        "domaine": domaine_from_denominations(row["Denominations"]),
        "styles": [],                 # TODO curatorial pass: needs real style classification
        "proprietaire": clean_text(row["Statut_juridique_du_proprietaire"]),
        "proprietaire_detail": None,
        "lien_pop": f"https://www.pop.culture.gouv.fr/notice/merimee/{ref}",
        "lien_source": None,
        "historique": historique,
        "image": None,                # TODO: photo sourcing pass, same workflow as photos-a-faire.xlsx
        "adresse": clean_text(row["Adresse_forme_editoriale"]),
        "code_postal": None,          # TODO: not in source, needs enrichment (INSEE != postal code)
        "visite_statut": None,
    }


def main():
    download_csv()
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="|"))

    places = [transform(r) for r in rows]

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, separators=(",", ": "))

    missing_coords = sum(1 for p in places if p["lat"] is None)
    missing_architecte = sum(1 for p in places if not p["architecte"])
    missing_historique = sum(1 for p in places if not p["historique"])
    print(f"\nWrote {len(places)} places to {OUT_PATH}")
    print(f"  missing coordinates: {missing_coords} ({100*missing_coords/len(places):.0f}%)")
    print(f"  missing architecte:  {missing_architecte} ({100*missing_architecte/len(places):.0f}%)")
    print(f"  missing historique:  {missing_historique} ({100*missing_historique/len(places):.0f}%)")


if __name__ == "__main__":
    main()
