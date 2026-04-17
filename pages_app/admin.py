import streamlit as st
from datetime import datetime
from pages_app.db import get_supabase

# Banque de questions suggérées
SUGGESTED_QUESTIONS = [
    "Quelle a été ta plus belle découverte ce mois-ci ?",
    "Quel livre / film / série t'a marqué(e) récemment ?",
    "Quelle est une chose que tu as apprise sur toi-même ce mois ?",
    "Quel moment t'a le plus fait rire ce mois-ci ?",
    "Si tu devais résumer ton mois en un mot, lequel choisirais-tu ?",
    "Quel défi as-tu relevé ce mois-ci ?",
    "Quelle personne t'a inspiré(e) ce mois-ci, et pourquoi ?",
    "Quelle habitude as-tu essayé de prendre ou de quitter ?",
    "Quelle musique ou podcast t'a accompagné(e) ce mois ?",
    "Qu'est-ce que tu attends le plus du mois prochain ?",
    "Quel endroit as-tu (re)découvert ce mois-ci ?",
    "Quelle est la chose dont tu es le plus fier/fière ce mois-ci ?",
]

def get_current_period():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"

def show():
    st.markdown('<p class="main-title">🛠️ Questions du mois</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sélectionne les questions pour ce mois-ci (max 5 recommandé)</p>', unsafe_allow_html=True)

    # Mot de passe admin simple
    #admin_pwd = st.text_input("🔒 Mot de passe admin", type="password")
    #if admin_pwd != st.secrets.get("ADMIN_PASSWORD", "admin123"):
    #    if admin_pwd:
    #        st.error("Mot de passe incorrect.")
    #    st.info("Entrez le mot de passe admin pour accéder à cette page.")
     #   return

    supabase = get_supabase()
    period = get_current_period()

    # Charger les questions existantes pour ce mois
    existing = supabase.table("questions").select("*").eq("period", period).execute()
    existing_texts = [q["text"] for q in existing.data] if existing.data else []

    st.markdown(f'<span class="badge badge-blue">📅 Période : {period}</span>', unsafe_allow_html=True)
    st.markdown("")

    # --- Section : questions existantes ---
    if existing_texts:
        st.markdown("### ✅ Questions actives ce mois-ci")
        for i, q in enumerate(existing_texts):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.markdown(f'<div class="card">**{i+1}.** {q}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"del_{i}", help="Supprimer"):
                    supabase.table("questions").delete().eq("period", period).eq("text", q).execute()
                    st.rerun()
        st.divider()

    # --- Section : ajouter depuis la banque ---
    st.markdown("### 📚 Banque de questions suggérées")
    cols = st.columns(2)
    for idx, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[idx % 2]:
            already = q in existing_texts
            with st.container():
                st.markdown(f'<div class="card">{"✅ " if already else ""}{q}</div>', unsafe_allow_html=True)
                if not already:
                    if st.button("➕ Ajouter", key=f"add_{idx}"):
                        supabase.table("questions").insert({
                            "text": q,
                            "period": period,
                            "created_at": datetime.now().isoformat()
                        }).execute()
                        st.success("Question ajoutée !")
                        st.rerun()

    st.divider()

    # --- Section : question personnalisée ---
    st.markdown("### ✏️ Ajouter une question personnalisée")
    with st.container():
        custom_q = st.text_area("Écris ta question ici...", max_chars=300, height=80)
        if st.button("➕ Ajouter ma question"):
            if custom_q.strip():
                supabase.table("questions").insert({
                    "text": custom_q.strip(),
                    "period": period,
                    "created_at": datetime.now().isoformat()
                }).execute()
                st.success("Question personnalisée ajoutée !")
                st.rerun()
            else:
                st.warning("La question ne peut pas être vide.")

    # --- Résumé ---
    st.divider()
    count = len(existing_texts)
    if count == 0:
        st.warning("⚠️ Aucune question sélectionnée pour ce mois.")
    else:
        st.success(f"✅ {count} question(s) prête(s) pour {period}. Les membres peuvent maintenant répondre !")
