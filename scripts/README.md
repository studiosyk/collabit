# scripts

用途別の補助スクリプト置き場。

## Directories

- `howma_mag/`
  - HowMaマガジン `/mag/` 配下URLの週次クロール
  - URL差分、記事メタ情報差分、追加URLのMarkdown化
  - 手順: [HOWMA_MAG_URL_SNAPSHOT.md](howma_mag/HOWMA_MAG_URL_SNAPSHOT.md)
- `writing/`
  - Collabit執筆作業の補助
  - 記事フォルダ作成、テンプレート複製、初期ファイル生成
  - スクリプトは初期セットアップまでを担当し、その後のワークフロー2〜5はエージェントが同じ作業ターン内で続けて実施する

## Examples

```powershell
python .\scripts\howma_mag\update_howma_mag_urls.py --date yymmdd --sleep-sec 0
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\writing\start_writing_article.ps1 -SourcePath ".\core\writing\1_stock\構成案.md" -MoveSource
```
