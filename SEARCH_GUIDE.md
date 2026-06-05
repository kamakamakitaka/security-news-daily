# 🔍 セキュリティニュース検索・要約ガイド

`search_articles.py` を使って、Supabase に保存されたセキュリティニュースを検索・要約します。

---

## 📋 基本的な使い方

### 準備

```powershell
cd C:\Users\mstk\security-news-analyzer
```

---

## 🎯 検索パターン

### 1️⃣ キーワード検索

**特定の脅威や技術を検索**

```powershell
python search_articles.py -k vulnerability
```

**例**：
```powershell
# 脅威名で検索
python search_articles.py -k malware
python search_articles.py -k ransomware
python search_articles.py -k phishing
python search_articles.py -k "zero-day"

# CVE番号で検索
python search_articles.py -k CVE

# 企業名で検索
python search_articles.py -k Cisco
python search_articles.py -k Microsoft

# 技術で検索
python search_articles.py -k authentication
python search_articles.py -k encryption
python search_articles.py -k DDoS
```

**出力**：マッチした記事のタイトル、日付、URLを表示

---

### 2️⃣ キーワード検索 + Claude 要約

**見つかった記事をセキュリティトレンドでまとめる**

```powershell
python search_articles.py -k malware -s
```

**出力**：
- マッチした記事一覧
- Claude による自動要約（日本語、高校生レベル）

---

### 3️⃣ 日付範囲検索

**特定期間の全記事を検索**

```powershell
python search_articles.py -d 2026-06-03 2026-06-30
```

**例**：
```powershell
# 6月全体
python search_articles.py -d 2026-06-01 2026-06-30

# 1週間
python search_articles.py -d 2026-06-03 2026-06-10

# 本日のみ
python search_articles.py -d 2026-06-05 2026-06-05
```

**出力**：その期間の全記事を日付順で表示

---

### 4️⃣ 日付範囲 + Claude 要約（月間トレンド分析）

**期間内の全記事をセキュリティトレンドで要約**

```powershell
python search_articles.py -d 2026-06-03 2026-06-30 -s
```

**出力**：
- 期間内の全記事一覧
- Claude による月間セキュリティトレンド分析

---

## 💡 実用例

### 例1：「mythos」という脅威についてすべて知りたい

```powershell
python search_articles.py -k mythos -s
```

結果：
- mythos に関する全記事を表示
- Claude が mythos について統一的に要約

---

### 例2：6月3日～6月末のセキュリティニュースを月間サマリーで読みたい

```powershell
python search_articles.py -d 2026-06-03 2026-06-30 -s
```

結果：
- 6月の全記事（7件）を表示
- Claude が月間のセキュリティトレンドをまとめる

---

### 例3：CVE（脆弱性）関連の記事をすべて見たい

```powershell
python search_articles.py -k CVE -s
```

結果：
- CVE を含む全記事
- 脆弱性のトレンド分析

---

### 例4：ランサムウェア関連のニュースを分析

```powershell
python search_articles.py -k ransomware -s
```

---

## 🔧 オプション

| オプション | 説明 | 例 |
|-----------|------|-----|
| `-k` | キーワード検索 | `-k vulnerability` |
| `-d` | 日付範囲検索 | `-d 2026-06-01 2026-06-30` |
| `-s` | Claude で要約 | `-s` |

---

## 📊 Supabase に保存されている内容

各記事は以下の情報で保存されています：

- **title**: 記事タイトル
- **url**: 記事 URL
- **date**: 記事取得日時
- **analysis**: Claude による日本語解説（人間が読める形式）
- **keywords**: 記事に含まれるセキュリティキーワード

---

## 📝 Tips

1. **複数キーワード検索したい場合**：
   ```powershell
   python search_articles.py -k vulnerability -s
   python search_articles.py -k patch -s
   # 結果を比較
   ```

2. **週単位で分析したい**：
   ```powershell
   # 第1週
   python search_articles.py -d 2026-06-01 2026-06-07 -s
   
   # 第2週
   python search_articles.py -d 2026-06-08 2026-06-14 -s
   ```

3. **特定企業の脆弱性をすべて抽出**：
   ```powershell
   python search_articles.py -k "Microsoft vulnerability" -s
   ```

---

**最終更新**: 2026-06-05
