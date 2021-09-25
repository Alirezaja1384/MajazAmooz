from django.db.models import Q
from shared.models import ConfirmStatusChoices


_ACTIVE_CONFIRMED_FILTERS = {
    "is_active": True,
    "confirm_status": ConfirmStatusChoices.CONFIRMED,
}


def get_active_confirmed_filters(rel_name: str = "") -> Q:
    """Makes active and confirmed filters by given relation name.

    Args:
        rel_name (str, optional): Relation name to apply filter on it.
            Defaults to "".

    Returns:
        Q: Generated active and confirmed filters to apply on queryset.
    """
    return Q(
        **(
            _ACTIVE_CONFIRMED_FILTERS
            if not rel_name
            else {
                f"{rel_name}__{key}": val
                for key, val in _ACTIVE_CONFIRMED_FILTERS.items()
            }
        )
    )


__all__ = ["get_active_confirmed_filters"]
