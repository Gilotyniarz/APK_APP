from flask import Flask, render_template, request, url_for, redirect, session, make_response
from flask_mail import Mail, Message
import os
import pdfkit
import sys, subprocess, platform

def _get_pdfkit_config():
    """wkhtmltopdf lives and functions differently depending on Windows or Linux. We
     need to support both since we develop on windows but deploy on Heroku.

    Returns:
        A pdfkit configuration
    """
    if platform.system() == 'Windows':
        return pdfkit.configuration(
            wkhtmltopdf=os.environ.get('WKHTMLTOPDF_BINARY', 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'))
    else:
        WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')],
                                           stdout=subprocess.PIPE).communicate()[0].strip()
        return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)

    def make_pdf_from_url(url, options=None):
        """Produces a pdf from a website's url.
        Args:
            url (str): A valid url
            options (dict, optional): for specifying pdf parameters like landscape
                mode and margins
        Returns:
            pdf of the website
        """
        return pdfkit.from_url(url, False, configuration=_get_pdfkit_config(), options=options)

    def make_pdf_from_raw_html(html, options=None):
        """Produces a pdf from raw html.
        Args:
            html (str): Valid html
            options (dict, optional): for specifying pdf parameters like landscape
                mode and margins
        Returns:
            pdf of the supplied html
        """
        return pdfkit.from_string(html, False, configuration=_get_pdfkit_config(), options=options)

# @@@@@@@@@@@@@@@@@@ Config @@@@@@@@@@@@@@@@@@

# @@@@@@@@@@@@@@@@@@ CONST @@@@@@@@@@@@@@@@@@@
MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASSWORD = os.environ.get("MY_PASSWORD")
LESS_SECURE_APPS = os.environ.get("LESS_SECURE_APPS")
SECRET_KEY = os.environ.get("SECRET_KEY")
# @@@@@@@@@@@@@@@@@ CONFIG @@@@@@@@@@@@@@@@@@@@@@
app = Flask(__name__)
# @@@@@@@@@@@@@@@@@@@@@@ Session @@@@@@@@@@@@@@@@@@@@@
app.secret_key = SECRET_KEY
# @@@@@@@@@@@@@@@@@@@@@@@@@@ MAIL @@@@@@@@@@@@@@@@@@@@@@@@
app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=MY_EMAIL,
    MAIL_PASSWORD=LESS_SECURE_APPS,

))
mail = Mail(app)


@app.route('/')
def base():
    return render_template("index.html")


@app.route('/agent/<agent>')
def what_agent(agent):
    session["agent"] = agent
    print(session["agent"])
    return render_template("clear.html")


@app.route('/test', methods=["POST", "GET"])
def test():
    if request.method == 'POST':
        pojazd = request.form.get("pojazd")
        dom = request.form.get("dom")
        podroz = request.form.get("podroz")
        zycie = request.form.get("zycie")
        rolne = request.form.get("rolne")
        firma = request.form.get("firma")
        return redirect(url_for("form", pojazd=pojazd, dom=dom, podroz=podroz, zycie=zycie, rolne=rolne, firma=firma))
    return render_template("index_1.html")


@app.route("/form/<int:pojazd><int:dom><int:zycie><int:podroz><int:rolne><int:firma>", methods=["POST", "GET"])
def form(pojazd, dom, podroz, zycie, rolne, firma):
    if request.method == 'POST':

        # @@@@@@@@@@@@@@@@@@@@@@@ wyciagniecie danych do bazy danych@@@@@@@@@@@@@@@@@@@@

        session["form_name"] = request.form.get("name")
        session["form_lastname"] = request.form.get("lastname")
        session["form_email"] = request.form.get("email")
        session["form_message"] = request.form.get("message")

        # @@@@@@@@@@@@@@@@@@@@@ opracowanie wszystkich danynch z arkusza @@@@@@@@@@@@@@@@@@@
        raw_submit = request.form.items()
        list_submit = []
        for part in raw_submit:
            str_part = ",".join(part)
            list_submit.append(str_part)
        list_submit_reversed = list_submit[::-1]
        list_submit_only_insurance = list_submit_reversed[4:]
        string_submit = ",".join(list_submit_only_insurance)
        session["insurance"] = string_submit

        return redirect(url_for("full"))
    return render_template("index_2.html", pojazd=pojazd, dom=dom, podroz=podroz, zycie=zycie, rolne=rolne, firma=firma)


@app.route('/full', methods=["POST", "GET"])
def full():
    # @@@@@@@@@@@@@@@@ DEFAULT AGENT @@@@@@@@@@@@@@@@
    if "agent" in session:
        pass
    else:
        session["agent"] = MY_EMAIL
    products = session["insurance"].split(",")[::2]  # converting session str to list

    # @@@@@@@@@@@@@@@@ CONVERSING HTML TO PDF @@@@@@@@@@@@@@@@@

    rendered_pdf = render_template('messages/message_pdf.html', products=products)
    pdf = pdfkit.from_string(rendered_pdf, False)

    # @@@@@@@@@@@@@@@ SENDING MAIL @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    msg = Message(f'{session["form_name"]} {session["form_lastname"]} - APK', sender='APK - Podsumowanie',
                  recipients=[session.get("agent"), MY_EMAIL])
    msg.html = render_template("messages/message.html", products=products)
    # @@@@@@@@@@@@@@@ Adding Attachment pdf @@@@@@@@@@@@@@@@@@@@
    msg.attach(f"{session['form_name']} {session['form_lastname']}-APK", "invoice/pdf", pdf)
    mail.send(msg)

    return render_template("index_4_win.html")


@app.route('/message')
def message():
    return render_template("messages/message.html")


@app.route('/ok')
def ok():
    return render_template("index_4_win.html")


if __name__ == '__main__':
    app.run(debug=True)
