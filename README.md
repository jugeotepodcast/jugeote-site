# jugeote-site

Le site www.jugeote.fr. Il est publié automatiquement par GitHub Pages à chaque modification.

## Modifier un texte

1. Ouvre le fichier de la page dans le dossier `pages/` :
   - `index.html` : accueil
   - `episodes.html` : liste de tous les épisodes
   - `top-voice.html` : page Top Voice
   - `a-propos.html` : à propos et contact
   - `mentions-legales.html` : mentions légales
   - `_entete.html` et `_pied.html` : menu et bas de page, communs à toutes les pages
2. Clique sur le crayon, modifie le texte entre les balises, puis clique sur **Commit changes**.
3. Le site est à jour en 1 à 2 minutes (suivi dans l'onglet **Actions**).

Le bloc en haut de chaque page (`TITRE`, `DESCRIPTION`) donne le titre de l'onglet et le résumé affiché par Google.

## Ajouter un Top Voice

Dans `data/top-voice.json`, ajoute un bloc dans `membres` :

```json
{
  "nom": "Prénom Nom",
  "categorie": "CIF indépendant",
  "description": "Une phrase sur son approche et ses clients types.",
  "episode": "https://lien-vers-son-episode",
  "site": "https://son-site.fr",
  "actif_jusqu_a": "novembre 2027",
  "photo": "prenom-nom.jpg"
}
```

`categorie` vaut exactement `Coach financier`, `CGP` ou `CIF indépendant`. `actif_jusqu_a` affiche « Partenaire actif jusqu'en … » sur sa fiche. La photo est facultative : dépose-la dans `assets/top-voice/`. Sans photo, ses initiales s'affichent.

## Les épisodes

Ils sont lus automatiquement dans le flux RSS Podcastics, à chaque publication et chaque matin à 7h. Rien à faire. Pour forcer une mise à jour : onglet **Actions**, **Publier le site**, **Run workflow**.

## Ne jamais mettre ici

Ce dépôt est public. Aucun mot de passe, tarif négocié, coordonnée privée ni note interne.
