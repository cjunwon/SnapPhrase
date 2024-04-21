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
from .states.baseState import State
# from .states.uploadState import UploadState

import reflex_webcam as webcam

from sqlmodel import Field, Session, SQLModel, create_engine 

# CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

engine = create_engine("sqlite:///reflex.db", echo=True)
SQLModel.metadata.create_all(engine)

# Identifies a particular webcam component in the DOM
WEBCAM_REF = "webcam"

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
                rx.button("Host A New Game", on_click=State.new_game()),
                rx.cond(State.game_settings, 
                    rx.select(
                        ['Afar', 'Abkhazian', 'Afrikaans', 'Akan', 'Albanian', 'Amharic', 'Arabic', 'Aragonese', 'Armenian', 'Assamese', 'Avaric', 'Avestan', 'Aymara', 'Azerbaijani', 'Bashkir', 'Bambara', 'Basque', 'Belarusian', 'Bengali', 'Bihari languages', 'Bislama', 'Tibetan', 'Bosnian', 'Breton', 'Bulgarian', 'Burmese', 'Catalan; Valencian', 'Czech', 'Chamorro', 'Chechen', 'Chinese', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic', 'Chuvash', 'Cornish', 'Corsican', 'Cree', 'Welsh', 'Czech', 'Danish', 'German', 'Divehi; Dhivehi; Maldivian', 'Dutch; Flemish', 'Dzongkha', 'Greek, Modern (1453-)', 'English', 'Esperanto', 'Estonian', 'Basque', 'Ewe', 'Faroese', 'Persian', 'Fijian', 'Finnish', 'French', 'Western Frisian', 'Fulah', 'Georgian', 'German', 'Gaelic; Scottish Gaelic', 'Irish', 'Galician', 'Manx', 'Greek, Modern (1453-)', 'Guarani', 'Gujarati', 'Haitian; Haitian Creole', 'Hausa', 'Hebrew', 'Herero', 'Hindi', 'Hiri Motu', 'Croatian', 'Hungarian', 'Armenian', 'Igbo', 'Icelandic', 'Ido', 'Sichuan Yi; Nuosu', 'Inuktitut', 'Interlingue; Occidental', 'Interlingua (International Auxiliary Language Association)', 'Indonesian', 'Inupiaq', 'Icelandic', 'Italian', 'Javanese', 'Japanese', 'Kalaallisut; Greenlandic', 'Kannada', 'Kashmiri', 'Georgian', 'Kanuri', 'Kazakh', 'Central Khmer', 'Kikuyu; Gikuyu', 'Kinyarwanda', 'Kirghiz; Kyrgyz', 'Komi', 'Kongo', 'Korean', 'Kuanyama; Kwanyama', 'Kurdish', 'Lao', 'Latin', 'Latvian', 'Limburgan; Limburger; Limburgish', 'Lingala', 'Lithuanian', 'Luxembourgish; Letzeburgesch', 'Luba-Katanga', 'Ganda', 'Macedonian', 'Marshallese', 'Malayalam', 'Maori', 'Marathi', 'Malay', 'Micmac', 'Macedonian', 'Malagasy', 'Maltese', 'Mongolian', 'Maori', 'Malay', 'Burmese', 'Nauru', 'Navajo; Navaho', 'Ndebele, South; South Ndebele', 'Ndebele, North; North Ndebele', 'Ndonga', 'Nepali', 'Dutch; Flemish', 'Norwegian Nynorsk; Nynorsk, Norwegian', 'Bokmål, Norwegian; Norwegian Bokmål', 'Norwegian', 'Occitan (post 1500)', 'Ojibwa', 'Oriya', 'Oromo', 'Ossetian; Ossetic', 'Panjabi; Punjabi', 'Persian', 'Pali', 'Polish', 'Portuguese', 'Pushto; Pashto', 'Quechua', 'Romansh', 'Romanian; Moldavian; Moldovan', 'Romanian; Moldavian; Moldovan', 'Rundi', 'Russian', 'Sango', 'Sanskrit', 'Sinhala; Sinhalese', 'Slovak', 'Slovak', 'Slovenian', 'Northern Sami', 'Samoan', 'Shona', 'Sindhi', 'Somali', 'Sotho, Southern', 'Spanish; Castilian', 'Albanian', 'Sardinian', 'Serbian', 'Swati', 'Sundanese', 'Swahili', 'Swedish', 'Tahitian', 'Tamil', 'Tatar', 'Telugu', 'Tajik', 'Tagalog', 'Thai', 'Tibetan', 'Tigrinya', 'Tonga (Tonga Islands)', 'Tswana', 'Tsonga', 'Turkmen', 'Turkish', 'Twi', 'Uighur; Uyghur', 'Ukrainian', 'Urdu', 'Uzbek', 'Venda', 'Vietnamese', 'Volapük', 'Welsh', 'Walloon', 'Wolof', 'Xhosa', 'Yiddish', 'Yoruba', 'Zhuang; Chuang', 'Chinese', 'Zulu'],
                        placeholder="Choose your language",
                        name="Languages",
                    )
                ),
                # Join existing game form
                rx.button("Join A Game", on_click=State.search_game()),
                rx.cond(State.find_game, rx.input(
                    placeholder="Enter your unique PLeague code",
                    name="PLeague Code",
                )),
                rx.button("Submit", type="submit"),
                rx.button("Generate Theme and Count", on_click=State.gen_theme_count()),
                rx.link(
                    rx.button("Submit", type="submit"),
                href="/protected/upload")
            ),
            on_submit=State.handle_submit,
            reset_on_submit=True,
        ),
        rx.divider(),
        rx.heading("Results"),
        rx.text(State.form_data.to_string()),
    )


# Camera Upload widget

def last_screenshot_widget() -> rx.Component:
    """Widget for displaying the last screenshot and timestamp."""
    return rx.box(
        rx.cond(
            State.last_screenshot,
            rx.fragment(
                rx.image(src=State.last_screenshot),
                rx.text(State.last_screenshot_timestamp),
            ),
            rx.center(
                rx.text("Click image to capture.", size="4"),
                ),
        ),
        height="270px",
    )

def webcam_upload_component(ref: str) -> rx.Component:
    """Component for displaying webcam preview and uploading screenshots.
    Args:
        ref: The ref of the webcam component.
    Returns:
        A reflex component.
    """
    return rx.vstack(
        webcam.webcam(
            id=ref,
            on_click=webcam.upload_screenshot(
                ref=ref,
                handler=State.handle_screenshot,  # type: ignore
            ),
        ),
        last_screenshot_widget(),
        width="320px",
        align="center",
    )

@rx.page(route="/protected/upload")
@require_google_login
def upload() -> rx.Component:
    return rx.fragment(
        rx.center(
            webcam_upload_component(WEBCAM_REF),
            padding_top="3em",
        ),
    )

app = rx.App()
app.add_page(index)
app.add_page(upload, route="/protected/upload")
