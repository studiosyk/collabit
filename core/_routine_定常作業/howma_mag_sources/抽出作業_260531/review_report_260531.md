# HowMa /mag/ 定期チェック レポート 260531

## Summary

- 前回URL数: 541
- 現在URL数: 550
- 追加URL: 9
- 削除URL: 0
- 継続URL: 541
- title/H1変更: 0
- 追加URL MD化: 要確認
- 判定: 要確認

## Human Check

- [ ] `added` を確認した
- [ ] `removed` を確認した
- [ ] `changed` を確認した
- [ ] 追加URLをMarkdown化してよい

## Added URLs

| URL | H1 |
| --- | --- |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-10_4/ | 売買のベテラン仲介営業がいつも後悔する、不動産売買の決済のあるあるトラブル事例と「後悔しない」手続を独白！ |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-1_1/ | 2分で分かる！不動産AI査定の正しい理解・使い方と査定結果の解釈・次に取るべき行動 |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-1_2/ | 不動産の買い替えをまず考えるときにぶち当たる「ダブルローン・仮住まい・同時決済」の違いを徹底図解 |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-1_3/ | 売った後のお金は大事すぎる！不動産AI査定＋ローン残高から、あなたの物件の手残り金額を試算 |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-1_4/ | 不動産売却にかかる費用は売却価格の約5%？結局いくらかかるの？手取り額の計算方法と、自宅と投資用の違いも徹底解説！ |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-6_1/ | 自宅の売却を依頼する不動産会社選びの3つのステップ |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-6_2/ | 失敗しない！信頼できる不動産業者を見抜く10のチェックポイント |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-8_2/ | 買主に最高の内覧体験を提供し、気持ちよく買ってもらうための内覧対応の黄金パターン |
| https://www.how-ma.com/mag/sell/ai-sell-realestate-perfectguide-8_3/ | 内覧で好印象を与え売却成約率を上げる！ハウスクリーニングの重点箇所とコツ |

## Removed URLs

削除URLはありません。

## Changed Title/H1

title/H1変更はありません。

## Output Files

- `python_outputs/howma_mag_260531_article_like_clean.csv`
- `python_outputs/howma_mag_260531_article_metadata.csv`
- `python_outputs/diff/howma_mag_260531_added.csv`
- `python_outputs/diff/howma_mag_260531_removed.csv`
- `python_outputs/diff/howma_mag_260531_changed.csv`
- `python_outputs/diff/howma_mag_260531_summary.csv`
- `python_outputs/diff/howma_mag_260531_metadata_summary.csv`
- `python_outputs/howma_mag_260531_run.log`

## Next Step

人間確認後、問題なければ以下を実行する。

```powershell
python .\scripts\howma_mag\export_added_articles_to_md.py --date 260531 --sleep-sec 0
```
