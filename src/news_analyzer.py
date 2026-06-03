"""
セキュリティニュース解析・解説エンジン
Anthropic Claude API を使用して高校生レベルでわかりやすく解説
"""

import os
import json
import logging
from datetime import datetime
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup


class NewsAnalyzer:
    """セキュリティニュース解析クラス"""
    
    def __init__(self, api_key=None, archive_dir='archive'):
        """
        初期化
        
        Args:
            api_key: Anthropic API キー(環境変数 ANTHROPIC_API_KEY から取得)
            archive_dir: 過去記事アーカイブディレクトリ
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY 環境変数が設定されていません")
        
        self.client = Anthropic(api_key=self.api_key)
        self.archive_dir = archive_dir
        self.logger = logging.getLogger(__name__)
        
        # アーカイブディレクトリが存在しない場合は作成
        os.makedirs(self.archive_dir, exist_ok=True)
    
    def fetch_article_content(self, url):
        """
        記事URLから本文を取得
        
        Args:
            url: 記事URL
            
        Returns:
            str: 記事本文
        """
        try:
            self.logger.info(f"記事を取得中: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # The Hacker News の記事本文を抽出
            # 通常は <div class="articlebody"> に本文が含まれる
            article_body = soup.find('div', class_='articlebody')
            
            if not article_body:
                # フォールバック: <article> タグを探す
                article_body = soup.find('article')
            
            if article_body:
                # テキストを抽出(段落ごとに改行)
                paragraphs = article_body.find_all(['p', 'h2', 'h3', 'ul', 'ol'])
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
                return content
            else:
                self.logger.warning("記事本文を抽出できませんでした")
                return ""
                
        except Exception as e:
            self.logger.error(f"記事取得エラー: {e}")
            return ""
    
    def search_past_articles(self, keywords, limit=3):
        """
        過去の解説から関連記事を検索
        
        Args:
            keywords: 検索キーワードリスト
            limit: 最大検索数
            
        Returns:
            list: 関連記事のリスト
        """
        related_articles = []
        
        try:
            # アーカイブディレクトリ内のJSONファイルを検索
            archive_files = sorted(
                [f for f in os.listdir(self.archive_dir) if f.endswith('.json')],
                reverse=True  # 新しい順
            )
            
            for filename in archive_files[:30]:  # 最新30件を検索対象
                filepath = os.path.join(self.archive_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    article_data = json.load(f)
                
                # キーワードマッチング(タイトルまたは解説本文)
                title = article_data.get('title', '').lower()
                analysis = article_data.get('analysis', '').lower()
                
                match_score = 0
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower in title:
                        match_score += 3
                    if keyword_lower in analysis:
                        match_score += 1
                
                if match_score > 0:
                    related_articles.append({
                        'date': article_data.get('date'),
                        'title': article_data.get('title'),
                        'summary': analysis[:200] + '...',
                        'score': match_score
                    })
            
            # スコア順にソート
            related_articles.sort(key=lambda x: x['score'], reverse=True)
            
            return related_articles[:limit]
            
        except Exception as e:
            self.logger.error(f"過去記事検索エラー: {e}")
            return []
    
    def analyze_article(self, article_title, article_url, article_content):
        """
        記事を解析・解説
        
        Args:
            article_title: 記事タイトル
            article_url: 記事URL
            article_content: 記事本文
            
        Returns:
            str: 解説文(Markdown形式)
        """
        self.logger.info(f"記事を解析中: {article_title}")
        
        # キーワード抽出(簡易版)
        keywords = self._extract_keywords(article_title)
        
        # 過去記事を検索
        past_articles = self.search_past_articles(keywords)
        
        # プロンプトを構築
        prompt = self._build_analysis_prompt(
            article_title,
            article_url,
            article_content,
            past_articles
        )
        
        try:
            # Claude APIで解析
            message = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=8000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            analysis = message.content[0].text
            
            self.logger.info("解析が完了しました")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Claude API エラー: {e}")
            raise
    
    def _extract_keywords(self, text):
        """テキストから重要なキーワードを抽出"""
        # セキュリティ関連の重要キーワードリスト
        important_terms = [
            'vulnerability', 'exploit', 'malware', 'ransomware', 'phishing',
            'zero-day', 'CVE', 'patch', 'breach', 'leak', 'attack',
            'backdoor', 'trojan', 'botnet', 'DDoS', 'SQL injection',
            'XSS', 'CSRF', 'authentication', 'encryption', 'firewall',
            'APT', 'threat', 'credential', 'password', 'data'
        ]
        
        text_lower = text.lower()
        keywords = []
        
        for term in important_terms:
            if term.lower() in text_lower:
                keywords.append(term)
        
        # 企業名やプロダクト名も抽出(大文字で始まる単語)
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                keywords.append(word)
        
        return keywords[:10]  # 最大10個
    
    def _build_analysis_prompt(self, title, url, content, past_articles):
        """解析用プロンプトを構築"""
        
        past_context = ""
        if past_articles:
            past_context = "\n\n## 過去の関連記事\n"
            for i, article in enumerate(past_articles, 1):
                past_context += f"\n{i}. **{article['date']}**: {article['title']}\n"
                past_context += f"   {article['summary']}\n"
        
        prompt = f"""あなたはセキュリティ初心者およびIT初級者向けのセキュリティニュース解説者です。
