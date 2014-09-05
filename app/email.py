"""
    For the ability of sending emails in the app.
    Must set the config.py first.
"""


from threading import Thread
from flask import current_app, render_template
from flask.ext.mail import Message
from . import mail

# we send asynchronous emails because otherwise we would have the
# browser unresponsive during some time. To avoid this, the email
# send function is moved to the background thread.
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# Takes the destination address, a subject line, a template and
# make a thread to send this email.
# The template must be given without the extension so that we can
# have both plain and rich text bodies
def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['ANTISOCIAL_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['ANTISOCIAL_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
