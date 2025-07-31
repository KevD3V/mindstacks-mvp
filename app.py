import streamlit as st
import pandas as pd
import os

# --- ► LEVEL SELECTOR (Subject → Chapter → Optional Sub-topic) ---
BASE = "decks"

# 1️⃣ Subject
subjects = [d for d in os.listdir(BASE) if os.path.isdir(os.path.join(BASE, d))]
subject = st.sidebar.selectbox("Subject", subjects, key="sel_subject")

subject_path = os.path.join(BASE, subject)

# 2️⃣ Chapters & Subfolders
flat_chapters = [f for f in os.listdir(subject_path)
                 if f.lower().endswith(".csv")]
subfolders     = [d for d in os.listdir(subject_path)
                  if os.path.isdir(os.path.join(subject_path, d))]

chapter_choice = st.sidebar.selectbox(
    "Chapter",
    flat_chapters + subfolders,
    key="sel_chapter"
)

# 3️⃣ Drill-down into subfolder if chosen
if chapter_choice.lower().endswith(".csv"):
    deck_folder = subject_path
    deck_files  = [chapter_choice]
else:
    deck_folder = os.path.join(subject_path, chapter_choice)
    deck_files  = [f for f in os.listdir(deck_folder)
                   if f.lower().endswith(".csv")]

#  ◼ Guard against empty folder
if not deck_files:
    st.sidebar.error(f"No .csv decks found under:\n  {deck_folder}")
    st.stop()

# 4️⃣ Optional sub-topic picker
if len(deck_files) > 1:
    deck_file = st.sidebar.selectbox("Sub-topic (optional)", deck_files, key="sel_subtopic")
else:
    deck_file = deck_files[0]

# Build the full path
deck_path = os.path.join(deck_folder, deck_file)

# --- ► RESET STATE ON DECK CHANGE --------------------------------
prev = st.session_state.get("current_deck", None)
if prev != deck_path:
    # User picked a new deck – reset flashcard state
    st.session_state.idx = 0
    st.session_state.show_answer = False
    st.session_state.current_deck = deck_path

# --- Load deck -------------------------------------------------
df = pd.read_csv(deck_path)

# --- Initialize other session state if missing ----------------
st.session_state.setdefault("idx", 0)
st.session_state.setdefault("show_answer", False)

# --- Buttons & logic ------------------------------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("Show Answer", key="show_btn"):
        st.session_state.show_answer = True
with col2:
    if st.button("Next Card", key="next_btn"):
        st.session_state.idx = (st.session_state.idx + 1) % len(df)
        st.session_state.show_answer = False

# --- Display card ------------------------------------------------
card = df.iloc[st.session_state.idx]
st.title("MindStacks MVP")
st.subheader(f"Deck: {deck_file.replace('_',' ').rsplit('.',1)[0].title()}")

st.markdown(f"**Q:** {card.Q}")
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



# --- Email Signup Form (Sidebar) -----------------------------
with st.sidebar.form("email_signup", clear_on_submit=True):
    st.markdown("### 📬 Join the MindStacks List")
    email = st.text_input("Enter your email to get new decks:")
    submitted = st.form_submit_button("Sign Up")
    if submitted:
        # Append to local file (will create if missing)
        with open("emails.csv", "a") as f:
            f.write(email.strip() + "\n")
        st.success("Thanks! We'll send you new decks soon.")



### This is a test comment f