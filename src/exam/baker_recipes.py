from model_bakery.recipe import Recipe
from exam.models import Exam, Question, ExamResult


exam = Recipe(Exam)
question = Recipe(Question)
exam_result = Recipe(ExamResult)
