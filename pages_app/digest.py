import streamlit as st
from datetime import datetime, timezone
from pages_app.db import get_supabase

# ─────────────────────────────────────────────
#  Logique de période
# ─────────────────────────────────────────────
# Cycle mensuel :
#   Du 20 du mois M au 4 du mois M+1  → LOCKED  (réponses en cours pour M)
#   Du 5 au 19 du mois M+1            → OPEN    (affiche le digest de M)
#
# Exemple :
#   20 avr → 4 mai  : bloqué, période réponse = "2025-04"
#   5 mai → 19 mai  : digest visible de "2025-04"
#   20 mai → 4 juin : bloqué, période réponse = "2025-05"

def get_digest_state():
    """
    Retourne :
      locked        : bool   — digest bloqué ou non
      digest_period : str    — période YYYY-MM dont on affiche le digest
      unlock_dt     : datetime — date/heure à laquelle ça déverrouille (si locked)
    """
    now = datetime.now()
    day = now.day

    if day >= 20:
        # Du 20 au dernier jour du mois M → locked, digest sera pour M
        # unlock le 5 du mois M+1
        if now.month == 12:
            unlock_dt = datetime(now.year + 1, 1, 5, 0, 0, 0)
        else:
            unlock_dt = datetime(now.year, now.month + 1, 5, 0, 0, 0)
        digest_period = f"{now.year}-{now.month:02d}"
        return True, digest_period, unlock_dt
    elif day <= 4:
        # Du 1er au 4 du mois M+1 → locked, digest sera pour M (mois précédent)
        if now.month == 1:
            prev_year, prev_month = now.year - 1, 12
        else:
            prev_year, prev_month = now.year, now.month - 1
        unlock_dt = datetime(now.year, now.month, 5, 0, 0, 0)
        digest_period = f"{prev_year}-{prev_month:02d}"
        return True, digest_period, unlock_dt
    else:
        # Du 5 au 19 → ouvert, affiche le mois précédent
        if now.month == 1:
            prev_year, prev_month = now.year - 1, 12
        else:
            prev_year, prev_month = now.year, now.month - 1
        digest_period = f"{prev_year}-{prev_month:02d}"
        return False, digest_period, None

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

def format_countdown(unlock_dt: datetime) -> str:
    now = datetime.now()
    delta = unlock_dt - now
    if delta.total_seconds() <= 0:
        return "bientôt !"
    total_secs = int(delta.total_seconds())
    days = total_secs // 86400
    hours = (total_secs % 86400) // 3600
    minutes = (total_secs % 3600) // 60
    parts = []
    if days:
        parts.append(f"**{days}j**")
    if hours:
        parts.append(f"**{hours}h**")
    parts.append(f"**{minutes}min**")
    return " ".join(parts)

