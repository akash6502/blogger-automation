import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from config import Config
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0) 
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

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

