from model_bakery.recipe import Recipe
from exam.models import (
    Exam,
    Question,
    ExamLike,
    ExamResult,
    ParticipantAnswer,
)


exam = Recipe(Exam)
question = Recipe(Question)
exam_like = Recipe(ExamLike)
exam_result = Recipe(ExamResult)
participant_answer = Recipe(ParticipantAnswer)
