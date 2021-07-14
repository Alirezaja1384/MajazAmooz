from model_bakery.recipe import Recipe
from model_bakery.random_gen import gen_string
from shared.models import ConfirmStatusChoices
from learning.models import Category, Tutorial, TutorialComment

# Category recipes
category = Recipe(Category)
active_category = category.extend(is_active=True)
inactive_category = category.extend(is_active=False)

# Tutorial recipes
tutorial = Recipe(
    Tutorial,
    short_description=gen_string(50),
    body=gen_string(150),
    _fill_optional=["author"],
)
confirmed_tutorial = tutorial.extend(
    confirm_status=ConfirmStatusChoices.CONFIRMED
)
waiting_for_confirm_tutorial = tutorial.extend(
    confirm_status=ConfirmStatusChoices.WAITING_FOR_CONFIRM
)
disproved_tutorial = tutorial.extend(
    confirm_status=ConfirmStatusChoices.DISPROVED
)

# TutorialComment recipes
tutorial_comment = Recipe(
    TutorialComment,
    body=gen_string(150),
    _fill_optional=["user"],
)
confirmed_tutorial_comment = tutorial_comment.extend(
    confirm_status=ConfirmStatusChoices.CONFIRMED
)
disproved_tutorial_comment = tutorial_comment.extend(
    confirm_status=ConfirmStatusChoices.DISPROVED
)
