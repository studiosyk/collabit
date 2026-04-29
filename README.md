# collabit

Collabit の独立運用領域です。

## Purpose

- 本案件としての継続運用
- 過去資料の保管
- 派生施策の整理

## Structure

- `core/`: 継続運用する本体領域
- `archive/`: 過去資料や履歴の保管
- `campaigns/`: 期間や目的が区切られた派生施策

## Writing Workflow

記事執筆時の基本的な作業フローは次のとおりです。

1. 社員ディレクターから指示、構成案、資料を受け取る
2. 指示内容を `brief.md` に整理して保存する
3. 素材と情報のファクトチェックを行う
4. 必要なリサーチを行い、要点を `research.md` に整理する
5. 構成を確認し、必要に応じて `outline.md` を整える
6. 本文用の図版や説明画像が必要であれば作成し、各記事フォルダの `assets/description/` に置く
7. 本文を `draft.md` に執筆する
8. 校正を行う
9. ファクトチェックを行う
10. 確定版を `final.md` にまとめる
11. サムネイルを作成し、各記事フォルダの `assets/thumbnail/` に置く
12. 必要に応じてレビュー後、公開済み状態へ進める

補足:

- `log.md` は上記の全工程で随時更新する
- 記事ごとの詳細なファイル構成は `core/writing/README.md` を参照する
- 文体や単語ルールは `core/writing_guide/` を参照する
- 記事アセットの基準は `core/design_guide/design_system.md` を参照する
