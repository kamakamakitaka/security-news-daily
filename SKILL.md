# Security News Analyzer Skill

## 概要

The Hacker News のセキュリティニュース記事を自動で取得し、高校生レベルでわかりやすく日本語解説するスキル。

## 主な機能

1. **Gmail からメール取得**: The Hacker News のニュースレターを自動取得
2. **記事解析**: Claude API を使用して記事を詳細に解説
3. **GitHub 保存**: 解説を GitHub リポジトリに自動保存・公開
4. **過去記事参照**: 関連する過去記事を検索して振り返り
5. **自動実行**: Windows タスクスケジューラで毎日実行

## 使用方法

### 基本実行

```bash
cd security-news-analyzer/src
python main.py
```

### 個別モジュールのテスト

```bash
# Gmail 取得テスト
python gmail_fetcher.py

# 解析エンジンテスト
python news_analyzer.py

# GitHub 保存テスト
python github_saver.py
```

## 必要な環境変数

```bash
# Anthropic API キー
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# GitHub Personal Access Token
export GITHUB_TOKEN="ghp_..."
```

## 必要な認証情報

### Gmail API
- `credentials/credentials.json` - Google Cloud Console からダウンロード
- `credentials/token.pickle` - 初回認証時に自動生成

### GitHub API
- Personal Access Token（スコープ: `repo`）

## 設定ファイル

`config.yaml`:
```yaml
gmail:
  email: "mstk.allfirst@gmail.com"
  sender_filter: "news@news.nl00.net"

github:
  username: "kamakamakitaka"
  repo_name: "security-news-daily"

anthropic:
  model: "claude-sonnet-4-20250514"
  max_tokens: 8000
```

## 出力形式

### Markdown（GitHub保存）
```
daily/YYYY/MM/DD_記事タイトル.md
```

### JSON（アーカイブ）
```
archive/YYYY/MM/DD_記事タイトル.json
```

### ログ
```
logs/analyzer_YYYYMMDD.log
```

## 解説の構成

1. **背景知識**: 高校生レベルでの前提知識
2. **何が起きたのか**: 事件・発見の概要
3. **技術的な詳細**: 仕組みの解説
4. **なぜ重要なのか**: 影響範囲や重要性
5. **対策・今後の展望**: 対策方法や今後の動向
6. **過去記事との関連**: 関連する過去記事
7. **用語解説**: 専門用語のまとめ

## 自動実行設定

### Windows タスクスケジューラ
- **実行時刻**: 毎日 21:35
- **プログラム**: `python.exe`
- **引数**: `src\main.py`
- **開始ディレクトリ**: プロジェクトルート

## トラブルシューティング

### Gmail 認証エラー
```bash
# credentials.json を確認
ls credentials/credentials.json

# 再認証
python src/gmail_fetcher.py
```

### GitHub Push エラー
```bash
# トークン確認
echo $GITHUB_TOKEN  # Linux/Mac
echo %GITHUB_TOKEN%  # Windows
```

### Claude API エラー
```bash
# APIキー確認
echo $ANTHROPIC_API_KEY  # Linux/Mac
echo %ANTHROPIC_API_KEY%  # Windows
```

## ディレクトリ構造

```
security-news-analyzer/
├── README.md                 # 詳細セットアップガイド
├── QUICKSTART.md            # クイックスタート
├── CLAUDE_CODE_SETUP.md     # Claude Code 実行手順
├── config.yaml              # 設定ファイル
├── requirements.txt         # Python 依存関係
├── credentials/             # Gmail API 認証情報
│   ├── credentials.json     # OAuth クライアント ID
│   └── token.pickle         # アクセストークン
├── src/                     # ソースコード
│   ├── main.py             # メインスクリプト
│   ├── gmail_fetcher.py    # Gmail 取得
│   ├── news_analyzer.py    # 記事解析
│   └── github_saver.py     # GitHub 保存
├── archive/                 # ローカルアーカイブ（JSON）
├── logs/                    # 実行ログ
└── .gitignore              # Git 除外設定
```

## 依存パッケージ

```
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.108.0
anthropic==0.42.0
PyYAML==6.0.1
python-dateutil==2.8.2
requests==2.31.0
PyGithub==2.1.1
beautifulsoup4==4.12.2
lxml==4.9.3
schedule==1.2.0
```

## カスタマイズ

### 解説のトーン変更
`src/news_analyzer.py` の `_build_analysis_prompt()` メソッドを編集

### スケジュール変更
`config.yaml` の `schedule` セクションを編集

### GitHub リポジトリ変更
`config.yaml` の `github` セクションを編集

## セキュリティ注意事項

⚠️ **絶対に GitHub にコミットしない**:
- `credentials/credentials.json`
- `credentials/token.pickle`
- 環境変数（API キー、トークン）

## バージョン履歴

- **1.0.0** (2025-05-24): 初回リリース
  - Gmail 自動取得
  - Claude 解析
  - GitHub 自動保存
  - 過去記事参照

## ライセンス

MIT License

## サポート

詳細は [README.md](README.md) を参照してください。
