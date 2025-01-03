# total-screentime

macのスクリーンタイムを全期間で取得するやつ

保存されているファイルを見つけてデータを取り出します。
macのスクリーンタイムの保存期間がよくわからないので、一応バックアップを取るやつも作っといたけど
それを参照する部分は作ってないです

## 使い方

Python 3.4 以降で実行可能なはずです。

```zsh
git clone https://github.com/ajshooting/total-screentime.git
cd total-screentime
python total-screentime.py
```

## 定期実行する..?

やらなくていいです

```cli
chmod +x run_backup.zsh
```

`com.ajshooting.backup.plist` を `~/Library/LaunchAgents/` に保存  
(第1週と第3週の日曜日に実行するようになっている...はず..)

pathとかは変えてください

```cli
launchctl load ~/Library/LaunchAgents/com.ajshooting.backup.plist
```
