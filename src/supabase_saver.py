"""
Supabase にセキュリティニュース記事を保存するモジュール
"""

import os
import logging
from datetime import datetime
from supabase import create_client, Client

class SupabaseSaver:
    """Supabase にデータを保存するクラス"""

    def __init__(self, url=None, key=None):
        """
        初期化

        Args:
            url: Supabase Project URL
            key: Supabase anon public key
        """
        self.url = url or os.environ.get('SUPABASE_URL')
        self.key = key or os.environ.get('SUPABASE_KEY')
        self.logger = logging.getLogger(__name__)

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL と SUPABASE_KEY 環境変数が必要です")

        self.client: Client = create_client(self.url, self.key)

    def save_article(self, article_data, analysis_text, keywords=None):
        """
        記事を Supabase に保存

        Args:
            article_data: 記事データ（title, url など）
            analysis_text: Claude の解説テキスト
            keywords: キーワードリスト

        Returns:
            dict: 保存されたデータ
        """
        try:
            # キーワードを抽出（簡易版）
            if keywords is None:
                keywords = self._extract_keywords(analysis_text)

            # 保存データを準備
            data = {
                'title': article_data.get('title'),
                'url': article_data.get('url'),
                'analysis': analysis_text,
                'keywords': keywords,
                'date': datetime.now().isoformat()
            }

            # Supabase に挿入
            response = self.client.table('articles').insert(data).execute()

            self.logger.info(f"Supabase に保存成功: {article_data['title']}")

            return response.data[0] if response.data else None

        except Exception as e:
            self.logger.error(f"Supabase 保存エラー: {e}")
            raise

    def _extract_keywords(self, text):
        """テキストからキーワードを抽出"""
        keywords = []
        important_terms = [
            'vulnerability', 'exploit', 'malware', 'ransomware', 'phishing',
            'zero-day', 'CVE', 'patch', 'breach', 'leak', 'attack',
            'backdoor', 'trojan', 'botnet', 'DDoS', 'SQL injection',
            'XSS', 'CSRF', 'authentication', 'encryption', 'firewall',
            'APT', 'threat', 'credential', 'password', 'data'
        ]

        text_lower = text.lower()
        for term in important_terms:
            if term.lower() in text_lower:
                keywords.append(term)

        return keywords[:10]

    def search_by_keyword(self, keyword):
        """キーワードで記事を検索"""
        try:
            response = self.client.table('articles').select('*').ilike(
                'title', f'%{keyword}%'
            ).execute()

            self.logger.info(f"{len(response.data)}件の記事を検出: {keyword}")

            return response.data

        except Exception as e:
            self.logger.error(f"検索エラー: {e}")
            return []

    def search_by_date_range(self, start_date, end_date):
        """期間で記事を検索"""
        try:
            response = self.client.table('articles').select('*').gte(
                'date', start_date
            ).lte(
                'date', end_date
            ).order('date', desc=True).execute()

            self.logger.info(f"{len(response.data)}件の記事を検出: {start_date} ～ {end_date}")

            return response.data

        except Exception as e:
            self.logger.error(f"検索エラー: {e}")
            return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    saver = SupabaseSaver()

    # テスト
    test_data = {
        'title': 'Test Article',
        'url': 'https://example.com/test'
    }

    result = saver.save_article(test_data, 'This is a test analysis.')
    print(f"Saved: {result}")
