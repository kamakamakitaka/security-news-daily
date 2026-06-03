"""
セキュリティニュース自動解析システム - メインスクリプト

毎日 The Hacker News からメールを取得し、Claude で解説して GitHub に保存
"""

import os
import sys
import logging
import yaml
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .env ファイルを読み込む
load_dotenv(os.path.join(project_root, '.env'))

from src.gmail_fetcher import GmailFetcher
from src.news_analyzer import NewsAnalyzer
from src.github_saver import GitHubSaver


def setup_logging(log_dir='logs'):
    """ログ設定"""
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"analyzer_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def load_config(config_path='config.yaml'):
    """設定ファイルを読み込む"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    """メイン処理"""
    
    # ログ設定
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("セキュリティニュース自動解析を開始します")
    logger.info("=" * 60)
    
    try:
        # 設定読み込み
        config = load_config()
        logger.info("設定ファイルを読み込みました")
        
        # 環境変数チェック
        required_env_vars = ['ANTHROPIC_API_KEY', 'GITHUB_TOKEN']
        for var in required_env_vars:
            if not os.environ.get(var):
                raise ValueError(f"環境変数 {var} が設定されていません")
        
        # モジュール初期化
        gmail_fetcher = GmailFetcher(
            credentials_dir=os.path.join(project_root, 'credentials')
        )
        
        news_analyzer = NewsAnalyzer(
            archive_dir=os.path.join(project_root, 'archive')
        )
        
        github_saver = GitHubSaver(
            username=config['github']['username'],
            repo_name=config['github']['repo_name']
        )
        
        logger.info("全モジュールを初期化しました")
        
        # Gmail 認証
        logger.info("Gmail認証を開始します...")
        gmail_fetcher.authenticate()
        
        # GitHub リポジトリ準備
        logger.info("GitHubリポジトリを準備します...")
        github_saver.create_or_get_repository()
        
        # 最新メールを取得
        logger.info("最新のセキュリティニュースメールを取得します...")
        email_data = gmail_fetcher.fetch_latest_news(
            sender_email=config['gmail']['sender_filter'],
            hours_back=24
        )
        
        if not email_data:
            logger.warning("新しいメールが見つかりませんでした")
            return
        
        logger.info(f"メール取得成功: {email_data['subject']}")

        # メールから記事を抽出
        articles = gmail_fetcher.extract_articles_from_email(email_data['body'])
        
        if not articles:
            logger.warning("記事が抽出できませんでした")
            return
        
        logger.info(f"{len(articles)}件の記事を抽出しました")
        
        # 各記事を解析
        for i, article in enumerate(articles, 1):
            logger.info("-" * 60)
            logger.info(f"記事 {i}/{len(articles)}: {article['title']}")
            
            try:
                # 記事本文を取得
                article_content = news_analyzer.fetch_article_content(article['url'])
                
                if not article_content:
                    logger.warning("記事本文を取得できませんでした。スキップします。")
                    continue
                
                # 解析・解説
                logger.info("Claude で解析中...")
                analysis = news_analyzer.analyze_article(
                    article['title'],
                    article['url'],
                    article_content
                )
                
                # ローカルに保存
                logger.info("ローカルに保存中...")
                news_analyzer.save_analysis(article, analysis)
                
                # GitHub に保存
                logger.info("GitHub に保存中...")
                github_url = github_saver.save_analysis(article, analysis)
                
                # README 更新
                github_saver.update_readme_with_latest(
                    article['title'],
                    article['url'],
                    github_url
                )
                
                logger.info(f"✅ 完了: {github_url}")
                
            except Exception as e:
                logger.error(f"❌ 記事処理エラー: {e}", exc_info=True)
                continue
        
        logger.info("=" * 60)
        logger.info("全ての処理が完了しました")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 致命的エラー: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
