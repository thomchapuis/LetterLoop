import streamlit as st
from datetime import datetime
from pages_app.db import get_supabase

def get_current_period():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"

def get_month_label(period: str) -> str:
    months = {
        "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
        "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
        "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
    }
    parts = period.split("-")
    if len(parts) == 2:
        return f"{months.get(parts[1], parts[1])} {parts[0]}"
    return period

def show():
    st.markdown('<p class="main-title">📖 Digest du groupe</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Découvrez les réponses de tout le monde !</p>', unsafe_allow_html=True)

    supabase = get_supabase()
    current_period = get_current_period()

    # Récupérer toutes les périodes disponibles
    all_periods_res = supabase.table("questions").select("period").execute()
    periods = sorted(list({q["period"] for q in all_periods_res.data}), reverse=True) if all_periods_res.data else [current_period]

    # Sélecteur de période
    col1, col2 = st.columns([2, 2])
    with col1:
        period_labels = [get_month_label(p) for p in periods]
        selected_label = st.selectbox("📅 Choisir un mois", period_labels)
        selected_period = periods[period_labels.index(selected_label)]

    # Charger questions + réponses
    questions_res = supabase.table("questions").select("*").eq("period", selected_period).order("created_at").execute()
    questions = questions_res.data if questions_res.data else []

    answers_res = supabase.table("answers").select("*").eq("period", selected_period).execute()
    answers = answers_res.data if answers_res.data else []

    if not questions:
        st.info(f"Aucune question définie pour {selected_label}.")
        return

    # Stats
    authors = list({a["author"] for a in answers})
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<span class="badge badge-blue">{len(questions)} questions</span>&nbsp;'
            f'<span class="badge badge-green">{len(authors)} participant(s)</span>&nbsp;'
            f'<span class="badge badge-orange">{len(answers)} réponses</span>',
            unsafe_allow_html=True
        )

    # Participants
    if authors:
        st.markdown("### 👥 Participants")
        st.markdown("&nbsp;&nbsp;".join([f'<span class="badge badge-blue">{a}</span>' for a in sorted(authors)]), unsafe_allow_html=True)
        st.markdown("")

    st.divider()

    # Afficher les réponses par question
    for q in questions:
        q_answers = [a for a in answers if a["question_id"] == q["id"]]

        st.markdown(f'<div class="question-header">❓ {q["text"]}</div>', unsafe_allow_html=True)

        if not q_answers:
            st.markdown('<div class="card" style="color:#999;font-style:italic;">Personne n\'a encore répondu à cette question.</div>', unsafe_allow_html=True)
        else:
            for a in sorted(q_answers, key=lambda x: x["author"]):
                st.markdown(
                    f'<div class="response-card">'
                    f'<span class="response-author">{a["author"]}</span>'
                    f'<p class="response-text">{a["answer"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("")

    # Bouton export
    st.divider()
    st.markdown("### 📥 Exporter le digest")

    if st.button("📄 Générer un résumé texte"):
        export_lines = [f"# Digest LetterLoop — {selected_label}\n"]
        for q in questions:
            export_lines.append(f"\n## ❓ {q['text']}\n")
            q_answers = [a for a in answers if a["question_id"] == q["id"]]
            for a in sorted(q_answers, key=lambda x: x["author"]):
                export_lines.append(f"**{a['author']}** : {a['answer']}\n")
        export_text = "\n".join(export_lines)
        st.download_button(
            label="⬇️ Télécharger (.md)",
            data=export_text,
            file_name=f"letterloop_{selected_period}.md",
            mime="text/markdown"
        )
