# Claude Code での実行手順

このプロジェクトを Claude Code で実行し、GitHub リポジトリを作成します。

## 前提条件

1. Claude Code がインストール済み
2. Windows PC
3. Python 3.8+ がインストール済み

---

## ステップ1: プロジェクトを配置

1. ダウンロードした `security-news-analyzer` フォルダを以下に配置:
   ```
   C:\Users\あなたのユーザー名\security-news-analyzer
   ```

2. フォルダ構成を確認:
   ```
   security-news-analyzer/
   ├── README.md
   ├── QUICKSTART.md
   ├── config.yaml
   ├── requirements.txt
   ├── credentials/
   ├── src/
   ├── archive/
   └── logs/
   ```

---

## ステップ2: 環境変数を設定

### ANTHROPIC_API_KEY

1. Windows検索で「環境変数」を検索
2. 「システム環境変数の編集」を開く
3. 「環境変数」ボタン
4. 「ユーザー環境変数」の「新規」
5. 変数名: `ANTHROPIC_API_KEY`
6. 変数値: `sk-ant-api03-...`（あなたのAPIキー）

### GITHUB_TOKEN

1. [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. "Generate new token (classic)" をクリック
3. Note: `Security News Analyzer`
4. Expiration: `No expiration`
5. スコープ: `repo` 全てにチェック
6. "Generate token" をクリック
7. 表示されたトークンをコピー

8. 環境変数に追加:
   - 変数名: `GITHUB_TOKEN`
   - 変数値: `ghp_...`（コピーしたトークン）

**重要**: 設定後、コマンドプロンプトを再起動してください。

---

## ステップ3: Gmail API 認証設定

### Google Cloud Console での設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクト作成: `security-news-analyzer`
3. 左メニュー「APIとサービス」→「ライブラリ」
4. "Gmail API" を検索して「有効にする」
5. 左メニュー「APIとサービス」→「認証情報」
6. 「認証情報を作成」→「OAuth クライアント ID」

### OAuth 同意画面の設定

初めての場合、同意画面の設定を求められます:

1. ユーザータイプ: **外部**
2. 「作成」をクリック
3. アプリ情報:
   - アプリ名: `Security News Analyzer`
   - ユーザーサポートメール: `mstk.allfirst@gmail.com`
   - アプリのロゴ: （スキップ可）
4. スコープ: （デフォルトのまま）
5. テストユーザー:
   - 「ADD USERS」をクリック
   - `mstk.allfirst@gmail.com` を追加
6. 「保存して次へ」を繰り返して完了

### OAuth クライアント ID 作成

1. 「認証情報」画面に戻る
2. 「認証情報を作成」→「OAuth クライアント ID」
3. アプリケーションの種類: **デスクトップアプリ**
4. 名前: `Security News Analyzer Desktop`
5. 「作成」をクリック
6. 表示されたダイアログで「JSONをダウンロード」
7. ダウンロードしたファイル（`client_secret_*.json`）を:
   ```
   C:\Users\あなたのユーザー名\security-news-analyzer\credentials\credentials.json
   ```
   にリネームして保存

---

## ステップ4: Claude Code でセットアップ

### 4.1 Claude Code を起動

コマンドプロンプトで:
```bash
cd C:\Users\あなたのユーザー名\security-news-analyzer
claude
```

### 4.2 依存関係インストール

Claude Code に以下を依頼:

```
このプロジェクトのPython依存関係をインストールしてください。
requirements.txt を使って pip install してください。
```

### 4.3 Gmail 初回認証

Claude Code に以下を依頼:

```
src/gmail_fetcher.py を実行して、Gmail API の初回認証を行ってください。
ブラウザが開くので、mstk.allfirst@gmail.com でログインします。
```

ブラウザで:
1. `mstk.allfirst@gmail.com` を選択してログイン
2. 「このアプリは Google で確認されていません」→「詳細」→「移動」
3. 権限を確認して「許可」

### 4.4 GitHub リポジトリ作成

Claude Code に以下を依頼:

```
src/github_saver.py を実行して、GitHubに新しいリポジトリ
"security-news-daily" を作成してください。
```

### 4.5 メイン実行テスト

Claude Code に以下を依頼:

```
src/main.py を実行して、システム全体をテストしてください。
The Hacker News からメールを取得し、解析して、GitHub に保存します。
```

---

## ステップ5: 自動実行設定

### Windowsタスクスケジューラ

Claude Code に以下を依頼:

```
Windowsタスクスケジューラに、毎日21:35に src/main.py を
自動実行するタスクを登録する手順を教えてください。
```

または、手動で設定:

1. スタートメニュー→「タスクスケジューラ」
2. 「タスクの作成」
3. **全般タブ**:
   - 名前: `Security News Analyzer`
   - ✅ ユーザーがログオンしているかどうかにかかわらず実行する
4. **トリガータブ**:
   - 新規→毎日→21:35
5. **操作タブ**:
   - プログラム: `python.exe`
   - 引数: `src\main.py`
   - 開始: `C:\Users\あなたのユーザー名\security-news-analyzer`
6. **条件タブ**:
   - ❌ AC電源で使用している場合のみ（チェック外す）
7. 「OK」→パスワード入力

---

## 確認事項

### ✅ チェックリスト

- [ ] Python パッケージインストール完了
- [ ] 環境変数 `ANTHROPIC_API_KEY` 設定完了
- [ ] 環境変数 `GITHUB_TOKEN` 設定完了
- [ ] Gmail API 認証完了（`credentials/token.pickle` が生成された）
- [ ] GitHub リポジトリ `security-news-daily` 作成完了
- [ ] テスト実行成功（ログに "全ての処理が完了しました" 表示）
- [ ] タスクスケジューラ登録完了

### 📊 確認方法

**ログファイル確認**:
```bash
type logs\analyzer_YYYYMMDD.log
```

**GitHub リポジトリ確認**:
```
https://github.com/kamakamakitaka/security-news-daily
```

---

## トラブルシューティング

詳細は [README.md](README.md) の「トラブルシューティング」セクションを参照してください。

---

## 次のステップ

1. ✅ セットアップ完了
2. 🎯 毎日21:35に自動実行
3. 📊 翌朝 GitHub を確認
4. 🚀 必要に応じてカスタマイズ

おつかれさまでした！🎉
