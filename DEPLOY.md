# Procédure de déploiement — CineFlow

## Remotes configurés

| Remote  | URL                                                  | Usage                     |
|---------|------------------------------------------------------|---------------------------|
| origin  | https://github.com/chniang/cineflow.git              | Code source complet       |
| hf      | https://huggingface.co/spaces/TIJAANI/cineflow       | Space Streamlit (prod)    |

---

## Push GitHub (normal)

```bash
git push origin main
```

Images trackées, README intact, historique complet.

---

## Push Hugging Face

HF rejette les fichiers binaires (PNG) dans le pack git.
`images/` contient uniquement des screenshots du README — inutile au runtime Streamlit.
La branche `hf-deploy` est une branche **orpheline** (root-commit `9febf14`) :
aucun historique, aucun blob PNG dans le pack.

### Premier push (déjà fait)

```bash
git checkout --orphan hf-deploy
git rm -rf .
git checkout main -- app_complete.py style.css requirements.txt \
    init_db.py tidiane_flix.db tidiane_flix.sql .streamlit/ Dockerfile \
    .gitignore README.md
git commit -m "chore(hf): deploy"
git push hf hf-deploy:main --force
git checkout main
```

### Mettre à jour HF après des commits sur main

```bash
git checkout hf-deploy

# Récupérer les fichiers app modifiés depuis main (sans images/)
git checkout main -- app_complete.py style.css requirements.txt \
    init_db.py tidiane_flix.db .streamlit/ Dockerfile .gitignore README.md

git add .
git commit -m "chore(hf): sync from main $(git rev-parse --short main)"
git push hf hf-deploy:main
git checkout main
```

> `--force` n'est nécessaire que si l'historique HF diverge.
> Pour les mises à jour courantes, un push simple suffit.

---

## Avertissement HF (non bloquant)

Le push affiche un warning jaune :
```
Warning: empty or missing yaml metadata in repo card
```
C'est parce que le README.md n'a pas de bloc YAML frontmatter HF.
L'app tourne normalement. Pour le supprimer, ajouter en tête du README :
```yaml
---
title: CineFlow
emoji: 🎬
colorFrom: red
colorTo: black
sdk: streamlit
sdk_version: "1.28"
app_file: app_complete.py
pinned: false
---
```