以下の英語のセキュリティニュース記事を、高校生にもわかるレベルで日本語で解説してください。

## 記事情報
**タイトル**: {title}
**URL**: {url}

## 記事本文(英語)
{content[:4000]}  # 長すぎる場合は切り詰め

{past_context}

## 解説の要件

1. **前提知識の補足**
   - 高校生レベルでもわかるように、関連するシステム構成や背景知識を最初に説明してください
   - 専門用語が出てくる場合は、必ず補足説明を付けてください
   - 例: 「SQLインジェクション」→「データベースに不正な命令を送り込む攻撃手法」

2. **記事内容の詳細解説**
   - 何が起きたのか
   - なぜ重要なのか
   - どのような影響があるのか
   - 技術的な仕組み(わかりやすく)
   - 対策方法(もしあれば)

3. **過去記事との関連**
   - 上記の「過去の関連記事」がある場合、それと今回の記事の関係性を軽く触れてください
   - 「以前○○について解説しましたが、今回は...」のような形で

4. **構成**
   以下のMarkdown形式で出力してください：
   
   ```markdown
   # {{タイトル(日本語訳)}}

   **元記事**: [{{タイトル}}]({{url}})
   **解説日**: {{今日の日付}}
   
   ## 背景知識
   
   (このニュースを理解するために必要な前提知識)
   
   ## 何が起きたのか
   
   (事件・発見の概要)
   
   ## 技術的な詳細
   
   (仕組みの解説)
   
   ## なぜ重要なのか
   
   (影響範囲や重要性)
   
   ## 対策・今後の展望
   
   (対策方法や今後の動向)
   
   ## 過去記事との関連
   
   (関連する過去記事があれば)
   
   ## 用語解説
   
   (記事に出てきた専門用語のまとめ)
   ```

5. **トーン**
   - 丁寧で親しみやすい文体
   - 難しい内容でも「理解できる」と感じられるように
   - 例え話や具体例を積極的に使う

それでは、この記事の解説をお願いします。
"""
        
        return prompt
    
    def save_analysis(self, article_data, analysis_text):
        """
        解析結果を保存
        
        Args:
            article_data: 記事データ(title, url, date など)
            analysis_text: 解説文
            
        Returns:
            str: 保存したファイルパス
        """
        try:
            # ファイル名を生成(YYYYMMDD_HHmmss_タイトル.json)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # タイトルからファイル名を生成(英数字のみ、最大50文字)
            safe_title = "".join(
                c for c in article_data['title'] 
                if c.isalnum() or c in [' ', '-', '_']
            )[:50].strip().replace(' ', '_')
            
            filename = f"{timestamp}_{safe_title}.json"
            filepath = os.path.join(self.archive_dir, filename)
            
            # データを保存
            save_data = {
                'date': datetime.now().isoformat(),
                'title': article_data['title'],
                'url': article_data['url'],
                'analysis': analysis_text,
                'metadata': {
                    'source': 'The Hacker News',
                    'analyzer': 'Claude Security News Analyzer',
                    'version': '1.0'
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"解析結果を保存しました: {filepath}")
            
            # Markdownファイルも保存
            md_filepath = filepath.replace('.json', '.md')
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(analysis_text)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存エラー: {e}")
            raise


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)
    
    analyzer = NewsAnalyzer()
    
    # テスト用記事
    test_title = "New Malware Exploits Zero-Day Vulnerability in Windows"
    test_url = "https://example.com/test"
    test_content = "This is a test article content..."
    
    analysis = analyzer.analyze_article(test_title, test_url, test_content)
    print(analysis)
