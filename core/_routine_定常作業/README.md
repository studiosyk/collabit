# _routine_定常作業

定期的に繰り返す取得・点検・差分確認の作業置き場。

記事制作そのものは `core/writing/` で管理し、週次クロールなどの生データ、実行ログ、差分CSVはこの配下に保存する。

## Current routines

- `howma_mag_sources/`
  - HowMaマガジン `/mag/` 配下URLの週次クロール
  - URL、`title`、`h1`、`meta_description` の取得
  - 前回スナップショットとの差分確認
    - 追加URL
    - 削除URL
    - 継続URL
    - 同じURLで `title` または `h1` が変わった記事
  - 人間が件数と差分CSVを確認したあと、必要な場合のみ追加URLの記事本文をMarkdown化

## Human approval flow

1. 週次クロールを実行する
2. `diff/*_summary.csv` と `diff/*_metadata_summary.csv` で件数を確認する
3. `diff/*_added.csv`、`diff/*_removed.csv`、`diff/*_changed.csv` を人間が確認する
4. 問題なければ、追加URLのみMarkdown化する
5. 異常な削除数、想定外の変更数、文字化け、取得失敗があればMarkdown化せず原因を確認する

詳しい手順は [HOWMA_MAG_URL_SNAPSHOT.md](../../scripts/howma_mag/HOWMA_MAG_URL_SNAPSHOT.md) を参照。
