from http import HTTPStatus
from unittest import mock
from typing import Optional, Dict
from django.db import DatabaseError
from django.test import TestCase, RequestFactory
from django.http import HttpRequest, HttpResponse
from .views import shared as shared_views


def ajax_request(data: Optional[Dict] = None) -> HttpRequest:
    factory = RequestFactory()
    request = factory.post(
        "/",
        data=data or dict(),
        content_type="application/json",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    return request


@mock.patch.multiple(
    shared_views, logger=mock.DEFAULT, transaction=mock.DEFAULT
)
class AjaxViewTest(TestCase):
    class TestAjaxView(shared_views.AjaxView):
        def db_operation(self):
            return HttpResponse(status=200)

    class TestBrokenAjaxView(shared_views.AjaxView):
        db_error_default_text = "Default error text"

        def db_operation(self):
            raise DatabaseError

    def test_get_request_data(self, **_):
        """get_request_data should return sent data as dictionary."""
        data = {"key": "value"}

        view = self.TestAjaxView()
        view.setup(ajax_request(data))

        view_data = view.get_request_data()
        self.assertEqual(view_data, data)

    def test_non_ajax_request_status_bad_request(self, **_):
        """Should return BAD_REQUEST response (status code: 400)
        for non-ajax requests.
        """
        request = RequestFactory().post("/")
        view = self.TestAjaxView.as_view()

        self.assertEqual(view(request).status_code, HTTPStatus.BAD_REQUEST)

    def test_ajax_request_status_ok(self, **_):
        """Should return OK response (status code: 200) for ajax requests."""
        request = ajax_request()
        view = self.TestAjaxView.as_view()

        self.assertEqual(view(request).status_code, HTTPStatus.OK)

    def test_broken_db_operation_rollback(
        self, transaction: mock.MagicMock, **_
    ):
        """Should rollback database operation when db_operation()
        raises DatabaseError.

        Args:
            transaction (mock.MagicMock): Mocked transaction module.
        """
        self.TestBrokenAjaxView.as_view()(ajax_request())
        savepoint = transaction.savepoint.return_value

        transaction.rollback.assert_called_with(savepoint)

    def test_broken_log_error(self, logger: mock.MagicMock, **_):
        """Should log error when db_operation() raises DatabaseError.

        Args:
            logger (mock.MagicMock): Mocked logger variable.
        """
        self.TestBrokenAjaxView.as_view()(ajax_request())
        self.assertTrue(logger.error.called)

    def test_broken_response_error_status(self, **_):
        """Should return error status when db_operation() raises DatabaseError.
        Also should use db_error_default_text as error descreption.
        """
        response = self.TestBrokenAjaxView.as_view()(ajax_request())

        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {
                "status": shared_views.InsertOrDeleteStatus.ERROR,
                "error": self.TestBrokenAjaxView.db_error_default_text,
            },
        )
