import calendar
import datetime

from datetime import date, timedelta
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/dan/PycharmProjects/30DayChallenge/db/challenge.db'
db = SQLAlchemy(app)


class ChallengeDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    sets_to_complete = db.Column(db.Integer)
    sets_completed = db.Column(db.Integer)

    def __init__(self, date_today, total_sets):
        self.sets_to_complete = total_sets
        self.date = date_today
        self.sets_completed = 0

    def __repr__(self):
        return '<ChallengeDay %r>' % self.date


@app.route('/challenge')
def challenge():
    now = datetime.datetime.now()
    spaces = date(now.year, now.month, 1).weekday()
    complete_days = ChallengeDay.query.all()
    completed_this_month = []
    num_days_complete = len(complete_days) - 1
    days_to_go = 30 - len(complete_days) + 1
    if not complete_days:
        today = ChallengeDay(now, 1)
        db.session.add(today)
    else:
        completed_this_month = [day.date.day for day in complete_days if day.date.month == now.month]
        today = ChallengeDay.query.filter_by(date=date.today()).first()
        yesterday = ChallengeDay.query.filter_by(date=date.today() - timedelta(days=1)).first()
        if yesterday:
            if yesterday.sets_to_complete != yesterday.sets_completed:
                ChallengeDay.query.delete()
            today = ChallengeDay.query.filter_by(date=date.today()).first()
            if not today:
                today = ChallengeDay(now, yesterday.sets_to_complete + 1)
                db.session.add(today)
            else:
                if today.sets_to_complete == today.sets_completed:
                    num_days_complete = len(complete_days)
                    days_to_go = 30 - len(complete_days)
                else:
                    completed_this_month.remove(today.date.day)
    hide_button = False
    if today:
        sets_to_go = today.sets_to_complete - today.sets_completed
        if today.sets_to_complete == today.sets_completed:
            hide_button = True
    db.session.commit()
    return render_template("index.html", num_completed=num_days_complete, completed=completed_this_month,
                           hide_button=hide_button, days_to_go=days_to_go, year=now.year,
                           month=calendar.month_name[now.month], spaces=spaces, sets_to_go=sets_to_go,
                           days=range(1, calendar.monthrange(now.year, now.month)[1] + 1), today=now.day)

@app.route('/completed')
def completed():
    today = ChallengeDay.query.filter_by(date=date.today()).first()
    print "before add - sets complete = %s" % today.sets_completed
    today.sets_completed += 1
    print "after add - sets complete = %s" % today.sets_completed
    db.session.commit()
    complete_days = ChallengeDay.query.all()
    num_days_complete = len(complete_days) - 1
    days_to_go = 30 - len(complete_days) + 1
    hide = 'false'
    print "before math - sets complete = %s" % today.sets_completed
    sets_to_go = today.sets_to_complete - today.sets_completed
    print "sets_to_go = %s" % sets_to_go
    if today.sets_completed == today.sets_to_complete:
        hide = 'true'
        num_days_complete = len(complete_days)
        days_to_go = 30 - len(complete_days)
    return jsonify({'hide': hide, 'num_completed': num_days_complete, 'days_to_go': days_to_go, 'sets_to_go': sets_to_go})

if __name__ == "__main__":
    app.run(debug=True)