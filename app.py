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
    day = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    people = db.Column(db.Integer, nullable = False)

    def courses_list(self):
        courses_list = []
        for course in self.courses.split(","):
            course1 = course.strip()
            if course1 :
                courses_list.append(course1)

        return courses_list

    def __repr__(self):
        return (f"User('{self.username}', '{self.email}', '{self.courses}', '{self.day}', "
                f"'{self.time}', '{self.people}')")

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
        courses=request.form.get('courses', " ").lower(),
        day=request.form.get('day'),
        time=request.form.get('time'),
        people=int(request.form.get('people')))


    db.session.add(new)
    db.session.commit()
    result = find_matches(new)
    return render_template('results.html', user = new, result = result)

def find_matches(new, n = None):
    if n is None:
        n = new.people
    other_users = User.query.filter(User.id != new.id).all()
    score_matches = []
    new_courses_list = new.courses_list()

    for user in other_users:
        score = 0
        other_courses = user.courses_list()

        for course in other_courses:
            if course.lower() in new_courses_list:
                score += 10

        if new.day == user.day:
            score += 5

        if new.time == user.time:
            score += 3

        if score > 0:
            score_matches.append((user, score))

    length = len(score_matches)
    for i in range(length):
        max_idx = i
        for j in range(i + 1, length):
            if score_matches[j][1] > score_matches[max_idx][1]:
                max_idx = j

        score_matches[i], score_matches[max_idx] = score_matches[max_idx], score_matches[i]

    final_results = []

    count = 0
    for score1 in score_matches:
        if count < n:
            user_obj = score1[0]
            final_results.append(user_obj)
            count += 1
        else:
            break

    return final_results

if __name__ == '__main__':
    app.run(debug = True)