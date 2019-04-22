from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import discovery
from apiclient.http import MediaFileUpload
import os, json
from pathlib import Path
# 例外でなくwarningを抑止する際に利用
import warnings

# コンテンツのMediaType判定
import mimetypes

# 学習のため、簡単なクラスを作ります
class GoogleDriveUpload():
    def __init__(self, folder_id):
        self.set_service()
        self.upload_folder_id = 'folder_id'

    def set_service(self):
        # If modifying these scopes, delete the file token.json.
        SCOPES = 'https://www.googleapis.com/auth/drive.file'
        flags = tools.argparser.parse_args('--auth_host_name localhost --logging_level INFO'.split())
        warnings.filterwarnings('ignore')
        store = file.Storage('token.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store, flags)
        self.service = build('drive', 'v3', http=creds.authorize(Http()))

    # 一個づつアップロードする関数 / 基本はここがメイン
    def upload(self, filename, title, mediaType='application/pdf'):
        # ファイルのメタデータを設定
        file_metadata = {
            'name': title,
            'mimeType': mediaType,
            'parents': [self.upload_folder_id]
        }
        media = MediaFileUpload(str(filename),
                            mimetype='application/vnd.google-apps-document',
                               resumable=True)
        self.service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()

if __name__ == '__main__':
    googleDriveUpload = GoogleDriveUpload('1NtpUdK1CggdoUtR_RyYSN5diFmgFZXzc')
    googleDriveUpload.upload('filename.txt', 'title', 'text/plain')
