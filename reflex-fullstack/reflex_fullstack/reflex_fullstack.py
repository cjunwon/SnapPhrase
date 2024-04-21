CLIENT_ID = '453147289562-jkgjib093hs0c0r61n6nkgbbp47kgr2m.apps.googleusercontent.com'

import functools
import json
import os
import time

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

import reflex as rx

from .react_oauth_google import GoogleOAuthProvider, GoogleLogin

from db_model import *
from .states.baseState import State, FormState

from sqlmodel import Field, SQLModel, create_engine 

# CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

engine = create_engine("sqlite:///reflex.db", echo=True)
SQLModel.metadata.create_all(engine)


def user_info(tokeninfo: dict) -> rx.Component:
    return rx.hstack(
        rx.avatar(
            name=tokeninfo["name"],
            src=tokeninfo["picture"],
            size="8",
        ),
        rx.vstack(
            rx.heading(tokeninfo["name"], size="5"),
            rx.text(tokeninfo["email"]),
            align_items="flex-start",
        ),
        rx.button("Logout", on_click=State.logout),
        padding="10px",
    )


def login() -> rx.Component:
    return rx.vstack(
        GoogleLogin.create(on_success=State.on_success),
    )


def require_google_login(page) -> rx.Component:
    @functools.wraps(page)
    def _auth_wrapper() -> rx.Component:
        return GoogleOAuthProvider.create(
            rx.cond(
                State.is_hydrated,
                rx.cond(State.token_is_valid, page(), login()),
                # rx.spinner(),
            ),
            client_id=CLIENT_ID,
        )
    return _auth_wrapper


def index():
    return rx.vstack(
        rx.heading("Let's go SnapPhrase", size="8"),
        rx.link("GO", href="/protected"),
    )



@rx.page(route="/protected")
@require_google_login
def protected() -> rx.Component:

    return rx.vstack(
        user_info(State.tokeninfo),
        rx.text(State.protected_content),
        rx.link("Home", href="/"),
        rx.form(
            rx.vstack(
                # Host new game form
                rx.button("Host A New Game", on_click=FormState.new_game()),
                rx.cond(FormState.game_settings, 
                    rx.select(
                        ["Corey", "Spen", "Fhranz", "Eadale", "Chaainis"],
                        placeholder="Choose your language",
                        name="Languages",
                    )
                ),
                # Join existing game form
                rx.button("Join A Game", on_click=FormState.search_game()),
                rx.cond(FormState.find_game, rx.input(
                    placeholder="Enter your unique PLeague code",
                    name="PLeague Code",
                )),
                rx.button("Submit", type="submit"),
            ),
            on_submit=FormState.handle_submit,
            reset_on_submit=True,
        ),
        rx.divider(),
        rx.heading("Results"),
        rx.text(FormState.form_data.to_string()),
    )


app = rx.App()
app.add_page(index)
