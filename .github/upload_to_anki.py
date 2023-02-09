"""Upload built addon to the Anki."""
import os
from pathlib import Path

from webbot import Browser


def upload(ankiweb_username: str, ankiweb_password: str):
    """Upload built addon to the Anki."""
    web = Browser(showWindow=False)
    web.go_to("https://ankiweb.net/shared/upload")
    web.type(ankiweb_username, into="username")
    web.type(ankiweb_password, into="password")
    web.press(web.Key.ENTER)

    web.go_to(f"https://ankiweb.net/shared/upload?id=1885151920")

    web.type("Czech Plus: Addon for professional Czech words learning!", into="title")
    web.type("https://github.com/PerchunPak/czech-plus/issues", into="support url")

    web.type(str(Path("./czech-plus.ankiaddon").absolute()), id="v21file0")

    web.type("""Please see https://github.com/PerchunPak/czech-plus/#readme.""", id="desc")

    web.type("czech", into="tags")

    web.click("Update")


if __name__ == "__main__":
    upload(os.environ["ANKI_USERNAME"], os.environ["ANKI_PASSWORD"])
