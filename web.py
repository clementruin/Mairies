from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/database_01.db'
db = SQLAlchemy(app)

class Mairies(db.Model):
    __tablename__ = 'mairies'
    insee_code = db.Column( "insee_code", db.Integer, primary_key=True)
    postal_code = db.Column("postal_code", db.Integer)
    city = db.Column("city", db.Unicode)
    first_name = db.Column("first_name", db.Unicode)
    last_name = db.Column("last_name", db.Unicode)
    party = db.Column("party", db.Unicode)

@app.route('/')
def accueil():
    base = Mairies.query.all()
    return render_template('home.html', base=base)

if __name__ == '__main__':
    app.run(debug=True)