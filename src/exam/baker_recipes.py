from model_bakery.baker import generators
from model_bakery.recipe import Recipe
from model_bakery.random_gen import gen_text
from exam.models import (
    Exam,
    Question,
    ExamLike,
    ExamResult,
    ParticipantAnswer,
)


generators.add("django_bleach.models.BleachField", gen_text)

exam = Recipe(Exam)
question = Recipe(Question)
exam_like = Recipe(ExamLike)
exam_result = Recipe(ExamResult)
participant_answer = Recipe(ParticipantAnswer)
