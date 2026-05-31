def calculate_targets(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str
) -> dict:
    """
    Расчет дневной нормы КБЖУ.
    Используется формула Mifflin-St Jeor.
    """

    activity_factors = {
        "low": 1.2,
        "sedentary": 1.2,

        "medium": 1.375,
        "light": 1.375,

        "high": 1.55,
        "moderate": 1.55,

        "very_high": 1.725
    }

    if gender == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    factor = activity_factors.get(activity_level, 1.2)
    tdee = bmr * factor

    if goal in ["lose", "lose_weight"]:
        calories = tdee - 400
        protein = weight * 2.0
    elif goal in ["gain", "gain_weight"]:
        calories = tdee + 300
        protein = weight * 2.1
    else:
        calories = tdee
        protein = weight * 1.7

    calories = max(calories, 1200)

    fat = weight * 0.8
    carbs = (calories - protein * 4 - fat * 9) / 4
    carbs = max(carbs, 80)

    return {
        "calories": round(calories, 1),
        "protein": round(protein, 1),
        "fat": round(fat, 1),
        "carbs": round(carbs, 1)
    }