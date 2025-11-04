import pandas as pd

df1 = pd.read_csv(
    r"C:\Users\fatemeh.fereydouni\Desktop\extraction\premiere_entreprise_par_page.csv",
    encoding="cp1252")
print(df1.head())
df1.info()
df2=df1[["dirigeant"]].drop_duplicates().reset_index(drop=True)
df2.to_csv(r"C:\Users\fatemeh.fereydouni\Desktop\extraction\normalisation\dirigeants.csv", index=False, encoding="utf-8")
print("✅ Le fichier test.csv a été créé avec succès.")