import requests


def search_recipes(query):

    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"

    response = requests.get(url)

    data = response.json()

    meals = data.get("meals")

    if not meals:
        return []

    results = []

    for meal in meals:

        results.append({
            "name": meal["strMeal"],
            "image": meal["strMealThumb"]
        })

    return results