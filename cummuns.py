import pandas as pd

df1 = pd.read_csv(
    r"C:\Users\fatemeh.fereydouni\Desktop\extraction\premiere_entreprise_par_page.csv",
    encoding="cp1252")

df1 = df1[["ville", "code_postal", "adresse"]].drop_duplicates().reset_index(drop=True)
df2=pd.read_csv(
    r"C:\Users\fatemeh.fereydouni\Desktop\extraction\APIs\communes_coords.csv",
    encoding="cp1252")
df2=df2[["Longitude", "Latitude"]].drop_duplicates().reset_index(drop=True)
merged=pd.concat([df1,df2],axis=1)
merged.to_csv(r"C:\Users\fatemeh.fereydouni\Desktop\extraction\normalisation\cummuns.csv", index=False, encoding="utf-8")
print("✅ Le fichier test.csv a été créé avec succès.")

