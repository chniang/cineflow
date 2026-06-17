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
    .gitignore
# README.md NON copié depuis main — créer manuellement avec le bloc YAML ci-dessous
git commit -m "chore(hf): deploy"
git push hf hf-deploy:main --force
git checkout main
```

### Mettre à jour HF après des commits sur main

```bash
git checkout hf-deploy

# README.md exclu : il reste fixe sur hf-deploy pour préserver le bloc YAML HF.
# Le copier depuis main écraserait le frontmatter et provoquerait "Configuration error".
git checkout main -- app_complete.py style.css requirements.txt \
    init_db.py tidiane_flix.db .streamlit/ Dockerfile .gitignore

git add .
git commit -m "chore(hf): sync from main $(git rev-parse --short main)"
git push hf hf-deploy:main
git checkout main
```

> `--force` n'est nécessaire que si l'historique HF diverge.
> Pour les mises à jour courantes, un push simple suffit.

---

## YAML frontmatter HF (déjà appliqué sur hf-deploy)

Le fichier `README.md` sur `hf-deploy` commence par ce bloc — ne pas l'écraser :

```yaml
---
title: CineFlow
emoji: 🎬
colorFrom: red
colorTo: purple
sdk: docker
pinned: false
---
```

`sdk: docker` car le projet utilise un Dockerfile (pas le runner Streamlit natif HF).
Ce bloc est absent du README sur `main` — il est spécifique à la branche `hf-deploy`.
