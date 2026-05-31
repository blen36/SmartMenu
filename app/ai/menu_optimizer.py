import numpy as np


def select_best_foods(df, target_calories, target_protein, target_fat, target_carbs):

    best_score = 999999
    best_food = None

    foods = df.sample(min(300, len(df)))

    for _, row in foods.iterrows():

        score = 0

        score += abs(row["calories"] - target_calories)
        score += abs(row["protein"] - target_protein) * 3
        score += abs(row["fat"] - target_fat) * 2
        score += abs(row["carbs"] - target_carbs)

        if score < best_score:
            best_score = score
            best_food = row

    return best_food