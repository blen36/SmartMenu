import os
from functools import lru_cache

import pandas as pd


@lru_cache(maxsize=1)
def load_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    path = os.path.join(base_dir, "data", "clean_recipes.csv")

    df = pd.read_csv(path)
    df = df.dropna()

    df = df.rename(
        columns={
            "Calories": "calories",
            "ProteinContent": "protein",
            "FatContent": "fat",
            "CarbohydrateContent": "carbs"
        }
    )

    df = df[["text", "calories", "protein", "fat", "carbs"]]

    df["text"] = df["text"].astype(str)
    df["calories"] = df["calories"].astype(float)
    df["protein"] = df["protein"].astype(float)
    df["fat"] = df["fat"].astype(float)
    df["carbs"] = df["carbs"].astype(float)

    return df