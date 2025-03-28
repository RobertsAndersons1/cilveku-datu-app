import flask
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import os
from peewee import *
import csv

app = flask.Flask(__name__)


db = SqliteDatabase('people.db')

class FilteredPerson(Model):
    first_name = CharField()
    last_name = CharField()
    age = IntegerField()
    sex = CharField()

    class Meta:
        database = db



@app.route('/')
def home():
    return flask.render_template("home.html")

@app.route('/gender')
def gender_chart():
    df = pd.read_csv('people-1000.csv')
    gender_counts = df['Sex'].value_counts()


    plt.figure(figsize=(6, 6))
    gender_counts.plot(kind='bar', color=['yellow', 'purple'])
    plt.title('Dzimumu sadalījums pēc skaita')
    plt.xlabel("dzimums")
    plt.ylabel("skaits")
    bar_path = os.path.join('static', 'gender_bar.png')
    plt.savefig(bar_path)
    plt.close()

  
    plt.figure(figsize=(6, 6))
    plt.pie(gender_counts,
            labels=gender_counts.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=['skyblue', 'lightcoral'])
    plt.title('Dzimumu sadalījums procentos')
    pie_path = os.path.join('static', 'gender_pie.png')
    plt.savefig(pie_path)
    plt.close()

    return flask.render_template("gender.html",
                                 bar_url=bar_path,
                                 pie_url=pie_path)


@app.route('/age')
def age_histogram():
    df = pd.read_csv('people-1000.csv')
    df['Date of birth'] = pd.to_datetime(df['Date of birth'], errors='coerce')
    df = df.dropna(subset=['Date of birth'])
    today = pd.Timestamp.today()
    df['Age'] = df['Date of birth'].apply(lambda dob: (today - dob).days // 365)

    plt.figure(figsize=(8, 6))
    plt.hist(df['Age'], bins=10, color='yellow', edgecolor='black')
    plt.title("Vecuma sadalījums")
    plt.xlabel("vecums")
    plt.ylabel("cilvēku skaits")

    chart_path = os.path.join("static", "age_histogram.png")
    plt.savefig(chart_path)
    plt.close()


    return flask.render_template("age.html", chart_url=chart_path)


@app.route('/filter', methods=['GET', 'POST'])
def filter_people():
    df = pd.read_csv('people-1000.csv')
    df['Date of birth'] = pd.to_datetime(df['Date of birth'], errors='coerce')
    df = df.dropna(subset=['Date of birth'])
    today = pd.Timestamp.today()
    df['Age'] = df['Date of birth'].apply(lambda dob: (today - dob).days // 365)

    if flask.request.method == 'POST':
        gender = flask.request.form.get('gender')
        min_age = int(flask.request.form.get('min_age', 0))

        if gender:
            df = df[df['Sex'] == gender]

        df = df[df['Age'] >= min_age]

        results = df[['First Name', 'Last Name', 'Age', 'Sex']].to_dict(orient='records')
        FilteredPerson.delete().execute()
        for person in results:
            FilteredPerson.create(
                first_name=person['First Name'],
                last_name=person['Last Name'],
                age=person['Age'],
                sex=person['Sex']
            )

        return flask.render_template('filter.html', success=True)
    
    return flask.render_template('filter.html', success=False)


@app.route('/filtered')
def saved_people():
    people = FilteredPerson.select()
    return flask.render_template("filtered.html", people=people)


@app.route('/jobs')
def job_charts():
    df = pd.read_csv('people-1000.csv')

    top_10jobs_all = df['Job Title'].value_counts().head(10)
    plt.figure(figsize=(9,5))
    top_10jobs_all.plot(kind='barh', color='teal')
    plt.title("Top 10 profesijas")
    plt.xlabel("Cilvēku skaits")
    plt.tight_layout()
    plt.savefig('static/jobs_all.png')
    plt.close()


    top_10jobs_male = df[df['Sex'] == 'Male']['Job Title'].value_counts().head(10)
    plt.figure(figsize=(9,5))
    top_10jobs_male.plot(kind='barh', color='blue')
    plt.title("Top 10 profesijas vīriešiem")
    plt.xlabel("Cilvēku skaits")
    plt.tight_layout()
    plt.savefig('static/jobs_male.png')
    plt.close()


    top_10jobs_female = df[df['Sex'] == 'Female']['Job Title'].value_counts().head(10)
    plt.figure(figsize=(9,5))
    top_10jobs_female.plot(kind='barh', color='pink')
    plt.title("Top 10 profesijas sievietēm")
    plt.xlabel("Cilvēku skaits")
    plt.tight_layout()
    plt.savefig('static/jobs_female.png')
    plt.close()

    return flask.render_template("jobs.html")



db.connect()
db.create_tables([FilteredPerson])

if __name__ == '__main__':
    app.run(debug=True)