# 🔧 セキュリティニュース自動解析システム - セットアップガイド

このドキュメントは、本システムのセットアップ内容と、今後の編集・メンテナンス時に必要な情報をまとめたものです。

---

## 📋 システム概要

**目的**：The Hacker News から毎日セキュリティニュースを自動取得し、Claude API で日本語解説を生成、GitHub に自動保存

**構成**：
- **メインスクリプト**：`src/main.py`
- **モジュール**：
  - `src/gmail_fetcher.py` - Gmail API でメール取得
  - `src/news_analyzer.py` - Claude API で記事解析
  - `src/github_saver.py` - GitHub に解析結果保存
- **自動実行**：Windows タスクスケジューラ（毎日 21:35）

---

## 🔑 API 認証情報

### 1. ANTHROPIC_API_KEY（Claude API キー）

**場所**：`.env` ファイル

**取得方法**：
1. https://console.anthropic.com/ にアクセス
2. ログイン後、左メニューから「API Keys」を選択
3. 「Create Key」でキーを作成
4. キーを `.env` の `ANTHROPIC_API_KEY=` に貼り付け

**使用場所**：
- `src/news_analyzer.py` (line 165-166)
- モデル：`claude-sonnet-4-6`

---

### 2. GITHUB_TOKEN（GitHub Personal Access Token）

**場所**：`.env` ファイル

**取得方法**：
1. https://github.com/settings/tokens にアクセス
2. 「Generate new token」→「Generate new token (classic)」
3. **Scopes** で以下を選択：
   - ☑️ `repo` (リポジトリアクセス)
   - ☑️ `workflow` (GitHub Actions 必要な場合)
4. トークンを `.env` の `GITHUB_TOKEN=` に貼り付け

**使用場所**：
- `src/github_saver.py` (line 29)
- リポジトリ：`security-news-daily`

---

### 3. Gmail API 認証情報

**ファイル**：`credentials/credentials.json`

**取得方法**：
1. https://console.cloud.google.com/ にアクセス
2. プロジェクト：「Hacker News Bot」を選択
3. 左メニュー → 「API とサービス」
4. Gmail API が**有効**になっていることを確認
5. 「認証情報」→ 「OAuth 2.0 クライアント ID (デスクトップアプリ)」
6. JSON ダウンロード → `credentials/` フォルダに保存

**OAuth 同意画面**：
- タイプ：外部
- ユーザータイプ：自動プロビジョニング
- テストユーザー：mstk.allfirst@gmail.com

**使用場所**：
- `src/gmail_fetcher.py` (line 18-69)

**注意**：初回実行時にブラウザで認証が必要。その後は `credentials/token.pickle` に自動保存。

---

## ⏰ Windows タスクスケジューラ設定

**タスク名**：SecurityNewsAnalyzer

**実行時刻**：毎日 21:35

**実行内容**：
```
Python実行ファイル: python
引数: src/main.py
作業フォルダ: C:\Users\mstk\security-news-analyzer
```

### 重要な設定

✅ **StartWhenAvailable**：**有効**
- PC がオフだった時刻を過ぎても、起動後に自動実行
- 例：21:35 に PC OFF → 22:00 に起動 → 自動実行される

✅ **AllowStartIfOnBatteries**：**有効**
- ノートパソコンのバッテリー電源でも実行

✅ **DontStopIfGoingOnBatteries**：**有効**
- 実行中にバッテリーになっても実行を続行

✅ **MultipleInstances**：**IgnoreNew**
- 前のタスクがまだ実行中なら新規実行をスキップ（重複実行防止）

### 登録方法（再登録時）
1. PowerShell を「**管理者として実行**」で開く
2. 以下を実行：
```powershell
cd C:\Users\mstk\security-news-analyzer
.\setup_task.ps1
```

**タスク管理**：
- **確認**：Windows キー → 「タスク スケジューラ」で「SecurityNewsAnalyzer」を検索
- **手動実行**：タスク選択 → 右クリック → 「実行」
- **削除**：タスク選択 → 右クリック → 「削除」

**設定確認（PowerShell）**：
```powershell
Get-ScheduledTask -TaskName "SecurityNewsAnalyzer" | Select-Object *
```

**現在の実行状態確認**：
```powershell
Get-ScheduledTask -TaskName "SecurityNewsAnalyzer" | Get-ScheduledTaskInfo
```

---

## 📁 ファイル構成

