from model_bakery.recipe import Recipe
from model_bakery.random_gen import gen_string
from learning.models import Category, Tutorial


active_category = Recipe(Category, is_active=True)
inactive_category = Recipe(Category, is_active=False)

tutorial = Recipe(
    Tutorial, short_description=gen_string(50), body=gen_string(150)
)
