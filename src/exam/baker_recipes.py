from model_bakery.recipe import Recipe
from exam.models import Exam, Question

exam = Recipe(Exam)
question = Recipe(Question)
