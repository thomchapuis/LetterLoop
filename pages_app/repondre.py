import streamlit as st
from datetime import datetime
from pages_app.db import get_supabase

def get_current_period():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"

def show():
    st.markdown('<p class="main-title">✍️ Répondre aux questions</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Partage ce qui t\'a marqué(e) ce mois-ci avec ton groupe !</p>', unsafe_allow_html=True)

    supabase = get_supabase()
    period = get_current_period()

    # Charger les questions du mois
    questions_res = supabase.table("questions").select("*").eq("period", period).order("created_at").execute()
    questions = questions_res.data if questions_res.data else []

    if not questions:
        st.warning("⚠️ Aucune question n'a encore été définie pour ce mois. Revenez bientôt !")
        return

    st.markdown(f'<span class="badge badge-blue">📅 {period}</span>&nbsp;<span class="badge badge-orange">{len(questions)} questions</span>', unsafe_allow_html=True)
    st.markdown("")

    # Identité du répondant
    st.markdown("### 👤 Qui es-tu ?")
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input("Ton prénom", placeholder="Ex : Marie, Julien, Axel…", max_chars=50)
    with col2:
        emoji = st.selectbox("Ton emoji 😄", ["😊", "🌟", "🎸", "🌿", "🦊", "🐻", "🚀", "🎨", "🍕", "🧠", "🦋", "🌊"])

    if not name.strip():
        st.info("Commence par entrer ton prénom pour pouvoir répondre.")
        return

    display_name = f"{emoji} {name.strip()}"

    # Vérifier si cette personne a déjà répondu ce mois
    existing_answers = supabase.table("answers").select("question_id").eq("period", period).eq("author", display_name).execute()
    answered_question_ids = {a["question_id"] for a in existing_answers.data} if existing_answers.data else set()

    all_answered = all(q["id"] in answered_question_ids for q in questions)

    if all_answered:
        st.success(f"✅ Bravo {display_name} ! Tu as répondu à toutes les questions ce mois-ci.")
        st.balloons()
        st.markdown("---")
        st.markdown("### Tes réponses ce mois-ci")
        my_answers = supabase.table("answers").select("*").eq("period", period).eq("author", display_name).execute()
        q_map = {q["id"]: q["text"] for q in questions}
        for a in my_answers.data:
            q_text = q_map.get(a["question_id"], "Question inconnue")
            st.markdown(f'<div class="question-header">❓ {q_text}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="response-card"><span class="response-text">{a["answer"]}</span></div>', unsafe_allow_html=True)
        return

    # Formulaire de réponses
    st.markdown("---")
    st.markdown(f"### 💬 Tes réponses, {display_name}")

    answers_draft = {}

    for i, q in enumerate(questions):
        already_answered = q["id"] in answered_question_ids
        if already_answered:
            st.markdown(f'<div class="question-header">✅ {q["text"]}</div>', unsafe_allow_html=True)
            # Afficher la réponse existante
            ans = supabase.table("answers").select("answer").eq("question_id", q["id"]).eq("author", display_name).execute()
            if ans.data:
                st.markdown(f'<div class="response-card"><span class="response-text">{ans.data[0]["answer"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="question-header">❓ {q["text"]}</div>', unsafe_allow_html=True)
            answers_draft[q["id"]] = st.text_area(
                label=f"question_{i}",
                label_visibility="collapsed",
                placeholder="Ta réponse ici… sois authentique, personne ne te juge ! 😊",
                height=120,
                key=f"answer_{q['id']}"
            )

    # Bouton de soumission
    unanswered = {qid: txt for qid, txt in answers_draft.items() if txt.strip()}
    pending_count = len([q for q in questions if q["id"] not in answered_question_ids])

    st.markdown("")
    if pending_count > 0:
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.button(f"📨 Envoyer mes {len(unanswered)} réponse(s)", use_container_width=True)
        with col2:
            st.markdown(f'<div style="padding-top:0.5rem;"><span class="badge badge-orange">{pending_count - len(unanswered)} restante(s)</span></div>', unsafe_allow_html=True)

        if submitted:
            if not unanswered:
                st.warning("Réponds à au moins une question avant d'envoyer !")
            else:
                rows = []
                for qid, answer_text in unanswered.items():
                    rows.append({
                        "question_id": qid,
                        "period": period,
                        "author": display_name,
                        "answer": answer_text.strip(),
                        "created_at": datetime.now().isoformat()
                    })
                supabase.table("answers").insert(rows).execute()
                st.success(f"✅ Tes {len(rows)} réponse(s) ont été enregistrées. Merci {display_name} !")
                st.rerun()
