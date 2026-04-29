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
5. `core/writing_guide/regulation.md`
6. `core/writing_guide/tone_and_manner.md`
7. `core/writing_guide/wordlist.md`
8. `core/writing_guide/director_feedback.md`
9. `core/design_guide/design_system.md`
10. 対象記事フォルダの `brief.md`

## Working Scope

- 継続運用の実務は `core/` 配下で行う
- 過去資料は `archive/` に保管する
- 期間限定の派生施策は `campaigns/` に置く

## Writing Rules

- 1記事は 1 フォルダで管理する
- 記事フォルダ名は `yymmdd_title` 形式を基本にする
- ステータスは `1_stock` → `2_in_progress` → `3_review` → `4_published` の順に進める
- 使わなくなった記事や旧版は `5_archive` に移す
- `1_stock` 内の `.md` を指定して「作業開始」と依頼された場合は、`_templates/yymmdd_template` を複製して `2_in_progress` に記事フォルダを作成し、対象の原稿 `.md` をその中へ移動して着手状態にする
- あとで確認したい箇所は、原稿中でピンクマーカーを付けて明示する

## Article Workflow

`1_stock` にある記事案から着手するときは、次の順で作業を始めます。

1. 対象の `.md` を特定する
2. `2_in_progress` に `yymmdd_title` 形式の記事フォルダを作る
3. `_templates/yymmdd_template` をその記事フォルダとして複製する
4. 元の原稿 `.md` を `1_stock` から新しい記事フォルダ内へ移動する
5. 以後の執筆、調査、進行管理はその記事フォルダ内で行う

記事制作は、原則として次の流れで進めます。

1. 原稿を受領する
   - ディレクター指示、元原稿、補足資料を確認する
2. 内容整理をする
   - 原稿を通読する
   - 構成を確認する
   - 指示内容を `brief.md` に書く
   - 気になる点、追加確認が必要な点を洗い出す
   - JOB理論目線のアプローチを入れられるか検討する
3. リサーチとファクト確認をする
   - 不足情報の調査
   - 数値、制度、表現の確認
4. 本文用図版、説明画像を設計、制作する
   - まず必要箇所を判断してラフ設計を行う
   - その後は本文執筆と前後しながら内容を詰める
   - 完成した素材は `assets/description/` に置く
5. 本文を執筆する
6. 校正する
   - 読みやすさ、重複、流れ、表記ゆれを整える
7. ファクトチェックを最終実施する
   - 執筆後に事実関係をもう一度確認する
8. サムネイルを制作する
   - 記事内容と訴求がずれないように整える
   - 完成した素材は `assets/thumbnail/` に置く
9. 最終確認をする
   - 指示反映、CTA、トンマナ、納品状態を確認する

記事フォルダ内の主なファイルは、原則として次の順で使います。

1. `brief.md`
   - 記事の発注書、設計書、先方ディレクター指示を保存する
2. `research.md`
   - 調査メモ、参考情報の要約、論点整理を残す
3. `outline.md`
   - 見出し構成と記事全体の流れを整理する
4. `draft.md`
   - 本文の下書きを書く
5. `final.md`
   - 公開版、納品版、確定版の本文を残す

補足:
- `log.md` は全工程で使う進行記録ファイルとして、各ステップの途中でも随時更新する
- `log.md` には、実施内容、未対応事項、次の担当への引き継ぎを残す

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

## Tooling Rules

- 自分用の補助ツールや内部向けの仕組みを作る場合は `core/dev_in/` に置く
