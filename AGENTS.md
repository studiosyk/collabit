# Collabit Agent

このファイルは、`collabit` 配下で作業するエージェントの行動原則を定義します。

## Business Mission

- HowMa の AI 査定利用を促進し、不動産の査定額確認から一括査定申し込み、最終的な売却成約へつなげる

## Agent Mission

- 社員ディレクターが提供する構成案に基づいて、HowMaマガジンの記事本文と記事用クリエイティブを制作する
- 読者にとって分かりやすく、信頼感があり、次の行動につながる形で情報を整理する
- 作業履歴と判断根拠が追える形でファイルを残す

## Metrics

- KGI: HowMa 経由の売却成約率を上げる
- KPI: AI 査定申込数を増やす

## Read Order

作業前に、原則として次の順で確認します。

1. `README.md`
2. `.domain_context.md`
3. `core/README.md`
4. `core/writing/README.md`
5. `core/writing/★執筆ワークフロー.md`
6. `core/writing_guide/regulation.md`
7. `core/writing_guide/tone_and_manner.md`
8. `core/writing_guide/wordlist.md`
9. `core/writing_guide/director_feedback.md`
10. `core/design_guide/design_system.md`
11. 対象記事フォルダの `brief.md`

## Working Scope

- 継続運用の実務は `core/` 配下で行う
- 過去資料は `archive/` に保管する
- 期間限定の派生施策は `campaigns/` に置く

## Writing Rules

- 1記事は 1 フォルダで管理する
- 記事フォルダ名は `yymmdd_title` 形式を基本にする
- ステータスは `1_stock` → `2_in_progress` → `3_review` → `4_published` の順に進める
- 使わなくなった記事や旧版は `5_archive` に移す
- `1_stock` 内の構成案 `.md` をメンションしたうえで「執筆作業開始」と依頼された場合のみ、`_templates/yymmdd_template` を複製して `2_in_progress` に記事フォルダを作成し、対象の構成案をその中へ移動したうえで、記事制作フロー 2〜5 まで進める
- あとで確認したい箇所は、原稿中でピンクマーカーを付けて明示する
- CTA画像は使わない。過去記事にCTA画像があっても、新規記事・更新記事では画像CTAへ戻さない
- 原稿中のCTAは必ず `<mark style="background-color: #ffcccc;">CTA</mark>` と赤マーカー文字で位置だけ示す
- GoogleドキュメントからWordPressへコピペする運用では、CTA画像を直接貼ると同じ画像がギャラリーに重複アップロードされやすいため禁止する
- HowMa内の記事リンクや読者向けの追加導線は、本文中では `関連記事：` と表記する
- 執筆者側の参考メモは `参照記事：` として `research.md` や `log.md` に残し、本文中には原則出さない
- 官公庁、法令、統計、一次情報など本文の根拠元を示す場合は `出典：` と表記する

## 執筆ワークフロー

記事制作の具体的な手順は `core/writing/★執筆ワークフロー.md` に従う。

- `1_stock` 内の構成案 `.md` をメンションしたうえで「執筆作業開始」と依頼された場合のみ、同ファイルの「執筆作業開始トリガー」に沿って作業を始める
- 「執筆作業開始」は、人間が受領データを `core/writing/1_stock/` に保存し、中身を確認して、ディレクター確認などで止める必要がないと判断したあとに実行する
- 「執筆作業開始」では、初期セットアップ後に記事制作フロー 2〜5（構成案の解釈と前提整理からCTAと図版予定位置の配置まで）を同じ作業ターン内で実施する
- 記事制作フロー 6 以降は人間とAIの共同作業として進め、7以降は6「人間によるAIライティングの精査作業」が終わってから再開する
- 作業終了時は、`core/writing/★執筆ワークフロー.md` の「作業終了時の作業報告フロー」に沿って、対象記事フォルダの `log.md` とチャットに同じ作業報告を残す
- ユーザーが「コラビット終了」と依頼した場合は、スクリプトではなくAIがその時点の作業内容を確認し、作業報告を生成する
- Notionへ作業報告を残す場合は、まずチャットに作業報告案を出し、ユーザーがOKした後にのみコラビット専用DBへページ追加する
- 作業前に `core/writing/★執筆ワークフロー.md` を読み、構成案の解釈、`outline.md` への記事の狙い出力、リサーチ、執筆、校正、最終確認までの手順を確認する
- 初期セットアップは、原則として `scripts/writing/start_writing_article.ps1` を使って半自動化する

## Asset Rules

- 記事専用のクリエイティブは、各記事フォルダ内 `assets/` に置く
- `assets/thumbnail/`
  - サムネイル、アイキャッチ、SNS 用カバー画像
- `assets/description/`
  - 記事説明用画像、本文図版、補助ビジュアル
- 記事をまたぐ資産やルールは `core/design/` と `core/design_guide/` を参照する

## Reference Material Rules

- 元資料そのものは Google Drive に置いてよい
- ただし、執筆や制作に使う要点はローカルの Markdown に要約して残す
- 文体、禁止表現、単語ルールは `core/writing_guide/` を優先する

## HowMa Mag Source Maintenance

- 週に一度、HowMaマガジン `/mag/` 配下の公開URL一覧と記事タイトル情報を取得し、前回スナップショットとの差分を確認する
- サイトマップが使えない場合は、`scripts/howma_mag/update_howma_mag_urls.py` を使い、`https://www.how-ma.com/mag/` と主要カテゴリページを seed URL としてクロールする
- 実行コマンド例:
  - `python .\scripts\howma_mag\update_howma_mag_urls.py --date yymmdd --sleep-sec 0`
- URLスナップショット、差分CSV、実行ログは `core/_routine_定常作業/howma_mag_sources/抽出作業_yymmdd/python_outputs/` に保存する
  - `howma_mag_yymmdd_article_like_clean.csv`: 現在の記事URL一覧
  - `howma_mag_yymmdd_article_metadata.csv`: 現在の記事URL、`title`、`h1`、`meta_description`
  - `diff/howma_mag_yymmdd_added.csv`: 前回から増えたURL
  - `diff/howma_mag_yymmdd_removed.csv`: 前回から消えたURL
  - `diff/howma_mag_yymmdd_changed.csv`: 前回から `title` または `h1` が変わったURL
  - `diff/howma_mag_yymmdd_summary.csv`: 件数サマリー
- `howma_mag_yymmdd_run.log`: クロールと差分作成の作業ログ
- `title` / `h1` の変更は、URLが同じ記事について前回CSVと今回CSVの値を比較して判定する。本文差分そのものはこの定常作業では判定しない
- 必要に応じて `scripts/howma_mag/extend_article_metadata_csv.py` で `category` / `slug` を付与する
- 追加URLの記事本文をローカル参照用Markdownにする場合は、人間が `added` / `removed` / `changed` の件数と中身を確認してGOしたあと、`scripts/howma_mag/export_added_articles_to_md.py` を使い、`core/_routine_定常作業/howma_mag_sources/抽出作業_yymmdd/python_outputs/md_added_yymmdd/` に一時出力し、執筆用コピーを `core/writing/_assets/記事ソース_yymmdd/md_added/` に保存する
- 全URLをMarkdown化する必要がある場合のみ、`scripts/howma_mag/export_postcontents_to_md.py` を使う
- 取得した記事本文Markdownは、執筆時の参照資料として使い、本文へ引用・転載しすぎない。本文中の読者向けリンクは `関連記事：`、調査メモ内の参照は `参照記事：` として扱う

## Tooling Rules

- 自分用の補助ツールや内部向けの仕組みを作る場合は `core/dev_in/` に置く
