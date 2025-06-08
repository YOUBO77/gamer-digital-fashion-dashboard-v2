import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

st.set_page_config(page_title="🎮 Gamer Digital Fashion Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("Questionnaire for Gamers & Digital-Fashion Consumers.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Helper function to find columns by partial name (for more robust code)
def find_col(part):
    for col in df.columns:
        if part.lower() in col.lower():
            return col
    return None

# Clean and normalize spending values
def clean_spending(val):
    if pd.isna(val): return 0
    val = str(val).replace(',', '').replace('€', '').replace('$', '').lower()
    if "no" in val or "nothing" in val: return 0
    digits = ''.join(filter(lambda x: x.isdigit(), val.split()[0]))
    return int(digits) if digits else 0

# Sidebar filters
region_col = find_col("region")
age_col = find_col("age group")
gender_col = find_col("gender")

st.sidebar.title("🔎 Filters")
selected_region = st.sidebar.multiselect("Region", sorted(df[region_col].dropna().unique()))
selected_age = st.sidebar.multiselect("Age Group", sorted(df[age_col].dropna().unique()))
selected_gender = st.sidebar.multiselect("Gender", sorted(df[gender_col].dropna().unique()))

filtered_df = df.copy()
if selected_region:
    filtered_df = filtered_df[filtered_df[region_col].isin(selected_region)]
if selected_age:
    filtered_df = filtered_df[filtered_df[age_col].isin(selected_age)]
if selected_gender:
    filtered_df = filtered_df[filtered_df[gender_col].isin(selected_gender)]

# Clean spending for filtered data
spending_col = find_col("Approximate spent per month on digital cosmetics")
filtered_df['cleaned_spending'] = filtered_df[spending_col].apply(clean_spending)

# Title
st.title("🎮 Gamer & Digital Fashion Survey Dashboard")
st.markdown("Explore how gamers interact with digital fashion and cultural identity.")

# Layout: 3 columns for demographics
st.header("📊 Demographic Overview")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Age Distribution")
    fig, ax = plt.subplots()
    sns.countplot(y=filtered_df[age_col], order=filtered_df[age_col].value_counts().index, ax=ax, palette="viridis")
    st.pyplot(fig)
with col2:
    st.subheader("Gender Distribution")
    fig, ax = plt.subplots()
    sns.countplot(y=filtered_df[gender_col], order=filtered_df[gender_col].value_counts().index, ax=ax, palette="pastel")
    st.pyplot(fig)
with col3:
    st.subheader("Region Distribution")
    fig, ax = plt.subplots()
    sns.countplot(y=filtered_df[region_col], order=filtered_df[region_col].value_counts().index, ax=ax, palette="coolwarm")
    st.pyplot(fig)

# Monthly spending
st.header("💸 Monthly Spending on Digital Cosmetics")
col_spend1, col_spend2 = st.columns(2)
with col_spend1:
    st.subheader("Histogram")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df['cleaned_spending'], bins=15, kde=True, ax=ax)
    ax.set_xlabel("Monthly Spending ($/€)")
    st.pyplot(fig)
with col_spend2:
    st.subheader("Boxplot (by Age Group)")
    fig, ax = plt.subplots()
    sns.boxplot(x=filtered_df[age_col], y=filtered_df['cleaned_spending'], ax=ax)
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Monthly Spending ($/€)")
    st.pyplot(fig)

# Agreement ratings analysis
st.header("🧠 Agreement Ratings Analysis")
rating_cols = [col for col in df.columns if "present my true self" in col or "experiment with identities" in col or "borrow cultural motifs" in col]
for col in rating_cols:
    st.subheader(f"{col}")
    fig, ax = plt.subplots()
    sns.countplot(x=pd.to_numeric(filtered_df[col], errors='coerce'), ax=ax, palette="crest")
    ax.set_xlabel("Rating (1–7)")
    st.pyplot(fig)
    avg = pd.to_numeric(filtered_df[col], errors='coerce').mean()
    st.write(f"**Average rating:** {avg:.2f}")

# Cultural recognition
st.header("🌏 Cultural Recognition")
cultural_col = find_col("recognized its cultural origin")
if cultural_col:
    fig, ax = plt.subplots()
    filtered_df[cultural_col] = filtered_df[cultural_col].fillna("No Answer")
    counts = filtered_df[cultural_col].value_counts()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.axis('equal')
    st.subheader("Have you selected a skin/cosmetic based on cultural origin?")
    st.pyplot(fig)

# Word cloud for open responses
st.header("☁️ Word Cloud: Misrepresentation Examples")
text_col = find_col("misrepresentative")
if text_col:
    text_data = " ".join(filtered_df[text_col].dropna().astype(str))
    if text_data.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.write("No open responses found for word cloud.")

st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io)")
