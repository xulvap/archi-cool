# Base « Architecture contemporaine remarquable » (ACR)

Prépare la prochaine base de lieux pour archi.cool, en plus des 241 Monuments
Historiques actuels — **base séparée pour l'instant, à fusionner dans `data.json`
une fois travaillée proprement** (décision explicite de Paul, 2026-08-04).

## Source

Label « Architecture contemporaine remarquable » (ACR, ex-« Label XXe »),
Ministère de la Culture — la même famille de données Mérimée que la liste des
Monuments Historiques, mais pour des édifices **non protégés au titre des MH**
(complémentaire, pas de doublon possible).

- Jeu de données : https://www.data.gouv.fr/datasets/liste-des-edifices-labellises-architecture-contemporaine-remarquable-acr
- CSV (mis à jour chaque semaine) : `https://www.data.gouv.fr/api/1/datasets/r/80b6ac20-41b1-400c-8860-af201ff7dcb6`
- **1824 lieux** au total, France entière. Grosse majorité 20e siècle (pic
  1950-1970), aligné avec le sujet du site.

## Comment régénérer

```bash
python3 acr/build.py
```

Télécharge le CSV source à jour et régénère `acr/data-acr.json`. Le CSV brut
(`acr/acr-source.csv`, ~6 Mo) n'est pas versionné — seul le JSON transformé l'est.

## Ce qui est déjà fait (transform mécanique)

Mêmes noms de champs que `data.json` : `ref, nom, nom_officiel, architecte,
commune, dept, region, protection, statut, siecle, annee, decennie, lat, lon,
precision_coord, domaine, styles, proprietaire, proprietaire_detail, lien_pop,
lien_source, historique, image, adresse, code_postal, visite_statut`.

- `architecte` : rôles entre parenthèses retirés ("Dikansky Georges
  (architecte)" → "Dikansky Georges"), ordre Nom Prénom conservé — le
  `formatArchitecte()` déjà dans `index.html` s'en occupe à l'affichage, comme
  pour le jeu de données MH.
- `protection`/`statut` : nouveau libellé "labellisé ACR" — **`statutBadge()`
  dans `index.html` ne connaît que "classé MH"/"inscrit MH" pour l'instant, il
  faudra l'étendre au moment de la fusion.**
- `lien_pop` : même schéma d'URL POP que les notices Mérimée, vérifié
  fonctionnel sur des refs ACR.
- Aucun chevauchement de `ref` avec `data.json` (vérifié).

## Ce qui reste à faire avant fusion (le vrai travail)

1. **`styles` (le plus gros chantier)** — vide partout pour l'instant. La
   source n'a aucun champ de style ; comme pour les 241 lieux actuels, chaque
   bâtiment doit être classé dans Modernisme / Brutalisme / Art Déco /
   Industriel et rationaliste (un ou deux styles) à partir de la description,
   de l'architecte et de la date — jugement éditorial, pas mécanisable
   simplement. À faire par lots plutôt que d'un coup vu le volume (1824 vs 241).
2. **`nom`** — copie brute de `nom_officiel` pour l'instant. Dans `data.json`,
   `nom` est souvent une version raccourcie/désambiguïsée à la main (ex.
   `PA33000142` : nom officiel "Maison de type gratte-ciel" → nom affiché
   "Maison, 14 rue Le Corbusier"). Pas encore fait ici.
3. **Coordonnées manquantes** — 248 lieux (14 %) sans lat/lon dans la source
   (`precision_coord: "manquant"`). Il faudra les géocoder (adresse + commune)
   avant qu'ils puissent apparaître sur la carte.
4. **Photos** — aucune. Même logique que `photos-a-faire.xlsx` à reprendre une
   fois la sélection de lieux arrêtée (inutile de chercher des photos pour des
   lieux qui seront filtrés hors-sujet).
5. **`visite_statut`** — non renseigné, comme pour la majorité du jeu MH à
   l'origine ; recherche au cas par cas plus tard.
6. **`code_postal`** — absent de la source (le CSV n'a que le code INSEE
   commune, différent du code postal). À enrichir si besoin.
7. **Filtrage de pertinence** — 1824 lieux, c'est large : ça inclut par ex. de
   l'urbanisme/aménagement (lotissements, secteurs urbains) et pas seulement
   des bâtiments isolés. Une passe de tri (garder seulement ce qui correspond
   vraiment aux 4 styles du site) sera nécessaire avant la fusion — probable
   que la classification de style (point 1) fasse ce tri naturellement (pas
   classable = hors-sujet).

## Statut

Squelette de données prêt (1824 entrées, champs mécaniques peuplés). Rien
n'est encore branché sur `index.html`/la carte — c'est volontaire, à la
demande de Paul.
