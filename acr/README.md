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

## Classification des styles — en cours

**5e style ajouté : "Post-modernisme"** (décision prise le 2026-08-04, à
valider avec Paul). La taxonomie à 4 styles a été construite pour les 241 MH,
dont le plus tardif date de 1991 et reste stylistiquement "moderniste" au
sens large (Niemeyer, Le Corbusier tardif). L'ACR va beaucoup plus loin dans
le temps (177 lieux entre 1980 et 2020, ~10 % du jeu) et couvre une vraie
rupture esthétique documentée — réaction historicisante/ludique/colorée au
mouvement moderne, ~1975-1995, figures de proue Ricardo Bofill (Les Espaces
d'Abraxas, Noisy-le-Grand 1982 ; les Arcades du Lac, Saint-Quentin-en-Yvelines
1982) et Christian de Portzamparc en France. Sans ce 5e style, chaque bâtiment
postmoderne de l'ACR serait soit classé "Modernisme" à tort, soit laissé de
côté par défaut. Voir `classify_styles.py` pour les critères de détection.

**Cas limites rencontrés, à trancher avec Paul** (pas classés pour l'instant) :
- **Jean Nouvel** (Palais des Congrès de Tours, 1989-93 ; Maison Dick, 1975) —
  très daté "postmoderne" par la période, mais son vocabulaire est plus
  "high-tech critique" que le postmodernisme historicisant de Bofill. Rentre
  mal dans la définition retenue ci-dessus.
- **Claude Vasconi** (Hôtel de ville, Bourges 1983-92) — même famille de
  génération que Bofill mais idiome différent (verre/métal monumental plutôt
  qu'historicisant).
- **Andrault & Parat** ("immeubles à gradins" GR1/GR2, Dreux 1977) — duo connu
  pour ses ensembles de logements en gradins/ziggourats, entre Brutalisme
  sculptural et esthétique proche de Bofill. Ambigu entre les deux.
- **Pascal Häusermann** ("architecture bulle"/organique, ex. Maison Pasquini
  1967) — un mouvement à part entière (habitat "bulle", coques en béton
  projeté, avec Antti Lovag), qui ne rentre dans aucun des 5 styles actuels.
  À voir si ça vaut un 6e style si plusieurs autres lieux de ce type
  apparaissent dans le reste du jeu.

## Ce qui reste à faire avant fusion (le vrai travail)

1. **`styles` (le plus gros chantier, en cours)** — méthode : un script
   (`acr/classify_styles.py`) classe automatiquement les cas à signal fort
   (architecte déjà classé dans `data.json`, vocabulaire explicite type "art
   déco"/"brutaliste" dans la notice) ; le reste passe par une relecture
   manuelle lieu par lieu (architecte, date, description, parfois recherche
   web ponctuelle pour des architectes/mouvements spécifiques — pas une
   recherche par lieu, ingérable à ce volume). État au 2026-08-04 : **318/1824
   classés**, 239 hors-sujet (urbanisme/aménagement, pas des bâtiments), ~1267
   encore à relire. Ce n'est pas mécanisable à 100 % — un mauvais style est
   pire qu'un lieu pas encore sur la carte, donc on laisse `styles: []` plutôt
   que deviner quand le signal est faible.
   Règle sur les nouveaux styles (Paul, 2026-08-04) : on peut en créer, mais
   pas trop — un cas qui ne rentre dans aucun des 5 actuels est mis de côté
   dans `edge_cases.md` (pas classé, pas hors-sujet) plutôt que de créer un
   style à la première occurrence ; on tranche seulement si un vrai groupe se
   dégage, à la fin plutôt qu'au fil de l'eau.
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

Squelette de données prêt (1824 entrées, champs mécaniques peuplés).
Classification des styles en cours (318/1824, voir ci-dessus). Rien n'est
encore branché sur `index.html`/la carte — c'est volontaire, à la demande de
Paul.
