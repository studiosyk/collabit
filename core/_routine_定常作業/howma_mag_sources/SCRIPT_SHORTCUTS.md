# Script Shortcuts

この定常作業で使うスクリプト本体は、リポジトリ直下の `scripts/howma_mag/` に置く。

## Weekly URL Check

- [update_howma_mag_urls.py](../../../scripts/howma_mag/update_howma_mag_urls.py)
  - `/mag/` 配下をクロールする
  - URL一覧、`title`、`h1`、`meta_description` を取得する
  - 前回スナップショットとの差分を `diff/` に出す
  - 実行ログを保存する

```powershell
python .\scripts\howma_mag\update_howma_mag_urls.py --date yymmdd --sleep-sec 0
```

## Added URL Markdown Export

- [export_added_articles_to_md.py](../../../scripts/howma_mag/export_added_articles_to_md.py)
  - `diff/*_added.csv` にある新規URLだけをMarkdown化する
  - 人間が差分を確認してGOしたあとに実行する
  - 定常作業側に一時出力とログを保存し、`core/writing/_assets/記事ソース_yymmdd/md_added/` に執筆用コピーを作る

```powershell
python .\scripts\howma_mag\export_added_articles_to_md.py --date yymmdd --sleep-sec 0
```

## Helper Scripts

- [fetch_sitemap_urls.py](../../../scripts/howma_mag/fetch_sitemap_urls.py)
  - URLクロール本体
- [fetch_page_metadata.py](../../../scripts/howma_mag/fetch_page_metadata.py)
  - 各記事の `title`、`h1`、`meta_description` を取得
- [compare_url_csvs.py](../../../scripts/howma_mag/compare_url_csvs.py)
  - URLの `added` / `removed` / `unchanged` を作成
- [compare_article_metadata_csvs.py](../../../scripts/howma_mag/compare_article_metadata_csvs.py)
  - 同じURLの `title` / `h1` 変更を `changed` として作成
- [export_postcontents_to_md.py](../../../scripts/howma_mag/export_postcontents_to_md.py)
  - 任意のメタ情報CSVから記事本文をMarkdown化

## Operation Guide

- [HOWMA_MAG_URL_SNAPSHOT.md](../../../scripts/howma_mag/HOWMA_MAG_URL_SNAPSHOT.md)
