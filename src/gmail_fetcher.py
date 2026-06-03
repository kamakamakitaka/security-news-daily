"""
Gmail API を使用して The Hacker News のメールを取得するモジュール
"""

import os
import base64
import pickle
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Gmail API のスコープ
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailFetcher:
    """Gmail からセキュリティニュースメールを取得するクラス"""
    
    def __init__(self, credentials_dir='credentials'):
        """
        初期化
        
        Args:
            credentials_dir: 認証情報を保存するディレクトリ
        """
        self.credentials_dir = credentials_dir
        self.creds = None
        self.service = None
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self):
        """Gmail API の認証を行う"""
        token_path = os.path.join(self.credentials_dir, 'token.pickle')
        creds_path = os.path.join(self.credentials_dir, 'credentials.json')
        
        # 既存のトークンを読み込む
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # 認証情報が無効な場合は再認証
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.logger.info("トークンを更新しています...")
                self.creds.refresh(Request())
            else:
                if not os.path.exists(creds_path):
                    raise FileNotFoundError(
                        f"認証情報ファイルが見つかりません: {creds_path}\n"
                        "Google Cloud Console で OAuth 2.0 クライアント ID を作成し、\n"
                        "credentials.json としてダウンロードしてください。"
                    )
                
                self.logger.info("新規認証を開始します...")
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)
            
            self.logger.info("認証が完了しました")
        
        # Gmail サービスを構築
        self.service = build('gmail', 'v1', credentials=self.creds)
        
    def fetch_latest_news(self, sender_email, hours_back=24):
        """
        指定した送信者からの最新メールを取得
        
        Args:
            sender_email: 送信者のメールアドレス
            hours_back: 何時間前までのメールを検索するか
            
        Returns:
            dict: メール情報 (subject, body, date, message_id)
        """
        try:
            # 検索クエリを構築
            after_date = datetime.now() - timedelta(hours=hours_back)
            after_timestamp = int(after_date.timestamp())
            
            query = f"from:{sender_email} after:{after_timestamp}"
            
            self.logger.info(f"メールを検索中: {query}")
            
            # メッセージ一覧を取得
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                self.logger.warning(f"過去{hours_back}時間以内にメールが見つかりませんでした")
                return None
            
            # 最新のメッセージを取得
            latest_message_id = messages[0]['id']
            message = self.service.users().messages().get(
                userId='me',
                id=latest_message_id,
                format='full'
            ).execute()
            
            # ヘッダー情報を解析
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # 本文を取得
            body = self._get_message_body(message['payload'])
            
            self.logger.info(f"メール取得成功: {subject}")
            
            return {
                'subject': subject,
                'body': body,
                'date': date,
                'message_id': latest_message_id,
                'raw_message': message
            }
            
        except HttpError as error:
            self.logger.error(f"Gmail API エラー: {error}")
            raise
    
    def _get_message_body(self, payload):
        """メール本文を再帰的に取得"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                body += self._get_message_body(part)
        else:
            if payload.get('mimeType') == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            elif payload.get('mimeType') == 'text/html':
                data = payload['body'].get('data', '')
                if data:
                    # HTMLの場合もデコード（後でクリーニングが必要）
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def extract_articles_from_email(self, email_body):
        """
        メール本文から記事URLとタイトルを抽出

        Args:
            email_body: メール本文

        Returns:
            list: 記事情報のリスト [{'title': ..., 'url': ...}, ...]
        """
        from bs4 import BeautifulSoup
        import re

        articles = []

        # HTMLをパース
        soup = BeautifulSoup(email_body, 'html.parser')

        # リンクを抽出（複数のドメインに対応）
        for link in soup.find_all('a', href=True):
            url = link['href']
            title = link.get_text(strip=True)

            # 無効なURL を除外: mailto, javascript, など
            if url.startswith('mailto:') or url.startswith('javascript:') or not url.startswith('http'):
                continue

            # セキュリティニュースサイトのURLパターン
            if any(domain in url for domain in ['thehackernews.com', 'securityweek.com', 'bleepingcomputer.com',
                                                   'zdnet.com', 'darkreading.com', 'infosecurity-magazine.com',
                                                   'inl03.netline.com', 'inl02.netline.com']):
                # タイトルが無効でない場合のみ追加
                # "Read More", "Download Now" などの generic text は除外
                if (title and len(title) > 10 and
                    title not in ['Read More', 'Download Now', 'click here', 'Unsubscribe']):
                    articles.append({
                        'title': title,
                        'url': url
                    })
        
        # 重複を削除
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        self.logger.info(f"{len(unique_articles)}件の記事を抽出しました")
        
        return unique_articles


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)
    
    fetcher = GmailFetcher()
    fetcher.authenticate()
    
    email_data = fetcher.fetch_latest_news("news@news.nl00.net", hours_back=48)
    
    if email_data:
        print(f"件名: {email_data['subject']}")
        print(f"日時: {email_data['date']}")
        
        articles = fetcher.extract_articles_from_email(email_data['body'])
        print(f"\n記事数: {len(articles)}")
        
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   {article['url']}")
