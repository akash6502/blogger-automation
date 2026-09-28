import os
from urllib.parse import urlparse

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from config import Config
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/blogger']
TOKEN_FILE = "token.json"


class ReauthRequired(Exception):
    """Saved Google credentials are missing or can no longer be refreshed."""


def _discard_token():
    try:
        os.remove(TOKEN_FILE)
    except FileNotFoundError:
        pass


def _save_credentials(creds):
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())


def _flow(redirect_uri, state=None, code_verifier=None):
    kwargs = {"redirect_uri": redirect_uri}
    if state is not None:
        kwargs["state"] = state
    if code_verifier is not None:
        kwargs["code_verifier"] = code_verifier
    return Flow.from_client_secrets_file(
        Config.CLIENT_SECRET_FILE,
        scopes=SCOPES,
        **kwargs,
    )


def begin_authorization(redirect_uri):
    flow = _flow(redirect_uri)
    authorization_url, state = flow.authorization_url(prompt="consent")
    return authorization_url, state, flow.code_verifier


def finish_authorization(redirect_uri, authorization_response, state, code_verifier):
    parsed = urlparse(authorization_response)
    if parsed.scheme == "http" and parsed.hostname in ("localhost", "127.0.0.1"):
        # Desktop OAuth returns to this local http server. oauthlib blocks that
        # unless this flag is set for the code exchange.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    flow = _flow(redirect_uri, state=state, code_verifier=code_verifier)
    flow.fetch_token(authorization_response=authorization_response)
    _save_credentials(flow.credentials)


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except (ValueError, OSError) as exc:
            _discard_token()
            raise ReauthRequired("Google authorization required") from exc

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError as exc:
            _discard_token()
            raise ReauthRequired("Google authorization expired") from exc
        _save_credentials(creds)
        return creds

    _discard_token()
    raise ReauthRequired("Google authorization required")

def get_service():
    creds = get_credentials()
    return build("blogger", "v3", credentials=creds)

def publish_post(title, content):
    service = get_service()

    post = {
        "title": title,
        "content": content
    }

    posted = service.posts().insert(
        blogId=Config.BLOG_ID,
        body=post
    ).execute()

    return posted

def update_post(post_id, title, content):
    service = get_service()

    post = {
        "id": post_id,
        "title": title,
        "content": content
    }

    return service.posts().update(
        blogId=Config.BLOG_ID,
        postId=post_id,
        body=post
    ).execute()

