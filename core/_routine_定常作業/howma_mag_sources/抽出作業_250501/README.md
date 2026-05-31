# 抽出作業_250501

HowMaマガジン `/mag/` の過去取得スナップショット。

## Source

- スナップショット日: 250501
- 種別: 当時の `/mag/` URL一覧、記事メタ情報、全記事Markdown化データの管理情報
- 執筆用コピー: `core/writing/_assets/記事ソース_250501/md_all/`

## Files

- `python_outputs/howma_mag_article_like_clean.csv`: 記事URL一覧
- `python_outputs/howma_mag_article_metadata.csv`: URL、`title`、`h1`、`meta_description`
- `python_outputs/howma_mag_article_metadata_enriched.csv`: `category` / `slug` 付与済みメタ情報
- 全記事本文Markdown: `core/writing/_assets/記事ソース_250501/md_all/`

## Git Policy

Markdown本文はファイル数と容量が増えやすいためGit管理しない。CSV、README、スクリプトなど軽量な管理情報のみGit管理する。
