from flask import Flask, render_template, request
from datetime import date
from portoflio import Portfolio
import requests
import smtplib
import os

EMAIL = os.environ["OWN_EMAIL"]
PASSWORD = os.environ["OWN_PASSWORD"]
RECIPIENT = os.environ["RECIPIENT"]

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

app = Flask(__name__)
current_year = date.today().year


@app.route('/')
def get_all_case_studies():
    return render_template('index.html', year=current_year, portfolio=portfolio_objects)


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
