# ベースイメージとしてPythonを使用
FROM python:3.9-slim

# 作業ディレクトリを指定
WORKDIR /app

# 必要な第るをコンテナ内にコピー
COPY requirements.txt requirements.txt
COPY . .

# 必要なパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# Flaskアプリケーションを実行
CMD ["python", "app.py"]