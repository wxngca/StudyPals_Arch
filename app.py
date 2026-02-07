from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    courses = db.Column(db.String(200), nullable=False)
    availability = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    people = db.Column(db.Integer, nullable = False)

    def courses_list(self):
        courses_list = []
        for course in self.courses.split(","):
            course1 = course.strip()
            if course1 :
                courses_list.append(course1)

        return courses_list

    def __repr__(self):
        return (f"User('{self.username}', '{self.email}', '{self.courses}', '{self.availability}', "
                f"'{self.location}', '{self.people}')")

with app.app_context():
    db.create_all()
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    new = User(
        username=request.form.get('username'),
        email=request.form.get('email'),
        courses=request.form.get('courses').lower(),
        availability=request.form.get('availability'),
        location=request.form.get('location'),
        people=int(request.form.get('people')))

    db.session.add(new)
    db.session.commit()
    return "You create a new user successfully"

if __name__ == '__main__':
    app.run(debug = True)
