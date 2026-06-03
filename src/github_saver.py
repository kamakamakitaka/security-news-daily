"""
GitHub リポジトリへの自動保存モジュール
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from github import Github, GithubException

# .env ファイルを読み込む
project_root = Path(__file__).parent.parent
load_dotenv(os.path.join(project_root, '.env'))


class GitHubSaver:
    """GitHub リポジトリ管理クラス"""
    
    def __init__(self, token=None, username=None, repo_name=None):
        """
        初期化
        
        Args:
            token: GitHub Personal Access Token
            username: GitHubユーザー名
            repo_name: リポジトリ名
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GITHUB_TOKEN 環境変数が設定されていません")
        
        self.username = username
        self.repo_name = repo_name
        self.logger = logging.getLogger(__name__)
        
        # GitHub クライアントを初期化
        self.client = Github(self.token)
        self.user = self.client.get_user()
        self.repo = None
    
    def create_or_get_repository(self):
        """リポジトリを作成または取得"""
        try:
            # 既存のリポジトリを取得
            self.repo = self.user.get_repo(self.repo_name)
            self.logger.info(f"既存のリポジトリを使用: {self.repo_name}")
            
        except GithubException as e:
            if e.status == 404:
                # リポジトリが存在しない場合は作成
                self.logger.info(f"新規リポジトリを作成: {self.repo_name}")
                
                self.repo = self.user.create_repo(
                    self.repo_name,
                    description="Daily Security News Analysis by Claude",
                    private=False,  # 公開リポジトリ
                    auto_init=True  # README.md を自動生成
                )
                
                # 初期 README を更新
                self._create_initial_readme()
                
                self.logger.info("リポジトリを作成しました")
            else:
                raise
        
        return self.repo
    
    def _create_initial_readme(self):
        """初期 README.md を作成"""
        readme_content = f"""# Security News Daily Analysis

このリポジトリは、The Hacker News から配信される日次セキュリティニュースを、
高校生レベルでもわかりやすく日本語で解説したアーカイブです。

## 📰 更新について

- **配信元**: [The Hacker News](https://thehackernews.com/)
- **更新頻度**: 毎日 22:00 頃
- **解説者**: Claude (Anthropic)

## 📁 ディレクトリ構成

```
/
├── README.md           # このファイル
├── daily/             # 日次解説（Markdown形式）
│   └── YYYY/MM/       # 年月ごとに整理
└── archive/           # 全データ（JSON形式）
    └── YYYY/MM/
```

## 🎯 解説の特徴

1. **高校生レベルの日本語**: 専門用語には必ず補足説明
2. **前提知識の補足**: システム構成や背景を最初に解説
3. **過去記事との関連**: 似た記事があれば振り返り
4. **具体例と例え話**: 難しい概念をわかりやすく

## 🔗 関連リンク

- [The Hacker News](https://thehackernews.com/)
- [Claude (Anthropic)](https://www.anthropic.com/claude)

---

**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        try:
            readme = self.repo.get_contents("README.md")
            self.repo.update_file(
                "README.md",
                "Initialize README",
                readme_content,
                readme.sha
            )
        except GithubException:
            self.repo.create_file(
                "README.md",
                "Initialize README",
                readme_content
            )
    
    def save_analysis(self, article_data, analysis_markdown):
        """
        解析結果を GitHub に保存
        
        Args:
            article_data: 記事データ（title, url, date など）
            analysis_markdown: 解説文（Markdown）
            
        Returns:
            str: GitHub 上のファイルURL
        """
        try:
            # 日付ベースのパスを生成
            now = datetime.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")
            
            # ファイル名を生成
            safe_title = "".join(
                c for c in article_data['title']
                if c.isalnum() or c in [' ', '-', '_']
            )[:50].strip().replace(' ', '_')
            
            # Markdown ファイルパス
            md_path = f"daily/{year}/{month}/{day}_{safe_title}.md"
            
            # JSON ファイルパス
            json_path = f"archive/{year}/{month}/{day}_{safe_title}.json"
            
            # Markdown を保存
            self._create_or_update_file(
                md_path,
                analysis_markdown,
                f"Add analysis: {article_data['title']}"
            )
            
            # JSON を保存
            json_data = {
                'date': now.isoformat(),
                'title': article_data['title'],
                'url': article_data['url'],
                'analysis': analysis_markdown
            }
            
            self._create_or_update_file(
                json_path,
                json.dumps(json_data, ensure_ascii=False, indent=2),
                f"Add archive: {article_data['title']}"
            )
            
            # GitHub上のURLを生成
            file_url = f"https://github.com/{self.username}/{self.repo_name}/blob/main/{md_path}"
            
            self.logger.info(f"GitHubに保存完了: {file_url}")
            
            return file_url
            
        except Exception as e:
            self.logger.error(f"GitHub保存エラー: {e}")
            raise
    
    def _create_or_update_file(self, path, content, commit_message):
        """ファイルを作成または更新"""
        try:
            # 既存ファイルを取得
            file = self.repo.get_contents(path)
            
            # ファイルが存在する場合は更新
            self.repo.update_file(
                path,
                commit_message,
                content,
                file.sha
            )
            
            self.logger.info(f"ファイルを更新: {path}")
            
        except GithubException as e:
            if e.status == 404:
                # ファイルが存在しない場合は新規作成
                self.repo.create_file(
                    path,
                    commit_message,
                    content
                )
                
                self.logger.info(f"ファイルを作成: {path}")
            else:
                raise
    
    def update_readme_with_latest(self, article_title, article_url, analysis_url):
        """README に最新記事を追加"""
        try:
            readme = self.repo.get_contents("README.md")
            readme_content = readme.decoded_content.decode('utf-8')
            
            # 最新記事セクションを追加/更新
            latest_section = f"\n\n## 📌 最新の解説\n\n"
            latest_section += f"**{datetime.now().strftime('%Y年%m月%d日')}**: "
            latest_section += f"[{article_title}]({analysis_url})\n\n"
            latest_section += f"元記事: [{article_title}]({article_url})\n"
            
            # 既存の「最新の解説」セクションを置換
            if "## 📌 最新の解説" in readme_content:
                readme_content = re.sub(
                    r"## 📌 最新の解説.*?(?=##|\Z)",
                    latest_section,
                    readme_content,
                    flags=re.DOTALL
                )
            else:
                # セクションが無い場合は最後に追加
                readme_content += latest_section
            
            # Last Updated を更新
            readme_content = re.sub(
                r"\*\*Last Updated\*\*:.*",
                f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                readme_content
            )
            
            # README を更新
            self.repo.update_file(
                "README.md",
                f"Update README with latest: {article_title}",
                readme_content,
                readme.sha
            )
            
            self.logger.info("README を更新しました")
            
        except Exception as e:
            self.logger.error(f"README更新エラー: {e}")


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)
    
    # 環境変数から設定を読み込む
    saver = GitHubSaver(
        username="kamakamakitaka",
        repo_name="security-news-daily"
    )
    
    # リポジトリを作成または取得
    repo = saver.create_or_get_repository()
    print(f"リポジトリ: {repo.html_url}")
