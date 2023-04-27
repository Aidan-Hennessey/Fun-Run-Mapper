from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def result():
    print(request.form['full_data']) # should display 'bar'
    return 'Received !' # response to your request.

if __name__ == "__main__":
    app.run()
