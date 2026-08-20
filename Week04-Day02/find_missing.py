import pandas as pd
df = pd.read_csv("students.csv")
missing = df[df.isna().any(axis=1)]
print(missing[["student_id","study_hours","attendance"]])