# ─────────────────────────────────────────────
#  Page principale
# ─────────────────────────────────────────────
def show():
    st.markdown('<p class="main-title">📖 Digest du groupe</p>', unsafe_allow_html=True)

    locked, digest_period, unlock_dt = get_digest_state()

    # ── ÉTAT BLOQUÉ ──────────────────────────────────────────────
    if locked:
        unlock_label = unlock_dt.strftime("%-d %B") if unlock_dt else "bientôt"
        countdown = format_countdown(unlock_dt) if unlock_dt else ""

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 20px;
            padding: 3rem 2rem;
            text-align: center;
            margin-top: 1rem;
            color: white;
        ">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔒</div>
            <h2 style="color: white; font-size: 1.8rem; margin-bottom: 0.5rem;">
                Le digest est en cours de préparation…
            </h2>
            <p style="color: #a78bfa; font-size: 1.1rem; margin-bottom: 2rem;">
                Les réponses du groupe pour <strong style="color:white">{get_month_label(digest_period)}</strong>
                seront révélées le <strong style="color:#fbbf24">{unlock_label}</strong>.
            </p>
            <div style="
                background: rgba(255,255,255,0.08);
                border-radius: 12px;
                padding: 1.2rem 2rem;
                display: inline-block;
                margin-bottom: 2rem;
            ">
                <p style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 0.3rem;">⏳ Ouverture dans</p>
                <p style="font-size: 1.5rem; color: white; margin: 0">{countdown}</p>
            </div>
            <br/>
            <p style="color: #6b7280; font-size: 0.9rem;">
                En attendant, as-tu répondu à toutes les questions ? ✍️
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        # Auto-refresh toutes les 60s pour mettre à jour le timer
        st.markdown("""
        <script>
            setTimeout(function() { window.location.reload(); }, 60000);
        </script>
        """, unsafe_allow_html=True)
        return

    # ── ÉTAT OUVERT ───────────────────────────────────────────────
    supabase = get_supabase()
    label = get_month_label(digest_period)
    st.markdown(f'<p class="subtitle">Réponses du groupe pour <strong>{label}</strong></p>', unsafe_allow_html=True)

    questions_res = supabase.table("questions").select("*").eq("period", digest_period).order("created_at").execute()
    questions = questions_res.data if questions_res.data else []

    answers_res = supabase.table("answers").select("*").eq("period", digest_period).execute()
    answers = answers_res.data if answers_res.data else []

    if not questions:
        st.info(f"Aucune question définie pour {label}.")
        return

    authors = list({a["author"] for a in answers})

    # Stats rapides
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:2rem">📝</div><div style="font-size:1.4rem;font-weight:800">{len(questions)}</div><div style="color:#888;font-size:0.85rem">questions</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:2rem">👥</div><div style="font-size:1.4rem;font-weight:800">{len(authors)}</div><div style="color:#888;font-size:0.85rem">participant(s)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:2rem">💬</div><div style="font-size:1.4rem;font-weight:800">{len(answers)}</div><div style="color:#888;font-size:0.85rem">réponses</div></div>', unsafe_allow_html=True)

    # Liste participants
    if authors:
        st.markdown("&nbsp;&nbsp;".join([f'<span class="badge badge-blue">{a}</span>' for a in sorted(authors)]), unsafe_allow_html=True)
        st.markdown("")

    st.divider()

    # ── COMMENTAIRES : qui commente ? ────────────────────────────
    st.markdown("#### 👤 Tu es…")
    col_name, col_emoji = st.columns([3, 1])
    with col_name:
        commenter_name = st.text_input("Ton prénom pour commenter", placeholder="Marie, Julien…", max_chars=40, label_visibility="collapsed", key="commenter_name")
    with col_emoji:
        commenter_emoji = st.selectbox("Emoji", ["💬", "😊", "🌟", "🎸", "🌿", "🦊", "🐻", "🚀", "🎨", "🍕", "🧠", "🦋"], key="commenter_emoji", label_visibility="collapsed")
    if commenter_name.strip():
        commenter = f"{commenter_emoji} {commenter_name.strip()}"
    else:
        commenter = None

    st.divider()

    # ── RÉPONSES PAR QUESTION ─────────────────────────────────────
    for q in questions:
        q_answers = [a for a in answers if a["question_id"] == q["id"]]

        st.markdown(f'<div class="question-header">❓ {q["text"]}</div>', unsafe_allow_html=True)

        if not q_answers:
            st.markdown('<div class="card" style="color:#999;font-style:italic;">Personne n\'a répondu à cette question.</div>', unsafe_allow_html=True)
        else:
            for a in sorted(q_answers, key=lambda x: x["author"]):
                answer_id = a["id"]

                # Charger les commentaires pour cette réponse
                comments_res = supabase.table("comments").select("*").eq("answer_id", answer_id).order("created_at").execute()
                comments = comments_res.data if comments_res.data else []

                # Réponse principale
                st.markdown(
                    f'<div class="response-card">'
                    f'<span class="response-author">{a["author"]}</span>'
                    f'<p class="response-text">{a["answer"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Commentaires existants
                if comments:
                    for c in comments:
                        st.markdown(
                            f'<div style="margin-left:1.5rem;margin-top:0.3rem;margin-bottom:0.3rem;'
                            f'background:#f3f0ff;border-left:3px solid #a78bfa;border-radius:0 8px 8px 0;'
                            f'padding:0.5rem 1rem;">'
                            f'<span style="font-size:0.78rem;font-weight:700;color:#7c3aed">{c["author"]}</span>'
                            f'<span style="font-size:0.75rem;color:#aaa;margin-left:0.5rem">{c["created_at"][:10]}</span>'
                            f'<p style="margin:0.2rem 0 0 0;font-size:0.88rem;color:#444">{c["content"]}</p>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                # Formulaire pour commenter
                with st.expander(f"💬 Commenter ({len(comments)} commentaire{'s' if len(comments) != 1 else ''})", expanded=False):
                    if not commenter:
                        st.caption("Entre ton prénom en haut de page pour pouvoir commenter.")
                    else:
                        comment_key = f"comment_{answer_id}"
                        comment_text = st.text_area(
                            "Ton commentaire",
                            key=comment_key,
                            placeholder="Réagis à cette réponse…",
                            height=80,
                            label_visibility="collapsed",
                            max_chars=500
                        )
                        if st.button("Envoyer 💬", key=f"send_{answer_id}"):
                            if comment_text.strip():
                                supabase.table("comments").insert({
                                    "answer_id": answer_id,
                                    "author": commenter,
                                    "content": comment_text.strip(),
                                    "created_at": datetime.now().isoformat()
                                }).execute()
                                st.success("Commentaire ajouté !")
                                st.rerun()
                            else:
                                st.warning("Le commentaire ne peut pas être vide.")

        st.markdown("")

    # ── EXPORT ────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📥 Exporter le digest")
    if st.button("📄 Générer un résumé texte"):
        export_lines = [f"# Digest LetterLoop — {label}\n"]
        for q in questions:
            export_lines.append(f"\n## ❓ {q['text']}\n")
            q_answers = [a for a in answers if a["question_id"] == q["id"]]
            for a in sorted(q_answers, key=lambda x: x["author"]):
                export_lines.append(f"**{a['author']}** : {a['answer']}\n")
        export_text = "\n".join(export_lines)
        st.download_button(
            label="⬇️ Télécharger (.md)",
            data=export_text,
            file_name=f"letterloop_{digest_period}.md",
            mime="text/markdown"
        )
