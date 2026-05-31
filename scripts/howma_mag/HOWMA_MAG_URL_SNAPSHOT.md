# HowMa /mag/ URL snapshot

サイトマップが使えない場合に、`https://www.how-ma.com/mag/` 配下の一覧ページをクロールして記事URL一覧を作成し、前回スナップショットとの差分を出す。

この定常作業では、URLだけでなく各記事ページの `title`、`h1`、`meta_description` も取得する。同じURLで `title` または `h1` が変わった場合は `changed` として扱う。本文差分までは自動判定しない。

## Weekly update

```powershell
python .\scripts\howma_mag\update_howma_mag_urls.py --date yymmdd --sleep-sec 0
```

例:

```powershell
python .\scripts\howma_mag\update_howma_mag_urls.py --date 260531 --sleep-sec 0
```

出力先:

```text
core/_routine_定常作業/howma_mag_sources/抽出作業_yymmdd/python_outputs/
```

人間確認用レポートは、日付フォルダ直下に保存する。

```text
core/_routine_定常作業/howma_mag_sources/抽出作業_yymmdd/review_report_yymmdd.md
```

主な成果物:

- `howma_mag_yymmdd_article_like_clean.csv`: 現在の記事URL一覧
- `howma_mag_yymmdd_article_metadata.csv`: 現在の記事URL、`title`、`h1`、`meta_description`
- `diff/howma_mag_yymmdd_added.csv`: 前回から増えたURL
- `diff/howma_mag_yymmdd_removed.csv`: 前回から消えたURL
- `diff/howma_mag_yymmdd_unchanged.csv`: 継続して存在するURL
- `diff/howma_mag_yymmdd_changed.csv`: 前回から `title` または `h1` が変わったURL
- `diff/howma_mag_yymmdd_summary.csv`: 件数サマリー
- `diff/howma_mag_yymmdd_metadata_summary.csv`: `title` / `h1` 比較の件数サマリー
- `howma_mag_yymmdd_run.log`: クロールと差分作成の作業ログ
- `../review_report_yymmdd.md`: 人間確認用レポート

比較元は、`core/_routine_定常作業/howma_mag_sources/抽出作業_*` のうち実行日より古い最新スナップショットを自動で選ぶ。旧データ互換のため、過去の `記事ソース_*` と `core/writing/_assets/記事ソース_*` も参照する。明示したい場合は `--previous path\to\csv` を指定する。

## Human approval flow

週次実行後、まず人間が次を確認する。

1. `diff/howma_mag_yymmdd_summary.csv`
2. `diff/howma_mag_yymmdd_metadata_summary.csv`
3. `diff/howma_mag_yymmdd_added.csv`
4. `diff/howma_mag_yymmdd_removed.csv`
5. `diff/howma_mag_yymmdd_changed.csv`

削除数が不自然に多い、変更数が想定外に多い、ログに取得失敗が多い、文字化けして読めないなどの異常があれば、Markdown化に進まず原因を確認する。

## Markdown export for added URLs

人間がGOしたあと、追加URLだけMarkdown化する。

```powershell
python .\scripts\howma_mag\export_added_articles_to_md.py --date yymmdd --sleep-sec 0
```

出力先:

```text
core/_routine_定常作業/howma_mag_sources/抽出作業_yymmdd/python_outputs/md_added_yymmdd/
```

執筆時に使う参照コピーも保存する。

```text
core/writing/_assets/記事ソース_yymmdd/
├── README.md
└── md_added/
```

追加URLだけの入力CSVも保存する。

```text
core/_routine_定常作業/howma_mag_sources/抽出作業_yymmdd/python_outputs/howma_mag_yymmdd_added_article_metadata.csv
```

MD化の作業ログは、既定で `md_added_yymmdd/_export_added_postcontents.log` に保存する。抽出失敗がある場合は `_export_errors.csv` も保存する。

## Markdown export for all URLs

記事本文をMarkdown化する場合:

```powershell
python .\scripts\howma_mag\export_postcontents_to_md.py `
  --input .\core\_routine_定常作業\howma_mag_sources\抽出作業_yymmdd\python_outputs\howma_mag_yymmdd_article_metadata_enriched.csv `
  --outdir .\core\_routine_定常作業\howma_mag_sources\抽出作業_yymmdd\python_outputs\md_article_yymmdd `
  --sleep-sec 0
```

MD化の作業ログは、既定で出力先フォルダの `_export_postcontents.log` に保存する。抽出失敗がある場合は `_export_errors.csv` も保存する。
