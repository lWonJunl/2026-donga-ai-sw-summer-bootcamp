import pandas as pd
df = pd.read_csv("students.csv")
print(df.head())
print(df.dtypes)
print(df.isna().sum())
