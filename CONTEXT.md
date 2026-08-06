# Contexte du projet — à lire avant toute modification

Ce document résume l'historique complet des décisions de design/produit prises pendant la conception de cette app avec Claude (Cowork). Il existe pour qu'un futur agent (Claude Code ou autre) — ou moi-même dans une session future — comprenne immédiatement de quoi Paul parle quand il fait référence à "avant", "comme avant les accordéons", "l'effet Rains", etc., sans avoir à redécouvrir ces choix par essai-erreur.

**Règle d'or : si un point ci-dessous dit qu'une idée a été essayée puis annulée, ne pas la réintroduire sans que Paul le redemande explicitement.**

## Qu'est-ce que cette app

Carte interactive publique du patrimoine architectural français méconnu : mouvement moderne, brutalisme, Art Déco, architecture industrielle et rationaliste. 241 lieux réels, données officielles Mérimée/POP (Ministère de la Culture) — y compris un champ `historique` avec du texte curatorial officiel sourcé (jamais inventé). Public : grand public curieux, pas des experts. Ton éditorial/culturel, pas touristique-kitsch.

Site 100% statique, aucun backend, aucune dépendance à installer. `index.html` (structure/style/logique) + `data.json` (les 241 lieux), chargé via `fetch()`.

## Historique chronologique des décisions

### Fondations (round 1)
- Palette "Rains-inspirée" v1 (chaude, terracotta) : encre `#2b2a27`, papier crème `#faf7f2`, accent terracotta `#b3552f`. **Cette palette a depuis été entièrement remplacée par une palette noir/blanc/gris — voir plus bas.**
- Fond de carte CartoDB Positron (clair, minimal). Marqueurs colorés par style avec icône thématique (grille de fenêtres = mouvement moderne, masse à degrés = brutalisme, éventail = Art Déco, engrenage = industriel).
- Contrôles Leaflet traduits en français (zoom, attribution).

### Fiches lieu (rounds successifs)
- Hiérarchisation : accroche d'abord (nom, style, statut MH), détails ensuite.
- Noms d'architectes reformatés "Prénom Nom" (la base Mérimée stocke "Nom Prénom") via une heuristique qui évite de casser les noms d'institutions, de duos ("X et Y"), de particules ("de", "van"…) et de pseudonymes (Le Corbusier).
- Statut MH : le libellé complet ("Classé Monument Historique" / "Inscrit Monument Historique") est affiché à côté d'un bouton "i" qui ouvre une info-bulle explicative — **décision volontaire** : le mot complet donne envie de cliquer sur le "i", contrairement à l'abréviation "MH".
- CTA de fiche : Google Maps toujours en premier/primaire (libellé sans mention "Street View" car pas toujours disponible), lien POP relabellisé en langage clair ("Voir la fiche officielle" plutôt que "POP").
- Genre affiché en texte simple (`dp-value`), sans bulle/pill — aligné visuellement sur le style d'Époque, pour rester homogène.
- Champ **"Histoire"** (anciennement appelé "Intérêt" — renommé sur demande) : sous Architecte(s), extrait sourcé du champ `historique` officiel Mérimée, tronqué à 220 caractères avec bouton "Lire la suite" si plus long, **absent** si la base n'a pas de texte pour ce lieu (jamais de contenu inventé — vérifié : 235/241 lieux ont un historique renseigné, 6 nuls gérés proprement).
- **Structure de la fiche : essayé puis annulé un système de "cartes" séparées empilées** (une carte par section, façon vignettes Rains) — Paul a explicitely demandé de revenir à **un seul bloc continu** avec des sections séparées par de simples lignes de séparation (`dp-row` / `border-bottom`), pas des cartes distinctes.
- **Essayé puis annulé un système d'accordéon** (titres de section cliquables avec icône +/-, replié par défaut sauf Architecte(s)) inspiré de la page produit détaillée de Rains (Description/Livraison/Guide des tailles). Paul a demandé de tout remettre ouvert en permanence et de revenir à la structure plate d'origine (labels `Architecte(s)` / `Genre` / `Époque` / `Protection` / `Accès / propriété`), car l'accordéon créait un doublon de titres. **Ne pas réintroduire l'accordéon sans demande explicite.**
- Les labels de champ (`dp-label`) sont volontairement **gras et en capitales, en encre pleine** (`font-weight:800`, `color:var(--ink)`, pas `--ink-soft`) — plus appuyés que la version initiale, sur demande explicite de Paul ("un peu plus bold").

### Filtres
- Un seul bouton "Filtres" (icône sliders) ouvrant un panneau unique avec toutes les catégories (Style, Genre, Année, Propriété) — **remplace un design antérieur à 4 pills séparées** (Style/Genre/Année/Propriété côte à côte), jugé encombrant sur mobile.
- Multisélection par cases à cocher, deux CTA sticky en bas ("Réinitialiser" / "Voir les résultats"), grisés tant qu'aucun filtre n'est actif.
- En-tête du panneau : uniquement une croix de fermeture (une flèche retour avait été ajoutée puis retirée — jugée redondante).
- Filtre "Propriété" (publique/privée/non renseignée) avec note explicative sur la fiabilité de la visite.

