# apps/cashier_app/features/auth/vm.py

from .api import AuthAPI
from apps.cashier_app.app_state import state


class AuthVM:

    @staticmethod
    def login(username: str, password: str):
        response = AuthAPI.login(username, password)

        # Expected backend response:
        # {
        #   "access_token": "...",
        #   "token_type": "bearer",
        #   "user": {...}
        # }

        token = response.get("access_token")
        user = response.get("user")

        if not token or not user:
            raise Exception("Invalid login response from server.")

        state.set_session(token, user)