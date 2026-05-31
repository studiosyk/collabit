# howma_mag_sources

HowMaマガジン `/mag/` 配下の公開記事を週次で確認する定常作業。

## What This Routine Does

1. `/mag/` と主要カテゴリページを起点にクロールする
2. 記事URLらしいURLだけを抽出する
3. 各記事URLから `title`、`h1`、`meta_description` を取得する
4. 前回スナップショットと比較する
5. 差分CSVと実行ログを保存する
6. 人間が差分を確認してGOした場合のみ、追加URLの記事本文をMarkdown化する

## Snapshot Directory

各実行日の出力は日付フォルダに保存する。

```text
抽出作業_yymmdd/
├── review_report_yymmdd.md
└── python_outputs/
    ├── howma_mag_yymmdd_article_like_clean.csv
    ├── howma_mag_yymmdd_article_metadata.csv
    ├── howma_mag_yymmdd_run.log
    ├── diff/
    └── md_added_yymmdd/
```

`review_report_yymmdd.md` は人間確認用の入口。毎週の確認ではまずこのファイルを見る。

## diff

`diff/` は前回スナップショットとの比較結果。

- `howma_mag_yymmdd_added.csv`: 前回になく、今回新しく見つかったURL
- `howma_mag_yymmdd_removed.csv`: 前回はあったが、今回見つからなかったURL
- `howma_mag_yymmdd_unchanged.csv`: 前回も今回も存在するURL
- `howma_mag_yymmdd_changed.csv`: URLは同じだが、`title` または `h1` が変わった記事
- `howma_mag_yymmdd_summary.csv`: URL差分の件数
- `howma_mag_yymmdd_metadata_summary.csv`: `title` / `h1` 比較の件数
- `howma_mag_yymmdd_metadata_unchanged.csv`: URLも `title` / `h1` も変わらない記事

## Weekly Commands

クロールと差分作成:

```powershell
python .\scripts\howma_mag\update_howma_mag_urls.py --date yymmdd --sleep-sec 0
```

人間が差分を確認してGOしたあと、追加URLだけMarkdown化:

```powershell
python .\scripts\howma_mag\export_added_articles_to_md.py --date yymmdd --sleep-sec 0
```

MD化した記事本文は、執筆用ソースとして `core/writing/_assets/記事ソース_yymmdd/md_added/` に保存する。定常作業側の `python_outputs/md_added_yymmdd/` は一時出力・作業ログ置き場として扱い、Git管理しない。

スクリプトへのリンク集は [SCRIPT_SHORTCUTS.md](SCRIPT_SHORTCUTS.md) を参照。

## Encoding

CSVは `utf-8-sig`、Markdownとログは `utf-8` で保存する。PowerShellの表示上は一部の日本語パスが文字化けして見えることがあるが、ファイル内容はUTF-8で扱う。
