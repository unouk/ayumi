import asyncio
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from dependencies.queue import ShortMemoryChat
import time


CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

async def read_messages(youtube, livechat_id, memory):
    request = youtube.liveChatMessages().list(
        liveChatId=livechat_id,
        part='snippet,authorDetails',
        maxResults=1
    )
    prev_message = {"author": "", "message": ""}
    while True:
        response = request.execute()
        message = {"author": "", "message": ""}
        if response['items']:
            message['author'] = response['items'][0]['authorDetails']['displayName']
            message['message'] = response['items'][0]['snippet']['displayMessage']
            next_page_token = response['nextPageToken']
            print(message)
            if message != prev_message:
                memory.enqueue(date=time.strftime('%Y-%m-%d %H:%M:%S'),
                            author=message['author'],
                            message=message['message'],
                            timestamp=time.time())
                prev_message = message

        await asyncio.sleep(3)
        request = youtube.liveChatMessages().list(
            liveChatId=livechat_id,
            part='snippet,authorDetails',
            maxResults=1,
            pageToken=next_page_token
        )
            


if __name__ == '__main__':
    memory = ShortMemoryChat('messages')
    youtube = get_authenticated_service()
    request = youtube.liveBroadcasts().list(
        part='snippet',
        broadcastStatus="all",
        broadcastType="all"
    )
    response = request.execute()
    livechat_id = response['items'][0]['snippet']['liveChatId']

    request = youtube.liveChatMessages().list(
        liveChatId=livechat_id,
        part='snippet,authorDetails',
        maxResults=1
    )
    asyncio.run(read_messages(youtube, livechat_id, memory))

