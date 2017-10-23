from flask import Flask, render_template

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1


@app.route('/')
def home():
    return render_template("index_mairies.html")


if __name__ == '__main__':
    app.run(debug=True)
