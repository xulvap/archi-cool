# archi.cool

Carte interactive du patrimoine architectural français méconnu — mouvement moderne, brutalisme, Art Déco, architecture industrielle et rationaliste. 256 lieux protégés (Monuments Historiques), données officielles Mérimée/POP (Ministère de la Culture).

**Avant toute modification, lire [`CONTEXT.md`](./CONTEXT.md)** — historique des décisions de design/produit, y compris ce qui a été essayé puis explicitement annulé (à ne pas réintroduire sans demande explicite).

## Structure

- `index.html` — l'application (HTML/CSS/JS, carte Leaflet). Aucune dépendance à installer, aucun build : un site statique pur.
- `data.json` — les 256 lieux (nom, architecte, commune, statut de protection, style, genre, époque, historique sourcé, etc.), chargé au démarrage via `fetch('./data.json')`.

## Développement local

Ouvrir `index.html` directement dans un navigateur ne fonctionnera pas pour le chargement des données (les navigateurs bloquent `fetch()` sur les fichiers locaux `file://`). Servir le dossier avec un petit serveur local, par exemple :

```bash
npx serve .
# ou
python3 -m http.server 8000
```

Puis ouvrir `http://localhost:8000` (ou le port indiqué).

## Déploiement

Site 100 % statique — aucune configuration nécessaire côté Vercel. Il suffit d'importer le dépôt GitHub dans Vercel ; le déploiement se fait automatiquement (pas de build command, pas de framework à détecter, "Other" convient).

## Source des données

[data.gouv.fr — Liste des immeubles protégés au titre des Monuments Historiques](https://data.culture.gouv.fr/explore/dataset/liste-des-immeubles-proteges-au-titre-des-monuments-historiques/)
