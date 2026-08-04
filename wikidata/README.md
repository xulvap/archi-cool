# Base Wikidata

Une 3e base candidate pour archi.cool, en plus de `data.json` (241 lieux MH)
et `acr/data-acr.json` (1824 lieux ACR) — **base séparée pour l'instant**,
même logique que ACR : on prépare, on fusionnera plus tard.

## Pourquoi Wikidata

Contrairement à ACR, le style n'est pas à deviner ici : c'est une vraie
propriété Wikidata (**P149**, "style architectural"), donc chaque lieu
récupéré arrive déjà avec le bon style attaché. C'était le vrai goulot
d'étranglement sur ACR (seulement ~23 % des 1824 lieux classés après une
passe complète). Le compromis : Wikidata n'a que quelques centaines de
lieux tagués par catégorie en France — beaucoup moins de volume que ACR,
mais un taux de classification proche de 100 % au lieu de 23 %.

Autre avantage : la propriété "identifiant Mérimée" (**P380**) utilise
exactement les mêmes codes "PA" que `data.json`, donc le dédoublonnage avec
le site existant est fiable (comparaison directe de références, pas de
matching approximatif par nom/commune).

## Comment régénérer

```bash
python3 wikidata/build.py
```

Interroge le point d'accès public Wikidata Query Service (SPARQL) à chaque
lancement — pas de fichier source à télécharger séparément. Repose sur
l'API publique partagée : peut être lent ou temporairement bloqué (429) si
sollicité trop souvent, le script réessaie automatiquement.

## Ce qui est déjà fait

1824 → non, **432 lieux** au total (390 nouveaux + 42 déjà sur le site,
détectés via l'identifiant Mérimée P380 et exclus de la comparaison finale
mais gardés dans le fichier avec `deja_sur_le_site: true` pour référence) :

- **4 styles directement fiables** (le champ P149 de Wikidata, pas une
  déduction) : Modernisme (174 nouveaux), Art Déco (72), Brutalisme (28),
  Post-modernisme (14).
- **Industriel et rationaliste : plus fragile.** Wikidata n'a presque pas
  de tag de *style* "architecture industrielle" (3 résultats seulement) —
  on a donc pris un proxy par *type* de bâtiment ("usine", 1019 résultats
  bruts en France), mais ça va du moulin médiéval à l'usine de 2020, aucun
  rapport avec le style recherché. Filtré aux seules usines datées
  1880-1990 (126 gardées, 106 nouvelles) — un moulin à eau du XVIIe n'a
  clairement rien à faire dans "Industriel et rationaliste", mais même
  1880-1990 reste une présomption de date, pas une confirmation de style :
  **cette catégorie mériterait une relecture manuelle, contrairement aux
  4 autres qui sont fiables telles quelles.**
- Chevauchement avec ACR : seulement 3 lieux en commun (par nom+commune) —
  les deux bases sont largement complémentaires, pas redondantes.
- **269 lieux ont une photo Wikimedia Commons** déjà liée (`wikidata_image_url`)
  — mais ce sont de vraies photographies, pas le style ligne blanche/
  transparente du site. Même traitement que pour ACR : à rester en dehors
  du champ `image` tant que ce n'est pas passé par une étape d'illustration
  (voir la mésaventure de la tentative "télécharger les photos" — abandonnée
  faute d'automatisable proprement). `wikidata_image_url` sert juste de
  pense-bête pour une future passe photo, ce n'est **pas** un champ du
  schéma partagé avec `data.json` — à retirer avant fusion.
- `deja_sur_le_site` : idem, champ de travail à retirer avant fusion.

## Ce qui manque avant fusion

1. **`dept` / `region`** — vides pour l'instant. Wikidata a l'info (chaîne
   de propriétés P131 : commune → département → région) mais ça demande une
   requête supplémentaire par lieu ou une jointure plus complexe ; pas fait
   encore.
2. **`nom`** — copie brute du label Wikidata, pas encore la version
   raccourcie/désambiguïsée à la main comme sur `data.json`.
3. **`historique`, `domaine`, `adresse`, `code_postal`, `proprietaire`,
   `visite_statut`** — vides, mêmes manques que sur ACR au même stade.
4. **Industriel et rationaliste à revérifier** (voir plus haut) — c'est la
   seule des 5 catégories qui n'est pas directement fiable telle quelle.
5. **Photos** — 269 lieux ont une vraie photo de référence disponible
   (`wikidata_image_url`), ce qui devrait accélérer une future passe
   d'illustration par rapport à ACR où il fallait tout chercher à la main.

## Statut

432 lieux (390 nouveaux), 4 styles sur 5 directement fiables (P149 natif),
1 à revérifier (Industriel et rationaliste, proxy par type de bâtiment).
Rien n'est branché sur `index.html`/la carte.
