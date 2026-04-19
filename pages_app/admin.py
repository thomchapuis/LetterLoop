import streamlit as st
from datetime import datetime
from pages_app.db import get_supabase

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
    "Quelle photo symboliserait ton mois si tu devais en choisir une ?",
    "Qu'est-ce qui t'a surpris(e) ce mois-ci ?",
    "Quelle conversation t'a le plus marqué(e) ce mois ?",
]

def get_current_period():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"

def show():
    st.markdown('<p class="main-title">💡 Questions du mois</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Propose ou vote pour les questions de ce mois — tout le monde peut participer !</p>', unsafe_allow_html=True)

    supabase = get_supabase()
    period = get_current_period()

    existing_res = supabase.table("questions").select("*").eq("period", period).order("created_at").execute()
    existing = existing_res.data if existing_res.data else []
    existing_texts = [q["text"] for q in existing]

    st.markdown(f'<span class="badge badge-blue">📅 Période : {period}</span>&nbsp;<span class="badge badge-green">{len(existing)} question(s) active(s)</span>', unsafe_allow_html=True)
    st.markdown("")

    if existing:
        st.markdown("### ✅ Questions actives ce mois-ci")
        for i, q in enumerate(existing):
            col1, col2 = st.columns([11, 1])
            with col1:
                st.markdown(f'<div class="card"><strong>{i+1}.</strong> {q["text"]}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"del_{q['id']}", help="Supprimer"):
                    supabase.table("questions").delete().eq("id", q["id"]).execute()
                    st.rerun()
        st.divider()

    st.markdown("### 📚 Banque de questions suggérées")
    st.caption("Clique sur ➕ pour ajouter une question au mois en cours.")
    cols = st.columns(2)
    for idx, q_text in enumerate(SUGGESTED_QUESTIONS):
        with cols[idx % 2]:
            already = q_text in existing_texts
            border = "2px solid #6c63ff" if already else "1px solid #eee"
            st.markdown(
                f'<div class="card" style="border:{border};min-height:70px">'
                f'<span style="font-size:0.95rem">{q_text}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            if not already:
                if st.button("➕ Ajouter", key=f"add_{idx}"):
                    supabase.table("questions").insert({
                        "text": q_text,
                        "period": period,
                        "created_at": datetime.now().isoformat()
                    }).execute()
                    st.rerun()
            else:
                st.markdown('<span class="badge badge-green">Déjà ajoutée ✓</span>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### ✏️ Proposer ta propre question")
    custom_q = st.text_area(
        "label",
        placeholder="Imagine une question originale pour le groupe !",
        max_chars=300,
        height=90,
        label_visibility="collapsed"
    )
    if st.button("➕ Ajouter ma question"):
        if custom_q.strip():
            if custom_q.strip() in existing_texts:
                st.warning("Cette question existe déjà.")
            else:
                supabase.table("questions").insert({
                    "text": custom_q.strip(),
                    "period": period,
                    "created_at": datetime.now().isoformat()
                }).execute()
                st.success("✅ Ta question a été ajoutée !")
                st.rerun()
        else:
            st.warning("La question ne peut pas être vide.")

    st.divider()
    if not existing:
        st.warning("⚠️ Aucune question pour ce mois — sois le premier à en proposer une !")
    else:
        st.success(f"✅ {len(existing)} question(s) prête(s). Les membres peuvent maintenant répondre !")
