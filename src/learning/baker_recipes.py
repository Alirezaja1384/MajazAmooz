from model_bakery.recipe import Recipe
from learning.models import Category


active_category = Recipe(Category, is_active=True)
inactive_category = Recipe(Category, is_active=False)