### Mobile
- Le menu burger / la liste latérale sur mobile ont été **retirés entièrement** — sur mobile, la carte + les fiches au clic suffisent, pas besoin d'un listing dédié.
- **Remplacé le 2026-08-05, deux fois de suite** (essayé puis annulé) : une première version
  a copié une bottom sheet façon Google Maps (deux hauteurs, poignée à glisser) — rejetée par
  Paul après une vidéo de référence Google Maps montrant que ce n'était pas fidèle. Une deuxième
  tentative a corrigé l'ordre du contenu pour coller à cette vidéo — également rejetée : Paul a
  alors envoyé deux captures d'une autre app (fiche "Sancerre") et demandé explicitement de
  revenir au design de fiche d'origine, précédé d'une étape plus légère. **Ne pas réintroduire
  une bottom sheet à glisser/redimensionner sans demande explicite — les deux tentatives ont été
  essayées et jugées éloignées de ce que Paul voulait.**
  Design retenu (mobile uniquement, desktop inchangé — toujours le panneau latéral d'origine) :
  deux états discrets, pas de geste de drag :
  - **Mini-carte flottante** (état par défaut à l'ouverture) : juste la photo, le nom, et un
    bouton "En savoir plus" — une carte avec marge sur les 4 côtés (façon résultat de recherche
    Google Maps), pas une sheet plein-largeur collée au bord. Marge très fine entre la photo et
    le contour de la carte. Le CTA est volontairement discret (pilule grise, pas noire pleine,
    pas pleine largeur) pour ne pas concurrencer visuellement le titre.
  - **Fiche complète** ("full"), ouverte en tapant la mini-carte : reprend exactement le design
    de fiche d'origine (photo en premier, bloc continu, mêmes labels), plein écran sous le
    header, avec une flèche de retour (←) qui ramène à la mini-carte sans désélectionner le lieu
    (le pin reste actif, la position de la carte ne bouge pas).
  - Se balader sur la carte (drag ou tap simple) **ne ferme plus** la mini-carte — seul le ✕ (qui
    désélectionne complètement) ou le choix d'un autre pin (qui swap juste le contenu) la ferme/
    change. Avant le 2026-08-05, un tap/drag sur la carte fermait la fiche ; **changé sur
    demande explicite de Paul** ("se balader sur la carte ne ferme pas l'aperçu").
  - Dans l'état "full", la recherche et le bandeau du bas disparaissent (couverts par la fiche
    plein écran, en z-index, pas de règle CSS dédiée) — seul le logo en haut reste visible.
    "Autour de moi" (voir plus bas) reste lui accessible en permanence.
  - Au scroll dans la fiche "full", une fois le `<h2>` du titre sorti du cadre, une barre sticky
    apparaît avec le nom du lieu + la flèche de retour, pour garder l'orientation/navigation
    accessible sans remonter tout en haut.
  - Cliquer sur un autre pin pendant qu'une fiche est déjà ouverte swap juste le contenu et
    **garde le même état** (mini ou full) — jamais de reset auto. Fermer (✕ ou tap sur la carte
    en dehors) remet à zéro : la prochaine fiche ouverte redémarre en mini-carte.
  - Le zoom de la carte ne change **jamais** en ouvrant/changeant/fermant une fiche — seul le
    panoramique (pan) recentre le point sélectionné dans la zone de carte encore visible. C'était
    cassé avant (un `Math.max(zoom, 14)` forçait un zoom avant sur les vues très dézoomées).
- **Barre de navigation flottante en bas (2026-08-07)**, remplace l'ancienne pastille "Filtres"
  seule en haut à gauche — même verre translucide que le reste, 4 icônes façon Instagram (pas de
  texte) : **Filtres** (ouvre le même panneau qu'avant, juste déplacé), **Carte** (ferme tout —
  filtres/recherche/fiche — retour à une carte propre), **Recherche** (loupe : ouvre la barre de
  recherche, qui flotte au-dessus de la barre nav plutôt que dans le header), **Annuaire** (futur
  répertoire d'architectes, pas encore construit — affiche juste un toast "bientôt disponible"
  pour l'instant, **ne pas construire une vraie page sans qu'on le redemande explicitement**).
  - **Contrairement à l'ancienne pastille Filtres, cette barre reste visible quand la mini-carte
    est ouverte** — changement demandé explicitement par Paul. La mini-carte flotte au-dessus
    avec un petit espace (`--bar-clearance`, ~8px de marge), elle ne la recouvre plus.
  - "Autour de moi" est sorti du header : c'est maintenant une icône ronde flottante seule, en
    haut à droite, permanente (contrairement à avant, elle ne se cache plus dans la fiche "full").
  - **Piège CSS rencontré et à connaître** : `backdrop-filter` sur un ancêtre crée un nouveau
    containing block pour ses descendants `position:fixed` — le header (`backdrop-filter` déjà
    présent avant ce round) et la nouvelle barre du bas cassaient donc le positionnement fixed de
    leurs enfants (recherche, localisation, panneau filtres) une fois ceux-ci passés en
    `position:fixed` pour flotter indépendamment. Fixé en déplaçant le `background`+
    `backdrop-filter` sur un pseudo-élément `::before` (`position:absolute;inset:0;z-index:-1`)
    plutôt que sur l'élément lui-même — le verre reste identique visuellement, mais l'élément réel
    ne crée plus ce containing block. **Si un futur élément flottant (position:fixed) mal
    positionné apparaît sur mobile, vérifier en premier si un ancêtre a un `backdrop-filter` ou
    `filter` direct — c'est très probablement la cause.**

### Refonte visuelle "Rains" (dernier gros round)
Paul a fourni deux captures d'écran puis une vidéo de Rains.com (site e-commerce) comme référence directe. Éléments retenus :
- **Verre translucide** : tous les éléments flottants (bandeau/header, liste latérale, panneau de filtres, fiche lieu, pills, contrôle de zoom) partagent exactement la même recette CSS — actuellement `background: rgba(230,230,227,.52)` + `backdrop-filter: blur(12-14px) saturate(1.35)`.
  - Historique de tâtonnement avant la bonne recette : opacité baissée progressivement (.88 → .66 → .55 → .42 → .35) en pensant que "l'effet Rains" venait de plus de transparence, puis blur monté (46-50px → 66-70px) en pensant qu'il venait de plus de flou. **Les deux pistes étaient fausses.**
  - **La vraie recette a été trouvée en inspectant le CSS calculé réel de rains.com (pas une capture d'écran)** : leurs pills de nav/header utilisent `rgba(227,227,227,.52)` + `blur(8-12px)` seulement — un flou très léger, pas un flou poussé à fond. Leur variante sombre (bouton "Sign up") : `rgba(16,16,15,.8)` + `blur(12px)`.
  - **Enseignement clé** : l'effet "verre net" de Rains ne vient PAS d'un flou fort qui transforme le fond en simple tache de couleur. Il vient d'un flou léger (8-14px) qui laisse deviner de vraies formes/textures derrière (routes, labels de la carte chez nous), combiné à une teinte gris chaud (`rgb(230,230,227)`, pas blanc pur `255,255,255`) et un fort contraste texte/fond. **Si Paul redemande "plus/moins flouté" ou "plus/moins transparent" sur ces éléments, ajuster depuis cette base (12-14px / .52) par petits pas (ex. 10px ou 16px ; .45 ou .58) plutôt que de repartir vers les valeurs extrêmes essayées précédemment (66px+ de blur, ou .30- d'opacité) — ces pistes ont été essayées et jugées trop éloignées de l'effet recherché.**
- **Palette noir/blanc/gris** : toute la palette UI (texte, boutons, bordures, hover states) est passée du terracotta chaud à un système encre/gris neutre (`--ink:#141414`, `--ink-soft:#6e6e6e`, `--panel:#ececea`, `--accent:#141414` — l'accent EST le noir, pas une couleur). **Exception assumée** : les pins de la carte gardent leurs couleurs d'origine par style (bleu-gris moderne, gris chaud brutalisme, or Art Déco, olive industriel) — Paul l'a explicitement autorisé ("tu peux mettre de la couleur sur les icônes de lieu quand même"), et un vert discret reste pour le badge "lieu visitable" (même logique que le point vert "disponible en magasin" chez Rains). Le ton "probablement pas visitable" est passé de orange/brun à gris neutre.
- Titres de nav (bouton Filtres, "Autour de moi", placeholder de recherche, CTA) en **capitales**, inspiré de la nav Rains ("NEW IN", "FEMME", etc.).
- **Nom de l'app changé en "archi.cool"** — logotype en minuscules grasses avec un point entre "archi" et "cool". Essayé un point carré, puis Paul a demandé un point rond, plus gros, centré verticalement. Sur mobile, le logo est centré horizontalement en haut et agrandi (24px).

### État actuel (résumé)
- Palette : noir/blanc/gris partout sauf pins de carte (couleur) et badge "visitable" (vert).
- Toutes les surfaces flottantes : même recette de verre translucide, calquée sur le CSS réel de Rains (`rgba(230,230,227,.52)` / `12-14px` blur).
- Fiche lieu : bloc unique continu, sections séparées par des lignes fines, labels gras capitales encre pleine, **pas d'accordéon**, tout toujours visible.
- Logo : "archi·cool" minuscule gras, point rond, centré+agrandi sur mobile.

## Style de collaboration avec Paul

- Freelance PM non-technique. Préfère qu'on lui montre plutôt qu'on lui demande de choisir dans l'abstrait (screenshots, vidéos de référence).
- Itère par petites touches successives — il dit souvent "un peu plus X" ou "rends ça plus Y" : interpréter comme un ajustement incrémental de ce qui existe, pas une refonte.
- Quand il dit "comme avant" ou fait référence à une session précédente, **consulter ce document en premier** plutôt que de deviner.
- Aime les références de marques/sites existants (Rains.com) comme raccourci pour communiquer une direction visuelle — utile de proposer de vraies captures/vidéos si le prochain agent a besoin de clarifier une direction similaire.
