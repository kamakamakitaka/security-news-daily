# Security News Analyzer - セットアップガイド

The Hacker News のセキュリティニュースを自動で取得し、Claude が高校生レベルでわかりやすく日本語解説するシステムです。

## 📋 目次

1. [必要な環境](#必要な環境)
2. [セットアップ手順](#セットアップ手順)
3. [実行方法](#実行方法)
4. [自動実行の設定](#自動実行の設定)
5. [トラブルシューティング](#トラブルシューティング)

---

## 必要な環境

- **Windows 10/11**
- **Python 3.8 以上**
- **Gmail アカウント** (mstk.allfirst@gmail.com)
- **GitHub アカウント** (kamakamakitaka)
- **Anthropic API キー**

---

## セットアップ手順

### 1. Python パッケージのインストール

```bash
cd security-news-analyzer
pip install -r requirements.txt
```

### 2. Gmail API の設定

#### 2.1 Google Cloud Platform でプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（名前: `security-news-analyzer`）
3. プロジェクトを選択

#### 2.2 Gmail API を有効化

1. 左メニュー「APIとサービス」→「ライブラリ」
2. "Gmail API" を検索して選択
3. 「有効にする」をクリック

#### 2.3 OAuth 2.0 認証情報を作成

1. 左メニュー「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「OAuth クライアント ID」
3. 同意画面の設定を求められたら:
   - ユーザータイプ: **外部**
   - アプリ名: `Security News Analyzer`
   - ユーザーサポートメール: `mstk.allfirst@gmail.com`
   - デベロッパーの連絡先: `mstk.allfirst@gmail.com`
   - スコープ: 追加不要（デフォルトのまま）
   - テストユーザー: `mstk.allfirst@gmail.com` を追加
4. OAuth クライアント ID 作成画面に戻る:
   - アプリケーションの種類: **デスクトップアプリ**
   - 名前: `Security News Analyzer Desktop`
5. 「作成」をクリック
6. 表示された画面で「JSONをダウンロード」
7. ダウンロードしたファイルを `credentials/credentials.json` として保存

```bash
# ファイルを適切な場所に配置
mv ~/Downloads/client_secret_*.json credentials/credentials.json
```

#### 2.4 初回認証

```bash
cd src
python gmail_fetcher.py
```

- ブラウザが開くので、`mstk.allfirst@gmail.com` でログイン
- 「このアプリは Google で確認されていません」と表示されたら:
  - 「詳細」→「Security News Analyzer Desktop（安全ではないページ）に移動」をクリック
- 権限を確認して「許可」
- 認証成功メッセージが表示されればOK

### 3. GitHub Personal Access Token の取得

1. [GitHub Settings](https://github.com/settings/tokens) にアクセス
2. 「Generate new token」→「Generate new token (classic)」
3. 設定:
   - Note: `Security News Analyzer`
   - Expiration: `No expiration`（または長期間）
   - スコープ: 
     - ✅ `repo` (全てにチェック)
     - ✅ `workflow`
4. 「Generate token」をクリック
5. 表示されたトークンをコピー（**一度しか表示されません！**）

### 4. 環境変数の設定

#### 4.1 Windowsの環境変数を設定

1. スタートメニューで「環境変数」を検索
2. 「システム環境変数の編集」を開く
3. 「環境変数」ボタンをクリック
4. 「ユーザー環境変数」の「新規」をクリック
5. 以下の2つを追加:

**ANTHROPIC_API_KEY**
```
変数名: ANTHROPIC_API_KEY
変数値: sk-ant-api03-... （あなたのAnthropicAPIキー）
```

**GITHUB_TOKEN**
```
変数名: GITHUB_TOKEN
変数値: ghp_... （手順3で取得したGitHubトークン）
```

6. 「OK」で全てのウィンドウを閉じる
7. **コマンドプロンプトを再起動**（環境変数を反映）

#### 4.2 環境変数の確認

```bash
# コマンドプロンプトで確認
echo %ANTHROPIC_API_KEY%
echo %GITHUB_TOKEN%
```

### 5. 初回実行テスト

```bash
cd security-news-analyzer/src
python main.py
```

成功すると:
- Gmail から最新メールを取得
- Claude が各記事を解析
- GitHub リポジトリ `security-news-daily` が自動作成
- 解説が保存される

---

## 実行方法

### 手動実行

```bash
cd security-news-analyzer/src
python main.py
```

### ログの確認

```bash
# 最新のログを表示
cd security-news-analyzer/logs
type analyzer_YYYYMMDD.log
```

---

## 自動実行の設定

毎日 21:35 に自動実行するように設定します。

### Windowsタスクスケジューラの設定

1. スタートメニューで「タスクスケジューラ」を検索して起動
2. 右側の「タスクの作成」をクリック

#### 全般タブ
- 名前: `Security News Analyzer`
- 説明: `毎日のセキュリティニュース自動解析`
- ✅ ユーザーがログオンしているかどうかにかかわらず実行する
- ✅ 最上位の特権で実行する

#### トリガータブ
1. 「新規」をクリック
2. 設定:
   - タスクの開始: **スケジュールに従う**
   - 設定: **毎日**
   - 開始: **21:35:00**
   - 繰り返し間隔: （設定しない）
   - ✅ 有効
3. 「OK」

#### 操作タブ
1. 「新規」をクリック
2. 設定:
   - 操作: **プログラムの起動**
   - プログラム/スクリプト: `python.exe`
   - 引数の追加: `src\main.py`
   - 開始: `C:\Users\あなたのユーザー名\security-news-analyzer`
     
     **重要**: フルパスで指定してください。例:
     ```
     C:\Users\Masataka\security-news-analyzer
     ```

3. 「OK」

#### 条件タブ
- ❌ コンピューターをAC電源で使用している場合のみタスクを開始する（チェックを外す）
- ❌ タスクを実行するためにスリープを解除する（必要に応じて）

#### 設定タブ
- ✅ タスクが失敗した場合の再起動の間隔: `1分間`
- ✅ 再起動の試行回数: `3回`

4. 「OK」→ パスワード入力を求められたら Windows ログインパスワードを入力

### タスクのテスト実行

1. タスクスケジューラで作成したタスクを右クリック
2. 「実行する」を選択
3. ログファイル（`logs/analyzer_YYYYMMDD.log`）を確認

---

## トラブルシューティング

### Gmail認証エラー

**症状**: `FileNotFoundError: 認証情報ファイルが見つかりません`

**解決方法**:
1. `credentials/credentials.json` が存在するか確認
2. ファイルの中身が正しいJSON形式か確認
3. Google Cloud Console で OAuth クライアントを再作成

---

### GitHub Push エラー

**症状**: `GithubException: Bad credentials`

**解決方法**:
1. `GITHUB_TOKEN` 環境変数が正しく設定されているか確認:
   ```bash
   echo %GITHUB_TOKEN%
   ```
2. トークンのスコープに `repo` が含まれているか確認
3. トークンの有効期限が切れていないか確認
4. 必要に応じてトークンを再生成

---

### Claude API エラー

**症状**: `APIError: Invalid API Key`

**解決方法**:
1. `ANTHROPIC_API_KEY` 環境変数が正しく設定されているか確認:
   ```bash
   echo %ANTHROPIC_API_KEY%
   ```
2. APIキーが有効か [Anthropic Console](https://console.anthropic.com/) で確認
3. 環境変数設定後にコマンドプロンプトを再起動したか確認

---

### メールが取得できない

**症状**: `新しいメールが見つかりませんでした`

**考えられる原因**:
1. The Hacker News からメールが届いていない
2. 検索期間（24時間以内）にメールが無い

**解決方法**:
1. Gmail で実際にメールが届いているか確認
2. `src/main.py` の `hours_back=24` を `48` に変更して範囲を広げる

---

### タスクスケジューラが動作しない

**症状**: 指定時刻になっても実行されない

**確認項目**:
1. タスクが「有効」になっているか
2. 「開始」パスに正しいプロジェクトディレクトリが設定されているか
3. タスク履歴で実際に実行されているか確認
4. ログファイルにエラーが記録されていないか確認

---

## 📚 参考リンク

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [The Hacker News](https://thehackernews.com/)

---

## 🎯 次のステップ

1. ✅ セットアップ完了
2. ✅ 手動実行テスト
3. ✅ 自動実行設定
4. 📊 毎日のログ確認
5. 🚀 必要に応じてカスタマイズ

---

**作成日**: {datetime.now().strftime("%Y-%m-%d")}
**バージョン**: 1.0.0
