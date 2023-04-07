from django.test import TestCase


class TestSendNotification(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    # def test_send_firebase_notification(self):
    #     res = send_bulk_message(
    #         registration_ids=["4"], data={"title": "hello test"}, cloud_type="FCM"
    #     )
    #     return res
