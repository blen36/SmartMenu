from app.ai.recommender import get_similar_recipe_names

print(get_similar_recipe_names(["chicken"], top_n=5))