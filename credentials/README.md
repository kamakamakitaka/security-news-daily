# 認証情報ディレクトリ

このディレクトリには Gmail API の認証情報を保存します。

## 必要なファイル

### 1. credentials.json
Google Cloud Console からダウンロードした OAuth 2.0 クライアント ID の認証情報ファイル。

**取得方法**:
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. Gmail API を有効化
4. 認証情報を作成（OAuth 2.0 クライアント ID）
5. JSONファイルをダウンロード
6. このディレクトリに `credentials.json` として保存

### 2. token.pickle（自動生成）
初回認証後に自動的に生成されるトークンファイル。
手動で作成する必要はありません。

## セキュリティ注意事項

⚠️ **これらのファイルは絶対に GitHub にコミットしないでください！**

- `.gitignore` で除外されています
- 他人と共有しないでください
- バックアップする場合は安全な場所に保管してください
