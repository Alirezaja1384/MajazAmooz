from model_bakery.baker import generators
from model_bakery.recipe import Recipe
from model_bakery.random_gen import gen_text
from exam.models import (
    Exam,
    Question,
    ExamLike,
    ExamParticipation,
    ParticipantAnswer,
)


generators.add("django_bleach.models.BleachField", gen_text)

exam = Recipe(
    Exam,
    ends_at=None,
    deadline_duration=None,
    correct_score=5,
    incorrect_score=-2,
    blank_score=1,
)
question = Recipe(Question)
exam_like = Recipe(ExamLike)
exam_participation = Recipe(ExamParticipation, deadline=None)
participant_answer = Recipe(ParticipantAnswer)