```
security-news-analyzer/
├── .env                          # API キーなど（.gitignore に含まれる）
├── requirements.txt              # Python 依存パッケージ
├── setup_task.ps1               # タスク登録スクリプト
├── SETUP_GUIDE.md               # このファイル
│
├── src/
│   ├── main.py                  # メインスクリプト
│   ├── gmail_fetcher.py         # Gmail API モジュール
│   ├── news_analyzer.py         # Claude 解析モジュール
│   └── github_saver.py          # GitHub 保存モジュール
│
├── credentials/
│   ├── credentials.json         # Google OAuth 認証情報
│   └── token.pickle             # Gmail トークン（自動生成）
│
├── archive/                     # ローカル保存用
│   └── YYYYMMDD_HHMMSS_*.json   # 解析結果（JSON）
│   └── YYYYMMDD_HHMMSS_*.md     # 解析結果（Markdown）
│
└── logs/
    └── analyzer_YYYYMMDD.log    # 実行ログ
```

---

## 🚀 初回実行

```powershell
cd C:\Users\mstk\security-news-analyzer
python src/main.py
```

**初回のみ**：Gmail 認証のためブラウザが起動します。ログインして認証してください。

---

## 📝 主要なコード変更内容

### claude-sonnet モデル（src/news_analyzer.py line 166）
```python
model="claude-sonnet-4-6"  # 旧: "claude-sonnet-4-20250514"
```
**理由**：新しいモデルIDに対応

### Markdown テンプレートのエスケープ（src/news_analyzer.py line 256-259）
```python
# {{}} で囲むことで f-string での変数展開を防止
f"# {{{{タイトル(日本語訳)}}}}"
```

### Gmail リンク抽出フィルター（src/gmail_fetcher.py line 177-200）
- `thehackernews.com`, `securityweek.com`, `bleepingcomputer.com` など複数ドメイン対応
- `mailto:`, `javascript:` リンクを除外
- 最小タイトル長を 10 文字以上に設定
- `Read More`, `Download Now` などのジェネリックテキストを除外

---

## ⚠️ 編集時の注意事項

### 新しい API キーに変更する場合
1. `.env` ファイルを編集
2. 該当する環境変数を更新
3. 次のタスク実行時に新キーが使用されます

### モデルを変更する場合（`src/news_analyzer.py`）
```python
# line 166
model="claude-sonnet-4-6"  # ← ここを変更
```

**利用可能なモデル**：
- `claude-opus-4-7` （最高性能、実行時間・コスト大）
- `claude-sonnet-4-6` （バランス型）
- `claude-haiku-4-5` （軽量、実行時間・コスト小）

### 実行時刻を変更する場合
1. タスクスケジューラを開く
2. 「SecurityNewsAnalyzer」を選択
3. 右クリック → 「プロパティ」
4. 「トリガー」タブ → 実行時刻を編集
5. または `setup_task.ps1` を修正して再実行

### Email 送信元フィルターを変更する場合（`src/main.py`）
```python
# line 101
sender_email=config['gmail']['sender_filter'],
# config.yaml で設定を管理
```

---

## 🐛 トラブルシューティング

### タスクが実行されない
1. タスクスケジューラで「SecurityNewsAnalyzer」が「Ready」状態か確認
2. `logs/analyzer_*.log` でエラーを確認
3. タスクを手動実行してテスト

### Gmail 認証エラー
1. `credentials/token.pickle` を削除
2. 次回実行時にブラウザで再認証
3. テストユーザーとして登録されているか確認

### GitHub へのアップロードが失敗
1. `.env` の `GITHUB_TOKEN` を確認
2. token に `repo` スコープが含まれているか確認
3. リポジトリ作成権限があるか確認

### Claude API エラー
1. `.env` の `ANTHROPIC_API_KEY` を確認
2. API キーが有効期限内か確認
3. API 使用量を確認：https://console.anthropic.com/

---

## 📊 動作確認

### GitHub での確認
- **Markdown 版**：https://github.com/kamakamakitaka/security-news-daily/tree/main/daily/
- **JSON 版**：https://github.com/kamakamakitaka/security-news-daily/tree/main/archive/

### ローカルでの確認
```powershell
# 最新のログを確認
Get-Content logs/analyzer_*.log -Tail 50

# 最新の解析結果を確認
Get-Content archive/*.md -Tail 20
```

---

## 🔄 メンテナンス

### 定期的な確認事項
- **毎週**：GitHub リポジトリに新しいファイルが追加されているか確認
- **毎月**：API 使用量とコストを確認
- **3ヶ月ごと**：Claude モデルバージョンの確認（新しいバージョンがあれば検討）

### ログのクリーンアップ
```powershell
# 30日以上前のログを削除
Get-ChildItem logs/ -Filter "*.log" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

---

## 📞 サポート

問題が発生した場合：
1. `logs/analyzer_YYYYMMDD.log` でエラーを確認
2. 各 API のステータスページを確認
3. このドキュメントのトラブルシューティングセクションを参照

---

**最終更新**：2026-06-03  
**システム状態**：✅ 本番運用中
