import pandas as pd
df = pd.read_csv("students.csv")
result = df.groupby("passed")["study_hours"].mean()
print(result)
print("관찰만 기록하고 인과관계로 단정하지 않습니다.")
