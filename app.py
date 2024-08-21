from flask import Flask
import routes

app = Flask(__name__)

# routes.pyのルートをインポート
app.registter_blueprint(routes.bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)