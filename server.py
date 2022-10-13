from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional
from flask_wtf import FlaskForm
from datetime import date
from portoflio import Portfolio
import requests
import smtplib
import os

EMAIL = os.environ["OWN_EMAIL"]
PASSWORD = os.environ["OWN_PASSWORD"]
RECIPIENT = os.environ["RECIPIENT"]

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY_CODE']
ckeditor = CKEditor(app)

# CONNECT TO DB
if os.environ['DATABASE_URL'] == None:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///client_portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Bootstrap(app)
current_year = date.today().year

portfolio = requests.get("https://api.npoint.io/78c54b6b0ae07e92852f").json()

portfolio_objects = []
for client in portfolio:
    portfolio_object = Portfolio(
        client["id"],
        client["title"].split(" - ")[0].replace(" ", "-").lower(),
        client["title"],
        client["subtitle"],
        client["tagline"],
        client["image"],
        client["body"],
        client["cms"],
        client["urlsMigrated"],
        client["services"],
        client["industry"]
    )
    portfolio_objects.append(portfolio_object)


# CONFIGURE TABLE
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    tagline = db.Column(db.String(250), nullable=True)
    image = db.Column(db.String(250), nullable=True)
    body = db.Column(db.String(500), nullable=True)
    cms = db.Column(db.String(250), nullable=True)
    urls_migrated = db.Column(db.Integer, nullable=True)
    services = db.Column(db.String(250), nullable=True)
    industry = db.Column(db.String(250), nullable=True)
    url_string = db.Column(db.String(250), nullable=True)


# db.create_all()


# WTForm
class AddForm(FlaskForm):
    title = StringField('Enter a title tag for your client project', validators=[DataRequired()])
    tagline = StringField('Enter a tagline for your client project', validators=[DataRequired()])
    image = StringField('Enter the image file path', validators=[DataRequired()])
    body = StringField('Enter body content for your client project', validators=[DataRequired()])
    cms = StringField('Enter the cms used for your client project', validators=[DataRequired()])
    urls_migrated = IntegerField('Enter the # of URLs migrated for your client project', validators=[Optional()])
    services = StringField('Enter the services performed for the project', validators=[DataRequired()])
    industry = StringField('Enter the client industry', validators=[DataRequired()])
    url_string = StringField('Enter url string path', validators=[DataRequired()])
    submit = SubmitField('Submit')


case_studies = Client.query.all()


@app.route('/')
def get_all_case_studies():
    print(case_studies)
    return render_template('index.html', year=current_year, portfolio=case_studies)


@app.route('/add', methods=['GET', 'POST'])
def add_work():
    form = AddForm()
    if form.validate_on_submit():
        new_client = Client(
            title=form.title.data,
            tagline=form.tagline.data,
            image=form.image.data,
            body=form.body.data,
            cms=form.cms.data,
            urls_migrated=form.urls_migrated.data,
            services=form.services.data,
            industry=form.industry.data,
            url_string=form.url_string.data
        )
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('get_all_case_studies'))
    return render_template('add.html', form=form)


@app.route('/work/<int:index>-<path>')
def show_portfolio(index, path):
    requested_portfolio = None

    for case_study in case_studies:
        if case_study.id == index:
            requested_portfolio = case_study
    return render_template("portfolio.html", year=current_year, portfolio=requested_portfolio)


@app.route('/work')
def all_work():
    return render_template("work.html", year=current_year, portfolio=case_studies)


@app.route('/apps')
def all_apps():
    return render_template("apps.html", year=current_year)


@app.route("/about")
def my_info():
    return render_template("about.html", year=current_year)


@app.route('/thank-you', methods=["POST"])
def receive_data():
    name = request.form["name"]
    first_name = name.split(" ", 1)[0]
    email = request.form["email"]
    message = request.form["message"]
    send_email(name, email, message)
    return render_template("thank-you.html", name=name, first_name=first_name, email=email, message=message)


def send_email(name, email, message):
    email_message = f"Subject: New Website Submission!\n\nName: {name}\nEmail: {email}\nMessage: {message}"
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=PASSWORD)
        connection.sendmail(
            from_addr=EMAIL,
            to_addrs=RECIPIENT,
            msg=email_message
        )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
