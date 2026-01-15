# attendance-check-app

出勤簿と有給申請の突合を行い、未入力や不一致を検出する社内向けツールです。外部クラウドにはデータを送信せず、ローカルPCから社内ファイルサーバー上のExcelを読み取ります。

## できること

- 部署ごとの出勤簿（Excel）を走査し、始業/終業が未入力の社員を抽出
- 有給申請データと出勤簿の不一致を検出
- 結果を `results/YYYYMM/` に JSON・Excel・ログとして保存（3年分保持を想定）
- ローカルWeb UI（Flask）で一覧表示し、各行からメール作成（mailto）を起動

## 前提

- データは外部送信しません（社内ファイルサーバー／ローカルPCのみ）。
- 実行環境は Windows + Python 3 です。

## セットアップ

1. Python 3 をインストールします。
2. 必要パッケージをインストールします。

```bash
pip install -r requirements.txt
```

3. `config.sample.yaml` をコピーして `config.yaml` を作成します。

```bash
copy config.sample.yaml config.yaml
```

4. `config.yaml` のパスを社内環境に合わせて更新します。

## 月次運用手順

1. `config.yaml` の `target_year_month` を対象月に変更します。
2. `run.bat` をダブルクリックして起動します。
3. ブラウザで `http://127.0.0.1:5000/` を開き、必要ならパスを入力して「チェック開始」を押します。
4. 結果一覧を確認し、必要に応じてメール作成リンクをクリックします。
5. 出力ファイルは `results/YYYYMM/` に保存されます。

## 氏名ゆれ辞書の作り方

- `name_dictionary.csv` のような CSV または JSON を用意します。
- CSV の場合は `元の表記,正規化後` の2列で作成します。
- JSON の場合は `{ "旧表記": "正規化後" }` の形式にします。

## 社員マスタの列名仕様

- 氏名列に「氏名」という文字を含めてください。
- メール列に「メール」または「email」を含めてください。

## フォルダ構成

```
attendance-check-app/
├─ app/
├─ templates/
├─ static/
├─ data_samples/
├─ config.sample.yaml
├─ requirements.txt
├─ run.bat
└─ README.md
```

## 実行例

```bash
python -m app.main --config config.yaml
```
