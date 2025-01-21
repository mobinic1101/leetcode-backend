from django.test import TestCase
from httpx import Client

client = Client(base_url="http://localhost:8000/api")
get_authorization_header = lambda token: {"Authorization": f"Token {token}"}


# Create your tests here.
class TestMyDetail(TestCase):
    path = "/users/me/"

    def test_update_user_detail(self):
        data = {"username": "mobinic1101", "first_name": "mobincc"}
        files = {"profile_pic": open("/home/mobin/Downloads/mobin_pic.jpg", "rb")}

        response = client.post(
            self.path,
            data=data,
            files=files,
            headers=get_authorization_header(
                "092ece797b5e4fa88e94fb89b2757a80749b99fd"
            ),
        )
        self.assertEqual(response.status_code, 200)

        data = {"username": "mobinic1101", "first_name": "mobin"}
        response = client.post(
            self.path,
            data=data,
            files=files,
            headers=get_authorization_header(
                "092ece797b5e4fa88e94fb89b2757a80749b99fd"
            ),
        )
        self.assertEqual(response.status_code, 200)

