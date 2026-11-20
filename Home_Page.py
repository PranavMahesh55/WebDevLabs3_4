import streamlit as st

# Title of App
st.title("🩺 Symptom Checker & Health Study Buddy")

# Assignment Data
st.header("CS 1301")
st.subheader("Team 72, Web Development - Section C")
st.subheader("Pranav Mahesh, Lina")

# TODO (optional): add a group photo to the images folder and show it here:
# st.image("images/group_photo.jpg")


# Introduction
st.write("""
Welcome to our app! It is a learning tool about **medicine and diagnosis**.
You type in the symptoms you have, and the app looks through a medical dataset
to show which conditions match your symptoms the best.

It is built for medical students and anyone curious about healthcare. It is
**not** a real diagnosis and should never replace a doctor.

You can move between the pages using the sidebar on the left:

1. **Home**: This page, which explains what the app does.
2. **Symptom Checker**: Pick your symptoms and get a ranked list of possible
   conditions, with charts, descriptions, and a side-by-side comparison.
3. **HealthBuddy**: A friendly AI chatbot that explains conditions and medical
   words in simple language.
""")

st.info("Reminder: This app is a study tool, not medical advice. "
        "Always see a real doctor about your health.")
