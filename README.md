# ✉️ LetterLoop — Newsletter de groupe

Une app Streamlit + Supabase pour partager chaque mois les réponses de ton groupe à des questions communes.

## 📁 Structure du projet

```
letterloop/
├── app.py                    # Point d'entrée principal
├── requirements.txt
├── supabase_schema.sql       # À exécuter dans Supabase
├── .streamlit/
│   └── secrets.toml          # Tes credentials (ne pas committer !)
└── pages_app/
    ├── __init__.py
    ├── db.py                 # Connexion Supabase
    ├── admin.py              # Page 1 : sélection des questions
    ├── repondre.py           # Page 2 : réponses des membres
    └── digest.py             # Page 3 : digest du groupe
```

## 🚀 Installation

### 1. Crée un projet Supabase

1. Va sur [supabase.com](https://supabase.com) et crée un projet
2. Dans **SQL Editor**, colle et exécute le contenu de `supabase_schema.sql`
3. Récupère dans **Project Settings > API** :
   - `Project URL`
   - `anon public` key

### 2. Configure les secrets

Édite `.streamlit/secrets.toml` :

```toml
SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGci..."   # clé anon publique
ADMIN_PASSWORD = "TonMotDePasse"
```

> ⚠️ N'envoie jamais ce fichier sur GitHub. Ajoute-le à `.gitignore`.

### 3. Lance l'app

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📖 Utilisation

### Page 1 — 🛠️ Admin (Questions du mois)
- Accès protégé par mot de passe
- Choisis jusqu'à 5 questions parmi la banque, ou crée les tiennes
- Les questions sont liées à la période en cours (`YYYY-MM`)

### Page 2 — ✍️ Répondre
- Chaque membre entre son prénom + emoji
- Répond aux questions une par une
- Les réponses sont sauvegardées en base, une seule réponse par personne/question

### Page 3 — 📖 Digest
- Affiche toutes les réponses du groupe pour le mois choisi
- Statistiques de participation
- Export en `.md` téléchargeable

## ☁️ Déploiement sur Streamlit Cloud

1. Push le projet sur GitHub (**sans** `secrets.toml`)
2. Connecte le repo sur [share.streamlit.io](https://share.streamlit.io)
3. Dans **Settings > Secrets**, colle le contenu de ton `secrets.toml`
4. Deploy !

## 🔐 Sécurité

- Le mot de passe admin est simple (stocké en secrets). Pour plus de sécurité, remplace par une vraie auth Supabase Auth.
- Les politiques RLS Supabase permettent la lecture/écriture publique — adapte selon tes besoins.
