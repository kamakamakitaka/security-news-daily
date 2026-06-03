# クイックスタートガイド

## 5分でセットアップ

### 1. 依存関係インストール
```bash
cd security-news-analyzer
pip install -r requirements.txt
```

### 2. Gmail API 認証設定

1. [Google Cloud Console](https://console.cloud.google.com/) で新規プロジェクト作成
2. Gmail API を有効化
3. OAuth 2.0 クライアント ID 作成（デスクトップアプリ）
4. `credentials.json` をダウンロードして `credentials/` に配置

### 3. GitHub トークン取得

1. [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. "Generate new token (classic)"
3. スコープ: `repo` にチェック
4. トークンをコピー

### 4. 環境変数設定

**Windows**:
```cmd
setx ANTHROPIC_API_KEY "sk-ant-api03-..."
setx GITHUB_TOKEN "ghp_..."
```

**コマンドプロンプトを再起動！**

### 5. 初回実行

```bash
cd src
python gmail_fetcher.py  # Gmail認証（初回のみ）
python main.py           # メイン実行
```

### 6. 自動実行設定

Windowsタスクスケジューラ:
- プログラム: `python.exe`
- 引数: `src\main.py`
- 開始: `C:\Users\あなたのユーザー名\security-news-analyzer`
- トリガー: 毎日 21:35

---

詳細は [README.md](README.md) を参照してください。
