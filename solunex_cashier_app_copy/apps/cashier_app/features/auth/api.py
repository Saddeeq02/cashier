# apps/cashier_app/features/auth/api.py


from shared.api.client import client


class AuthAPI:

    @staticmethod
    def login(username: str, password: str):
        return client.post(
            "/api/auth/login",
            json={
                "username": username,
                "password": password
            }
        )