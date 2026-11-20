# Lab 3: Symptom Checker (data page)
#
# This page uses a free, public medical dataset (a list of diseases and the
# symptoms that go with them). Our own Python code reads the files, cleans them,
# and ranks which conditions match the symptoms the user picks.
#
# Data source: public "Disease-Symptom" dataset (free, no API key needed).
# No AI is used on this page -- just plain Python.

import csv
import streamlit as st


# ----------------------------------------------------------------------
# Helper functions (small jobs that we reuse)
# ----------------------------------------------------------------------

def clean_name(name):
    # The file has messy names like " skin_rash". This removes the extra
    # spaces and makes everything lowercase so names always match.
    return name.strip().lower()


def pretty(name):
    # Turn "skin_rash" into "Skin Rash" so it looks nice on the screen.
    return name.replace("_", " ").strip().title()


# ----------------------------------------------------------------------
# Loading the data from the CSV files
# ----------------------------------------------------------------------

def load_diseases():
    # Build a dictionary: disease name -> list of its symptoms.
    diseases = {}
    with open("data/dataset.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            disease = row[0].strip()
            if disease == "":
                continue  # skip the blank first line in the file

            # Everything after the first column is a symptom.
            if disease not in diseases:
                diseases[disease] = []
            for item in row[1:]:
                symptom = clean_name(item)
                if symptom != "" and symptom not in diseases[disease]:
                    diseases[disease].append(symptom)
    return diseases


def load_descriptions():
    # Dictionary: disease name -> short description.
    descriptions = {}
    with open("data/symptom_Description.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                descriptions[row[0].strip()] = row[1].strip()
    return descriptions


def load_precautions():
    # Dictionary: disease name -> list of precaution tips.
    precautions = {}
    with open("data/symptom_precaution.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                disease = row[0].strip()
                tips = []
                for tip in row[1:]:
                    if tip.strip() != "":
                        tips.append(tip.strip())
                precautions[disease] = tips
    return precautions


def load_severity():
    # Dictionary: symptom -> how serious it is (a number from about 1 to 7).
    severity = {}
    with open("data/Symptom_severity.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                severity[clean_name(row[0])] = int(row[1].strip())
    return severity


# Load everything once when the page runs.
diseases = load_diseases()
descriptions = load_descriptions()
precautions = load_precautions()
severity = load_severity()

# Make one big sorted list of every symptom (the real names).
all_symptoms = []
for disease in diseases:
    for symptom in diseases[disease]:
        if symptom not in all_symptoms:
            all_symptoms.append(symptom)
all_symptoms.sort()

# Make nice-looking names for the dropdown, and remember which real
# symptom each nice name belongs to.
nice_names = []
nice_to_real = {}
for symptom in all_symptoms:
    nice = pretty(symptom)
    nice_names.append(nice)
    nice_to_real[nice] = symptom


# ----------------------------------------------------------------------
# The page
# ----------------------------------------------------------------------

st.title("🩺 Symptom Checker")
st.write(
    "Pick the symptoms you have and this page will rank the medical conditions "
    "that match them best. Remember: this is a study tool, **not** a diagnosis."
)

st.caption("Our dataset has " + str(len(diseases)) +
           " conditions and " + str(len(all_symptoms)) + " symptoms.")

# --- Input 1: choose your symptoms ---
chosen_nice = st.multiselect("Select your symptoms:", nice_names)

# Turn the nice names the user picked back into the real symptom names.
chosen = []
for name in chosen_nice:
    chosen.append(nice_to_real[name])

# --- Input 2: how many results to show ---
top_n = st.slider("How many top conditions should we show?", 1, 10, 5)

# If nothing is picked yet, stop here with a friendly message.
if len(chosen) == 0:
    st.info("👆 Choose at least one symptom above to see possible conditions.")
    st.stop()


# ----------------------------------------------------------------------
# Scoring: count how many of your symptoms each disease has
# ----------------------------------------------------------------------

# Dictionary: disease -> how many of your symptoms it has.
scores = {}
for disease in diseases:
    match_count = 0
    for symptom in chosen:
        if symptom in diseases[disease]:
            match_count += 1
    if match_count > 0:
        scores[disease] = match_count

if len(scores) == 0:
    st.warning("No conditions in our dataset matched those symptoms. "
               "Try picking different ones.")
    st.stop()

# Put the conditions in order, best match first.
# We find the highest score, save it, then "cross it off" and repeat.
ranked_names = []
ranked_counts = []
scores_left = dict(scores)  # a copy we can cross things off of

while len(scores_left) > 0:
    best_disease = ""
    best_count = -1
    for disease in scores_left:
        if scores_left[disease] > best_count:
            best_count = scores_left[disease]
            best_disease = disease
    ranked_names.append(best_disease)
    ranked_counts.append(best_count)
    del scores_left[best_disease]  # cross it off so we don't pick it again

# Keep only the top N the user asked for.
top_conditions = ranked_names[:top_n]
top_counts = ranked_counts[:top_n]


# ----------------------------------------------------------------------
# Visual 1: a bar chart of the top matching conditions
# ----------------------------------------------------------------------

st.subheader("Top matching conditions")

# st.bar_chart can take a dictionary of lists. We tell it which list is the
# x-axis (the condition names) and which is the y-axis (the match counts).
st.bar_chart(
    {"Condition": top_conditions, "Matching symptoms": top_counts},
    x="Condition",
    y="Matching symptoms",
)

# Also list the matches in words, with a match percentage.
for i in range(len(top_conditions)):
    disease = top_conditions[i]
    count = top_counts[i]
    percent = round(count / len(chosen) * 100)
    st.write("**" + disease + "** — matches " + str(count) +
             " of your " + str(len(chosen)) + " symptoms (" + str(percent) + "%)")


# ----------------------------------------------------------------------
# Input 3 + Visual 2: look closer at one condition
# ----------------------------------------------------------------------

st.subheader("Look closer at one condition")

selected = st.selectbox("Pick a condition to learn more about:", top_conditions)

# Show its description if we have one.
if selected in descriptions:
    st.write(descriptions[selected])

# Visual 2: a bar chart of how severe YOUR matching symptoms are for this condition.
your_matching = []
for symptom in chosen:
    if symptom in diseases[selected]:
        your_matching.append(symptom)

if len(your_matching) > 0:
    sev_labels = []
    sev_values = []
    for symptom in your_matching:
        sev_labels.append(pretty(symptom))
        # Look up how serious the symptom is. If it's not in the file, use 0.
        if symptom in severity:
            sev_values.append(severity[symptom])
        else:
            sev_values.append(0)

    st.write("How serious your matching symptoms are for **" + selected + "**:")
    st.bar_chart(
        {"Symptom": sev_labels, "Severity (higher = more serious)": sev_values},
        x="Symptom",
        y="Severity (higher = more serious)",
    )

# Show precaution tips if we have them.
if selected in precautions and len(precautions[selected]) > 0:
    st.write("**Precautions / tips:**")
    for tip in precautions[selected]:
        st.write("- " + tip)


# ----------------------------------------------------------------------
# Extra feature: compare two conditions side by side
# ----------------------------------------------------------------------

st.subheader("Compare two conditions side by side")
st.write("Not sure how two conditions are different? Compare their symptoms here.")

all_disease_names = sorted(diseases.keys())

col1, col2 = st.columns(2)
with col1:
    disease_a = st.selectbox("First condition:", all_disease_names, index=0)
with col2:
    disease_b = st.selectbox("Second condition:", all_disease_names, index=1)

col1, col2 = st.columns(2)

with col1:
    st.write("**" + disease_a + "**")
    for symptom in sorted(diseases[disease_a]):
        # Put a check mark next to symptoms you picked.
        if symptom in chosen:
            st.write("✅ " + pretty(symptom))
        else:
            st.write("• " + pretty(symptom))

with col2:
    st.write("**" + disease_b + "**")
    for symptom in sorted(diseases[disease_b]):
        if symptom in chosen:
            st.write("✅ " + pretty(symptom))
        else:
            st.write("• " + pretty(symptom))

# Show which symptoms the two conditions share.
shared = []
for symptom in diseases[disease_a]:
    if symptom in diseases[disease_b]:
        shared.append(pretty(symptom))

st.write("**Symptoms they share:**")
if len(shared) > 0:
    shared.sort()
    st.write(", ".join(shared))
else:
    st.write("These two conditions share no symptoms in our dataset.")
