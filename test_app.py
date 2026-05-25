from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>测试成功！</h1><p>Railway 部署正常运行</p>'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
