from typing import Optional
import functools
import json
import os
import time
import reflex as rx
from db_model import User
CLIENT_ID = '453147289562-jkgjib093hs0c0r61n6nkgbbp47kgr2m.apps.googleusercontent.com'
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

class State(rx.State):
    id_token_json: str = rx.LocalStorage()
    # user: Optional[User] = None


    def find_user(self, email: str):
        with rx.session() as session:
            print("\n"*5 + f"email: {email}" + "\n"*5)
            return session.get(User, self.tokeninfo["email"])

    def on_success(self, id_token: dict):
        self.id_token_json = json.dumps(id_token)
        if not self.find_user(self.tokeninfo["email"]):
            with rx.session() as session:
                user = User(
                    name=self.tokeninfo["name"],
                    email=self.tokeninfo["email"],
                    score=0,
                )
                session.add(user)
                session.commit()
        print(f"Logged in as {self.tokeninfo['name']}")
        return None

    @rx.cached_var
    def tokeninfo(self) -> dict[str, str]:
        try:
            return verify_oauth2_token(
                json.loads(self.id_token_json)["credential"],
                requests.Request(),
                CLIENT_ID,
            )
        except Exception as exc:
            if self.id_token_json:
                print(f"Error verifying token: {exc}")
        return {}

    def logout(self):
        self.id_token_json = ""

    @rx.var
    def token_is_valid(self) -> bool:
        try:
            return bool(
                self.tokeninfo
                and int(self.tokeninfo.get("exp", 0)) > time.time()
            )
        except Exception:
            return False

    @rx.cached_var
    def protected_content(self) -> str:
        if self.token_is_valid:
            return f"This content can only be viewed by a logged in User. Nice to see you {self.tokeninfo['name']}"
        return "Not logged in."
    
    