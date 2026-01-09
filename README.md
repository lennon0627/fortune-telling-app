# 究極の運勢占いアプリ

5種類の占術（九星気学、四柱推命、五星三心、カバラ数秘術、宿曜占星術）で完全鑑定するWebアプリケーションです。

## ローカル開発環境のセットアップ

### 1. 必要なパッケージのインストール

```bash
pip install --break-system-packages -r requirements.txt
```

### 2. ローカルサーバーの起動

```bash
uvicorn main:app --reload
```

サーバーが起動したら、ブラウザで以下のURLにアクセス:
- http://127.0.0.1:8000/

### 3. 開発中の確認

- API動作確認: http://127.0.0.1:8000/docs
- 占いアプリ: http://127.0.0.1:8000/

## ファイル構成

```
fortune-telling-app/
├── main.py              # FastAPI バックエンド
├── requirements.txt     # Python依存パッケージ
├── start.sh            # Render起動スクリプト
├── README.md           # このファイル
└── static/             # 静的ファイル
    ├── index.html      # フロントエンド HTML
    ├── script.js       # JavaScript
    └── styles.css      # CSS
```

## Render.comへのデプロイ手順

### 1. GitHubリポジトリの作成

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fortune-telling-app.git
git push -u origin main
```

### 2. Renderでの設定

1. [Render.com](https://render.com/)にログイン
2. 「New +」→「Web Service」を選択
3. GitHubリポジトリを連携
4. 以下の設定を行う:

```
Name: my-fortune-api (または任意の名前)
Region: Singapore (または任意)
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: sh start.sh
```

5. 「Create Web Service」をクリック

### 3. デプロイ完了後

デプロイが完了すると、以下のようなURLが発行されます:
```
https://my-fortune-api.onrender.com
```

このURLにアクセスすると占いアプリが表示されます。

## トラブルシューティング

### ローカルで動かない場合

1. Pythonのバージョンを確認（3.9以上推奨）
```bash
python --version
```

2. 依存パッケージを再インストール
```bash
pip install --break-system-packages -r requirements.txt
```

3. ポートが使用中の場合
```bash
uvicorn main:app --reload --port 8001
```

### Renderでデプロイエラーが出る場合

1. ログを確認
2. requirements.txtの内容を確認
3. start.shの権限を確認（`chmod +x start.sh`）

## 機能

- 生年月日・時刻入力による5種類の占術鑑定
- 2026年の総合運勢スコア表示（108通りのランキング）
- レーダーチャートによる五行バランス可視化
- 結果のテキストコピー機能
- Gemini/ChatGPTへのワンクリック連携

## 技術スタック

- **バックエンド**: FastAPI, Python
- **フロントエンド**: Vanilla JavaScript, HTML, CSS
- **占術計算**: lunardate（旧暦変換）
- **可視化**: Chart.js（レーダーチャート）
- **デプロイ**: Render.com

## ライセンス

個人利用・商用利用ともに自由です。
# fortune-telling-app
