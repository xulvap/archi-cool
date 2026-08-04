#!/usr/bin/env python3
"""
First-pass style classifier for acr/data-acr.json.

Not a black box: assigns styles.py "high" confidence to a place only when a strong,
explainable signal fires (architect already classified in data.json, or unambiguous
vocabulary in the notice text), and otherwise leaves it for manual/LLM review — see
acr/classify_review.md, generated alongside. The goal is to shrink 1824 manual
judgement calls down to a much smaller stack that actually needs a human/LLM eye,
not to auto-decide everything mechanically.

Adds a 5th style, "Post-modernisme" (see acr/README.md for the rationale), for the
1975-1995ish reaction-to-modernism movement (Bofill, Portzamparc, etc.) that the
original 4-style taxonomy (built for the MH set, which barely reaches the 1980s) has
no bucket for — without it, every ACR postmodern building would either get force-fit
into "Modernisme" (wrong) or dropped as unclassifiable.

Usage: python3 acr/classify_styles.py
Writes:
  - acr/data-acr.json           (styles filled in for high-confidence matches)
  - acr/classify_review.md      (everything else, grouped, for manual review)
"""
import json
import re
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).parent
ACR_PATH = HERE / "data-acr.json"
MH_PATH = HERE.parent / "data.json"

STYLES = ["Modernisme", "Brutalisme", "Art Déco", "Industriel et rationaliste", "Post-modernisme"]

# --- 1. Architect -> style prior, learned from the already-curated 241 MH places ---

def build_architect_priors():
    mh = json.load(open(MH_PATH, encoding="utf-8"))
    priors = defaultdict(Counter)
    for d in mh:
        if not d.get("architecte"):
            continue
        for name in d["architecte"].split(","):
            name = name.strip().lower()
            if len(name) < 3:
                continue
            for s in d["styles"]:
                priors[name][s] += 1
    return priors


# --- 2. Keyword vocabulary per style (French architectural terms) ---
# Matched against nom + historique, case-insensitive. Ordered by specificity: a hit
# on a style-name keyword ("art déco", "brutaliste") is much stronger evidence than a
# generic period word, so keyword hits alone (no architect match) only reach "medium"
# confidence and still land in the review file unless corroborated by date.

KEYWORDS = {
    "Art Déco": [r"art[\s-]?d[ée]co", r"style paquebot", r"exposition.{0,20}1925"],
    "Brutalisme": [r"brutalis[mt]", r"b[ée]ton brut", r"b[ée]ton apparent"],
    "Industriel et rationaliste": [
        r"\busine\b", r"\bhangar\b", r"g[ée]nie civil", r"architecture industrielle",
        r"\bmanufacture\b", r"rationalis[mt]e",
    ],
    "Post-modernisme": [
        r"post[\s-]?moderne", r"postmodernis[mt]e", r"n[ée]o[\s-]?classi(que|sant)",
        r"citation historique", r"clin d.œil",
    ],
    "Modernisme": [r"mouvement moderne", r"moderniste", r"fonctionnalis[mt]e"],
}
KEYWORDS_COMPILED = {s: [re.compile(p, re.I) for p in pats] for s, pats in KEYWORDS.items()}

# Architects with no MH track record but well documented as postmodern figures —
# researched via web search (see acr/README.md), not guessed.
KNOWN_POSTMODERN_ARCHITECTS = {
    "bofill ricardo", "portzamparc christian de", "de portzamparc christian",
    "portzamparc christian",
}


def text_blob(place):
    return " ".join(filter(None, [place.get("nom_officiel"), place.get("historique")])).lower()


def architect_names(place):
    if not place.get("architecte"):
        return []
    return [n.strip().lower() for n in place["architecte"].split(",") if n.strip()]


def classify(place, priors):
    """Returns (styles_list, confidence, reason) — confidence in {"high","medium","low"}."""
    names = architect_names(place)
    blob = text_blob(place)

    # Signal A: known postmodern architect (explicit list, since priors from the MH
    # set can't know about a style the MH taxonomy didn't have).
    for n in names:
        if n in KNOWN_POSTMODERN_ARCHITECTS:
            return (["Post-modernisme"], "high", f"architecte {n} (postmoderne connu)")

    # Signal B: architect already classified in the MH set — strongest signal, since
    # it's grounded in Paul's own prior curation rather than a guess.
    arch_votes = Counter()
    matched_names = []
    for n in names:
        if n in priors:
            arch_votes.update(priors[n])
            matched_names.append(n)
    if arch_votes:
        top_style, top_count = arch_votes.most_common(1)[0]
        total = sum(arch_votes.values())
        # only trust it if that style is a clear majority of that architect's MH credits
        if top_count / total >= 0.7:
            return ([top_style], "high", f"architecte {matched_names} -> {dict(arch_votes)}")
        return ([top_style], "medium", f"architecte {matched_names} ambigu -> {dict(arch_votes)}")

    # Signal C: unambiguous keyword hit(s) in the text.
    style_hits = []
    for s, pats in KEYWORDS_COMPILED.items():
        if any(p.search(blob) for p in pats):
            style_hits.append(s)
    if len(style_hits) == 1:
        return (style_hits, "medium", f"mot-clé -> {style_hits[0]}")
    if len(style_hits) > 1:
        return (style_hits, "low", f"mots-clés multiples -> {style_hits}")

    return ([], "none", "aucun signal")


def main():
    priors = build_architect_priors()
    places = json.load(open(ACR_PATH, encoding="utf-8"))

    counts = Counter()
    review_buckets = defaultdict(list)

    for p in places:
        styles, confidence, reason = classify(p, priors)
        counts[confidence] += 1
        if confidence == "high":
            p["styles"] = styles
        else:
            # leave styles empty in the data file; queue for manual review instead of
            # guessing — a wrong style is worse than a place that's simply not on the
            # map yet.
            review_buckets[confidence].append((p, styles, reason))

    json.dump(places, open(ACR_PATH, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ": "))

    with open(HERE / "classify_review.md", "w", encoding="utf-8") as f:
        f.write("# Classification ACR — lieux à revoir manuellement\n\n")
        f.write(f"Classifiés automatiquement (confiance haute) : {counts['high']}\n\n")
        f.write(f"À revoir : {counts['medium'] + counts['low'] + counts['none']} "
                f"(medium={counts['medium']}, low={counts['low']}, none={counts['none']})\n\n")
        for conf in ["medium", "low", "none"]:
            f.write(f"\n## Confiance : {conf} ({len(review_buckets[conf])})\n\n")
            for p, styles, reason in review_buckets[conf]:
                f.write(f"- `{p['ref']}` **{p['nom_officiel']}** — {p.get('commune')} "
                        f"({p.get('annee')}) — {p.get('architecte')}\n")
                f.write(f"  - piste : {styles} — {reason}\n")

    print("Confiance:", dict(counts))
    print(f"data-acr.json mis à jour ({counts['high']} lieux classés).")
    print(f"classify_review.md écrit ({sum(counts.values()) - counts['high']} lieux à revoir).")


if __name__ == "__main__":
    main()
