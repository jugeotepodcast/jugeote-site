# Consignes pour Claude sur ce dépôt

Site statique de www.jugeote.fr (podcast Jugeote, propriétaire : David). Publié par GitHub Pages via `.github/workflows/deploy.yml`.

- Construire et vérifier : `python3 build.py`, puis ouvrir `_site/`. Aucune dépendance, ne pas en ajouter.
- Pages dans `pages/`, données dans `data/`, styles dans `css/style.css` (une seule feuille). `_site/` n'est jamais versionné.
- Dépôt public : jamais de donnée confidentielle.
- Textes en français, vouvoiement du lecteur. Style de David : pas de tiret long, pas de point-virgule, pas de tournure « ce n'est pas X, c'est Y », phrases courtes, chiffres et noms précis, pas d'autorité floue.
- Ne rien inventer sur David ni sur les invités : laisser un emplacement `[À COMPLÉTER]` et le signaler.
- Charte : bleu #21066f, violet #bf70f6, jaune #ffe57d, police Jost (titres) et Inter (texte), hébergées dans `assets/fonts/`. Aucun appel à Google Fonts ni traceur.
