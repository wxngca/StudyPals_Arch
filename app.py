from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


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

    def availability_list(self):
        slots = []
        if self.day and "|" in self.day:
            for item in self.day.split(";"):
                item = item.strip()
                if not item:
                    continue
                if "|" in item:
                    day, time = item.split("|", 1)
                    slots.append((day.strip(), time.strip()))
        elif self.day and self.time and self.time != "multi":
            slots.append((self.day.strip(), self.time.strip()))
        return slots

    def availability_display(self):
        slots = self.availability_list()
        if not slots:
            return "No availability selected"
        return ", ".join([f"{day} {time}" for day, time in slots])

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
    people_raw = request.form.get('people')
    try:
        people_value = int(people_raw) if people_raw is not None else None
    except ValueError:
        people_value = None

    if people_value is None:
        return render_template('index.html', error="Please enter a valid number of people.")

    email = request.form.get('email')
    if email and User.query.filter_by(email=email).first():
        return render_template('index.html', error="That email is already in use. Please use a different email.")

    availability = request.form.get('availability', '').strip()
    if not availability:
        return render_template('index.html', error="Please select at least one availability slot.")

    new = User(
        username=request.form.get('username'),
        email=email,
        courses=request.form.get('courses', " ").strip(),
        day=availability,
        time="multi",
        people=people_value)


    db.session.add(new)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return render_template('index.html', error="That email is already in use. Please use a different email.")
    result = find_matches(new)
    return render_template('results.html', user = new, result = result)

@app.route('/seed')
def seed():
    existing_emails = {u.email for u in User.query.all()}
    samples = [
        dict(username="Maya Brooks", email="maya@example.com", courses="CS 101, MATH 210", day="Monday|Evening;Tuesday|Evening", time="multi", people=3),
        dict(username="Jordan Lee", email="jordan@example.com", courses="CS 101, HIST 3", day="Monday|Evening;Thursday|Afternoon", time="multi", people=3),
        dict(username="Priya Patel", email="priya@example.com", courses="BIO 120, MATH 210", day="Wednesday|Afternoon", time="multi", people=3),
        dict(username="Luis Gomez", email="luis@example.com", courses="CS 101, PHYS 2", day="Monday|Morning;Wednesday|Morning", time="multi", people=3),
        dict(username="Zoe Kim", email="zoe@example.com", courses="HIST 3, ART 55", day="Friday|Evening;Saturday|Evening", time="multi", people=3),
    ]

    created = 0
    for sample in samples:
        if sample["email"] in existing_emails:
            continue
        db.session.add(User(**sample))
        created += 1

    if created:
        db.session.commit()

    return render_template('index.html', error=f"Seeded {created} fictional users.")

def find_matches(new, n = None):
    if n is None:
        n = new.people
    other_users = User.query.filter(User.id != new.id).all()
    score_matches = []
    new_courses_list = new.courses_list()
    new_availability = set(new.availability_list())

    for user in other_users:
        score = 0
        other_courses = user.courses_list()

        for course in other_courses:
            if course.lower() in new_courses_list:
                score += 10

        other_availability = set(user.availability_list())
        overlap = len(new_availability.intersection(other_availability))
        if overlap:
            score += overlap * 4

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
