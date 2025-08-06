import streamlit as st
import pandas as pd
from PIL import Image
import os
import random

# ─── Sidebar Branding ────────────────────────────────────────────
logo_path = os.path.join("assets", "card_back.png")
logo = Image.open(logo_path)
st.sidebar.image(logo, use_container_width=True)
st.sidebar.markdown("### MindStacks")
st.sidebar.markdown("#### Solve the Stack, Master Your Mind")
st.sidebar.write("---")

# ─── Sidebar: Deck Selection & Email Signup ────────────────────
BASE = "decks"
def subject_has_decks(subject):
    path = os.path.join(BASE, subject)
    if any(f.lower().endswith(".csv") for f in os.listdir(path)):
        return True
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

flat_chapters = sorted(
    f for f in os.listdir(subject_path)
    if f.lower().endswith(".csv")
)
subfolders = sorted(
    d for d in os.listdir(subject_path)
    if os.path.isdir(os.path.join(subject_path, d))
    and any(f.lower().endswith(".csv") for f in os.listdir(os.path.join(subject_path, d)))
)
chapter = st.sidebar.selectbox("Chapter", flat_chapters + subfolders, key="sel_chapter")

if chapter.lower().endswith(".csv"):
    deck_folder = subject_path
    deck_files = [chapter]
else:
    deck_folder = os.path.join(subject_path, chapter)
    deck_files = sorted(f for f in os.listdir(deck_folder) if f.lower().endswith(".csv"))

if not deck_files:
    st.sidebar.error(f"No .csv files under:\n  {deck_folder}")
    st.stop()

subtopic = st.sidebar.selectbox("Sub-topic (optional)", deck_files, key="sel_subtopic")
deck_path = os.path.join(deck_folder, subtopic)

# ─── Reset state on deck change ─────────────────────────────────
if st.session_state.get("current_deck") != deck_path:
    st.session_state.current_deck = deck_path
    st.session_state.idx = 0
    st.session_state.show_answer = False
    st.session_state.submitted = False
    st.session_state.shuffled_map = {}

# 4️⃣ Email capture form
with st.sidebar.form("email_signup", clear_on_submit=True):
    st.markdown("### 📬 Join the MindStacks List")
    email = st.text_input("Enter your email to get new decks:")
    if st.form_submit_button("Sign Up"):
        with open("emails.csv", "a") as f:
            f.write(email.strip() + "\n")
        st.success("Thanks! We'll send you new decks soon.")

# ─── Load deck & initialize session state ──────────────────────
df = pd.read_csv(deck_path)
st.session_state.setdefault("idx", 0)
st.session_state.setdefault("show_answer", False)
st.session_state.setdefault("submitted", False)
st.session_state.setdefault("shuffled_map", {})

# ─── Callback definitions ──────────────────────────────────────
def next_card():
    st.session_state.idx = (st.session_state.idx + 1) % len(df)
    st.session_state.show_answer = False
    st.session_state.submitted = False

def reveal_answer():
    st.session_state.show_answer = True

def submit_mcq():
    st.session_state.submitted = True

# ─── Render the Header & Deck Title ────────────────────────────
card = df.iloc[st.session_state.idx]
st.title("MindStacks MVP")
deck_title = subtopic.replace("_", " ").rsplit(".", 1)[0].title()
st.subheader(f"{subject} → {chapter.replace('_',' ').title()} → {deck_title}")

# ─── Detect MCQ vs. Open Flashcard ──────────────────────────────
is_mcq = all(col in df.columns for col in ["Option1","Option2","Option3","Option4","Correct"])

if is_mcq:
    # Prepare MCQ options and shuffle if needed
    orig_opts = [card[f"Option{i}"] for i in range(1,5)]
    correct_orig = int(card["Correct"]) - 1
    idx = st.session_state.idx

    if idx not in st.session_state.shuffled_map:
        opts_with_idx = list(enumerate(orig_opts))
        random.shuffle(opts_with_idx)
        st.session_state.shuffled_map[idx] = opts_with_idx
    opts_with_idx = st.session_state.shuffled_map[idx]
    opts = [opt for (_,opt) in opts_with_idx]
    correct_new = next(i for i,(orig_i,_) in enumerate(opts_with_idx) if orig_i==correct_orig)

    # MCQ UI
    st.markdown(f"**Q:** {card.Q}")
    choice = st.radio("Choose one:", opts, key=f"mcq_choice_{idx}")

    st.button("Submit Answer", on_click=submit_mcq, key=f"submit_{idx}")
    if st.session_state.submitted:
        if choice == opts[correct_new]:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. Right answer: **{opts[correct_new]}**.")

    st.button("Next Card", on_click=next_card, key=f"next_{idx}")

else:
    # Open‐ended flashcard UI
    st.markdown(f"**Q:** {card.Q}")

    col1, col2 = st.columns(2)
    with col1:
        st.button("Show Answer", on_click=reveal_answer, key="show_btn")
    with col2:
        st.button("Next Card", on_click=next_card, key="next_btn")

    if st.session_state.show_answer:
        st.markdown(f"**A:** {card.A}")
        rating = st.radio(
            "How well did you recall this card?",
            options=[0,1,2,3,4,5],
            index=3,
            horizontal=True,
            key="rating_widget"
        )
        st.write(f"Your rating: **{rating}**")
