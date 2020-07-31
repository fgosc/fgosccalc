# 開発者向けドキュメント

## Web 版をローカルで動かす

- pipenv/venv/virtualenv 等による環境分離については触れません。必要に応じて各自でお願いします。
- npm が使える状態にしておいてください。

依存ライブラリをインストールします。

```
pip install -r requirements-gcloud.txt
npm install
```

JS ファイルをビルドします。
`make` コマンドが使える場合は `make` でもよいです。
デフォルトターゲットが `npm run build` の実行になっています。

```
npm run build
```

これで `static/dist` の下に成果物の JS ファイルが生成されます。
この状態でローカル用の Web サーバーを起動します。

```
python main.py
```

準備が整ったので `http://localhost:8080/ にアクセスします。
