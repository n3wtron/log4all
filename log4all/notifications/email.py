import smtplib

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


class EmailNotification(object):
    def __init__(self, settings):
        self.settings = settings

    def notify(self, log_id, user=None, recipients=None):
        log_id_detail_url = self.settings['log4all.url'] + "/detail/?id=" + str(log_id)
        headers = dict()
        headers['MIME-Version'] = '1.0'
        headers['Content-type'] = 'text/html'
        subject = "log4all notification\n"
        tos = ""
        if not recipients and user:
            recipients = [user['email']]
            tos = user['name'] + " " + user['surname'] + "<" + user['email'] + ">"
        else:
            for recipient in recipients:
                tos += "<" + recipient + ">, "
        headers['To'] = tos
        content = '<a href="' + log_id_detail_url + '">' + log_id_detail_url + "</a>"
        send_email(self.settings, recipients, subject, content, headers)


def send_email(settings, recipients, subject, content, headers=dict()):
    smtp_hostname = settings['smtp.hostname']
    smtp_port = int(settings['smtp.port'])
    from_address = settings['smtp.from_address']
    smtp_server = smtplib.SMTP(smtp_hostname, port=smtp_port)
    body = "From: Log4All <" + from_address + ">\n"
    for key in headers.keys():
        body += key + ": " + headers[key] + "\n"
    body += "Subject: " + subject + "\n\n"
    body += content
    smtp_server.sendmail(from_address, recipients, body)