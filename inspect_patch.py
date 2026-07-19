import pandas as pd

df = pd.read_csv("app/ml/dataset/code_review_data_v2.csv")

print(df.loc[0, "patch"])