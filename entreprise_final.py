import pandas as pd

df_entreprise = pd.read_csv(
    r"C:\Users\fatemeh.fereydouni\Desktop\extraction\premiere_entreprise_par_page.csv",
    encoding="cp1252")
df_coords=pd.read_csv(
    r"C:\Users\fatemeh.fereydouni\Desktop\extraction\APIs\communes_coords.csv",
    encoding="cp1252")
df_coords=df_coords[["Longitude", "Latitude"]].drop_duplicates().reset_index(drop=True)
merged=pd.concat([df_entreprise,df_coords],axis=1)
merged=merged.drop(columns=["ville","Longitude", "Latitude","adresse"])
merged.to_csv(r"C:\Users\fatemeh.fereydouni\Desktop\extraction\normalisation\entreprise_final.csv", index=False, encoding="utf-8")
print("✅ Le fichier test.csv a été créé avec succès.")