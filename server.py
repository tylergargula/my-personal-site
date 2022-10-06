from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
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
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
current_year = date.today().year

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///client_portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=True)
    tagline = db.Column(db.String(250), nullable=True)
    description = db.Column(db.String(250), nullable=True)
    image = db.Column(db.String(250), nullable=True)
    body = db.Column(db.String(500), nullable=True)
    cms = db.Column(db.String(250), nullable=True)
    urls_migrated = db.Column(db.Integer, nullable=True)
    services = db.Column(db.String(250), nullable=True)
    industry = db.Column(db.String(250), nullable=True)

    def __repr__(self):
        return f'Case Study: {self.title}'


db.create_all()

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


class AddForm(FlaskForm):
    new_title = StringField('Enter a title tag for your client project', validators=[DataRequired()])
    new_subtitle = StringField('Enter a subtitle for your client project', validators=[DataRequired()])
    new_tagline = StringField('Enter a tagline for your client project', validators=[DataRequired()])
    new_description = StringField('Enter a description for your client project', validators=[DataRequired()])
    new_image = StringField('Enter the image file path', validators=[DataRequired()])
    new_body = StringField('Enter body content for your client project', validators=[DataRequired()])
    new_cms = StringField('Enter the cms used for your client project', validators=[DataRequired()])
    new_urls_migrated = StringField('Enter the # of URLs migrated for your client project', validators=[DataRequired()])
    new_services = StringField('Enter the services performed for the project', validators=[DataRequired()])
    new_industry = StringField('Enter the client industry', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def get_all_case_studies():
    return render_template('index.html', year=current_year, portfolio=portfolio_objects)


@app.route('/add', methods=['GET', 'POST'])
def add_work():
    add_client_form = AddForm()
    if add_client_form.validate_on_submit():
        new_client = Client(
            title=add_client_form.new_title.data,
            subtitle=add_client_form.new_subtitle.data,
            tagline=add_client_form.new_tagline.data,
            description=add_client_form.new_description.data,
            image=add_client_form.new_image.data,
            body=add_client_form.new_body.data,
            cms=add_client_form.new_cms.data,
            urls_migrated=add_client_form.new_urls_migrated.data,
            services=add_client_form.new_services.data,
            industry=add_client_form.new_industry.data,

        )

        db.session.add(new_client)
        db.session.commit()
        print("Added client successfully")
    return render_template('add.html', form=add_client_form)


@app.route('/work/<int:index>-<path>')
def show_portfolio(index, path):
    requested_portfolio = None

    for case_study in portfolio_objects:
        if case_study.id == index:
            requested_portfolio = case_study
    return render_template("portfolio.html", year=current_year, portfolio=requested_portfolio)


@app.route('/work')
def all_work():
    return render_template("work.html", year=current_year, portfolio=portfolio_objects)


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
    app.run(debug=True)
