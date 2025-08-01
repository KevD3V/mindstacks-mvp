import streamlit as st
import pandas as pd
from PIL import Image
import os


# ─── Sidebar Branding ────────────────────────────────────────────
logo_path = os.path.join("assets", "card_back.png")  # ensure this points to your saved icon
logo = Image.open(logo_path)
st.sidebar.image(logo, use_container_width=True)

# Tagline under the logo
st.sidebar.markdown("### MindStacks")
st.sidebar.markdown("#### Solve the Stack, Master Your Mind")
st.sidebar.write("---")  # horizontal divider



# ─── Sidebar: Deck Selection & Email Signup ────────────────────

BASE = "decks"

# 1️⃣ Subject picker (only subjects with at least one CSV anywhere below)
def subject_has_decks(subject):
    path = os.path.join(BASE, subject)
    # any CSV at root?
    if any(f.lower().endswith(".csv") for f in os.listdir(path)):
        return True
    # any CSV in subfolders?
    for sub in os.listdir(path):
        subp = os.path.join(path, sub)
        if os.path.isdir(subp) and any(f.lower().endswith(".csv") for f in os.listdir(subp)):
            return True
    return False

subjects = sorted(
    s for s in os.listdir(BASE)
    if os.path.isdir(os.path.join(BASE, s)) and subject_has_decks(s)
)
subject = st.sidebar.selectbox("Subject", subjects, key="sel_subject")
subject_path = os.path.join(BASE, subject)

# 2️⃣ Chapter picker (only CSVs and non-empty subfolders)
flat_chapters = sorted(
    f for f in os.listdir(subject_path)
    if f.lower().endswith(".csv")
)
subfolders = sorted(
    d for d in os.listdir(subject_path)
    if os.path.isdir(os.path.join(subject_path, d))
    and any(f.lower().endswith(".csv") for f in os.listdir(os.path.join(subject_path, d)))
)
chapter_options = flat_chapters + subfolders
chapter = st.sidebar.selectbox("Chapter", chapter_options, key="sel_chapter")

# 3️⃣ Sub-topic picker
if chapter.lower().endswith(".csv"):
    deck_folder = subject_path
    deck_files = [chapter]
else:
    deck_folder = os.path.join(subject_path, chapter)
    deck_files = sorted(
        f for f in os.listdir(deck_folder)
        if f.lower().endswith(".csv")
    )

# Guard against totally empty deck folder (shouldn't happen now)
if not deck_files:
    st.sidebar.error(f"No .csv files under:\n  {deck_folder}")
    st.stop()

subtopic = st.sidebar.selectbox("Sub-topic (optional)", deck_files, key="sel_subtopic")
deck_path = os.path.join(deck_folder, subtopic)

# ─── Reset flashcard state on deck change ──────────────────────
prev = st.session_state.get("current_deck", None)
if prev != deck_path:
    st.session_state.idx = 0
    st.session_state.show_answer = False
    st.session_state.current_deck = deck_path

# 4️⃣ Email capture form
with st.sidebar.form("email_signup", clear_on_submit=True):
    st.markdown("### 📬 Join the MindStacks List")
    email = st.text_input("Enter your email to get new decks:")
    if st.form_submit_button("Sign Up"):
        with open("emails.csv", "a") as f:
            f.write(email.strip() + "\n")
        st.success("Thanks! We'll send you new decks soon.")

# ─── Load deck & init state ────────────────────────────────────
df = pd.read_csv(deck_path)
st.session_state.setdefault("idx", 0)
st.session_state.setdefault("show_answer", False)

# ─── Flashcard Controls & Logic ────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("Show Answer", key="show_btn"):
        st.session_state.show_answer = True
with col2:
    if st.button("Next Card", key="next_btn"):
        st.session_state.idx = (st.session_state.idx + 1) % len(df)
        st.session_state.show_answer = False

# ─── Render the Flashcard ──────────────────────────────────────
card = df.iloc[st.session_state.idx]
st.title("MindStacks MVP")
deck_title = subtopic.replace("_", " ").rsplit(".", 1)[0].title()
st.subheader(f"{subject} → {chapter.replace('_',' ').title()} → {deck_title}")

st.markdown(f"**Q:** {card.Q}")
if st.session_state.show_answer:
    st.markdown(f"**A:** {card.A}")
    rating = st.radio(
        "How well did you recall this card?",
        options=[0, 1, 2, 3, 4, 5],
        index=3,
        horizontal=True,
        key="rating_widget"
    )
    st.write(f"Your rating: **{rating}**")
