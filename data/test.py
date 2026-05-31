import pandas as pd
df1 = pd.read_csv('recipes_clean.csv')
print(df1.head())
print(df1.describe())
print(df1.columns.to_list())
print(df1.info())

df2 = pd.read_csv('clean_recipes.csv')
print(df2.head())
print(df2.describe())
print(df2.columns.to_list())
print(df2.info())