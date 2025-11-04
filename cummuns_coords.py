
import pandas as pd
import requests
import os
import csv
import json 
data=pd.read_csv('premiere_entreprise_par_page.csv')
print(data.head())
data_filtered = data[['ville', 'code_postal']]
data_filtered = data_filtered.drop_duplicates()
data_filtered.to_csv('entreprises_avec_ville_et_code_postal.csv', index=False)
data = []

for _, r in data_filtered.iterrows():
    url = f"https://geo.api.gouv.fr/communes?nom={r.ville}&codePostal={r.code_postal}&fields=centre&format=json"
    res = requests.get(url).json()
    if res:
        coords = res[0]["centre"]["coordinates"]
        data.append([r.ville, r.code_postal, coords[1], coords[0]])

pd.DataFrame(data, columns=["Nom de la Commune", "Code Postal", "Latitude", "Longitude"]) \
  .to_csv("communes_coords.csv", index=False, encoding="utf-8-sig")

print("✅ Fichier 'communes_coords.csv' créé avec succès !")
print(pd.read_csv("communes_coords.csv").head())
