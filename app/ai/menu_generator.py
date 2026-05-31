import requests
from app.ai.menu_optimizer import select_best_foods


days = [
    "Monday","Tuesday","Wednesday",
    "Thursday","Friday","Saturday","Sunday"
]

meals = [
    ("Breakfast",0.25),
    ("Lunch",0.35),
    ("Dinner",0.30),
    ("Snack",0.10)
]


def search_real_recipe(query):

    url=f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"

    r=requests.get(url)
    data=r.json()

    if not data["meals"]:
        return None

    meal=data["meals"][0]

    return {
        "name":meal["strMeal"],
        "id":meal["idMeal"],
        "image":meal["strMealThumb"]
    }


def generate_week_menu(df,targets):

    menu=[]

    for day in days:

        for meal_name,ratio in meals:

            target_calories=targets["calories"]*ratio
            target_protein=targets["protein"]*ratio
            target_fat=targets["fat"]*ratio
            target_carbs=targets["carbs"]*ratio

            food=select_best_foods(
                df,
                target_calories,
                target_protein,
                target_fat,
                target_carbs
            )

            query=food["text"].split()[0]

            recipe=search_real_recipe(query)

            if recipe:

                menu.append({
                    "day":day,
                    "meal":meal_name,
                    "name":recipe["name"],
                    "recipe_id":recipe["id"],
                    "calories":food["calories"],
                    "protein":food["protein"],
                    "fat":food["fat"],
                    "carbs":food["carbs"]
                })

    return menu