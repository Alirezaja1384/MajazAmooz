import random
from model_bakery.recipe import Recipe
from model_bakery.random_gen import gen_string
from shared.models import ConfirmStatusChoices
from learning.models import Category, Tutorial, TutorialComment


def get_random_confirm_status():
    return random.choice(
        [
            ConfirmStatusChoices.CONFIRMED,
            ConfirmStatusChoices.WAITING_FOR_CONFIRM,
            ConfirmStatusChoices.DISPROVED,
        ]
    )


# Category recipes
category = Recipe(Category)
active_category = category.extend(is_active=True)
inactive_category = category.extend(is_active=False)

# Tutorial recipes
tutorial = Recipe(
    Tutorial,
    short_description=lambda: gen_string(150),
    body=lambda: gen_string(150),
    confirm_status=get_random_confirm_status,
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
    body=lambda: gen_string(150),
    tutorial=tutorial.make,
    confirm_status=get_random_confirm_status,
    _fill_optional=["user"],
)
confirmed_tutorial_comment = tutorial_comment.extend(
    confirm_status=ConfirmStatusChoices.CONFIRMED
)
waiting_for_confirm_tutorial_comment = tutorial_comment.extend(
    confirm_status=ConfirmStatusChoices.WAITING_FOR_CONFIRM
)
disproved_tutorial_comment = tutorial_comment.extend(
    confirm_status=ConfirmStatusChoices.DISPROVED
)
