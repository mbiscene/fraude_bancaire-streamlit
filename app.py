# -*- coding: utf-8 -*-
"""Biscene georges maxime ml avance.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12Jmp4KBqj1izPWjWnPu9OlXNtAu5-tUG
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Détection de Fraude Bancaire", layout="wide")
st.title("Système de Détection de Fraude Bancaire")

fraude_df = pd.read_csv("fraude_bancaire_synthetique_final.csv")
fraude_df.head()
if st.checkbox("Afficher les données brutes"):
    st.subheader("Données brutes")
    st.write(fraude_df)

st.subheader("Informations sur les données")
st.write(fraude_df.info())
st.write(fraude_df.describe())

fraude_df.isnull().sum()

fraude_df["age"] = fraude_df["age"].fillna(fraude_df["age"].median())
fraude_df["salaire"] = fraude_df["salaire"].fillna(fraude_df["salaire"].median())
fraude_df["score_credit"] = fraude_df["score_credit"].fillna(fraude_df["score_credit"].median())
fraude_df['anciennete_compte'] = fraude_df['anciennete_compte'].fillna(fraude_df['anciennete_compte'].median())

fraude_df["region"] = fraude_df["region"].fillna(fraude_df["region"].mode()[0])
fraude_df["type_carte"] = fraude_df["type_carte"].fillna(fraude_df["type_carte"].mode()[0])
fraude_df["genre"] = fraude_df["genre"].fillna(fraude_df["genre"].mode()[0])
fraude_df["fraude"] = fraude_df["fraude"].fillna(fraude_df["fraude"].mode()[0])

fraude_df["montant_transaction"] = fraude_df["montant_transaction"].fillna(fraude_df["montant_transaction"].median())

fraude_df.isna().sum()

cat_cols = fraude_df.select_dtypes(include=["object", "category"]).columns
print(cat_cols)

fraude_df_df = pd.get_dummies(fraude_df, columns=cat_cols, drop_first=True)
fraude_df_df.head()

st.subheader("Répartition des cas de fraude")
fig, ax = plt.subplots()
sns.countplot(x='fraude', data=fraude_df, ax=ax)
ax.set_title("Répartition des cas de fraude")
st.pyplot(fig)
plt.show()

st.subheader("📊 Distribution des montants de transaction")
fig, ax = plt.subplots()
sns.histplot(data= fraude_df, x="montant_transaction", kde=True, bins=30, ax=ax)
ax.set_title("Distribution des montants de transaction")
st.pyplot(fig)
plt.show()

st.subheader("📊 Montant des transactions selon la fraude")
fig, ax = plt.subplots()
sns.boxplot(x='fraude', y='montant_transaction', data= fraude_df, ax=ax)
ax.set_title("Montant des transactions selon la fraude")
st.pyplot(fig)
plt.show()

st.subheader("📊 Matrice de corrélation")
fraude_df = fraude_df.select_dtypes(include=['int64', 'float64', 'category'])
corr = fraude_df.corr()
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
st.pyplot(fig)
plt.show()

fraude_df_with_region = pd.read_csv("fraude_bancaire_synthetique_final.csv")

fig, ax = plt.subplots(figsize=(10, 5))
fraude_df_with_region['region'].value_counts().plot(kind='bar', ax=ax)
ax.set_title("Nombre de transactions par région")
ax.set_ylabel("Nombre")
ax.set_xlabel("Région")
plt.show()

X = fraude_df.drop("fraude", axis=1)
y = fraude_df["fraude"]

X = pd.get_dummies(X, drop_first=True)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

y_pred = model.predict(X_test)

st.write(print(classification_report(y_test, y_pred)))

st.subheader("Matrice de confusion")
fig, ax = plt.subplots()
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues', ax=ax)
ax.set_title("Matrice de confusion")
plt.show()
st.pyplot(fig)

st.subheader("🔍 Prédiction interactive : est-ce une fraude ?")

# Champs numériques
age = st.slider("Âge", 18, 100, 40)
salaire = st.number_input("Salaire", min_value=0.0, value=75000.0)
score_credit = st.slider("Score de crédit", 0.0, 100.0, 50.0)
montant_transaction = st.number_input("Montant de la transaction", min_value=0.0, value=25000.0)
anciennete_compte = st.slider("Ancienneté du compte (en années)", 0, 30, 10)

# Champs catégoriels
type_carte = st.selectbox("Type de carte", ["Visa", "Mastercard"])
region = st.selectbox("Région", ["Houston", "Orlando", "Miami"])
genre = st.selectbox("Genre", ["male", "femelle"])

# Transformer l'entrée utilisateur en DataFrame
user_input = pd.DataFrame({
    'age': [age],
    'salaire': [salaire],
    'score_credit': [score_credit],
    'montant_transaction': [montant_transaction],
    'anciennete_compte': [anciennete_compte],
    'type_carte': [type_carte],
    'region': [region],
    'genre': [genre]
})

# Encodage identique au training
df_input_full = pd.concat([fraude_df.drop('fraude', axis=1), user_input], ignore_index=True)
df_input_full_encoded = pd.get_dummies(df_input_full, drop_first=True)

# Aligner les colonnes
X_columns = pd.get_dummies(fraude_df.drop("fraude", axis=1), drop_first=True).columns
user_ready = df_input_full_encoded.tail(1).reindex(columns=X_columns, fill_value=0)

# Prédiction
pred = model.predict(user_ready)[0]
proba = model.predict_proba(user_ready)[0][1]

# Résultat
if pred == 1:
    st.error(f"🚨 Alerte : cette transaction est probablement frauduleuse (probabilité : {proba:.2%})")
else:
    st.success(f"✅ Cette transaction semble légitime (probabilité de fraude : {proba:.2%})")