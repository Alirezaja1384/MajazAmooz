"""TypedDict classes used in this project"""
from typing import TypedDict


class TutorialStatistics(TypedDict):
    """Tutorial statistics typed dict including tutorials_count,
    likes_count, views_count and comments_count.
    """

    tutorials_count: int
    likes_count: int
    views_count: int
    comments_count: int
