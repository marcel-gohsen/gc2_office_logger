import os
import datetime
from threading import Timer

mail_template = \
    "mail from: marcel.gohsen@uni-weimar.de\n" \
    "rcpt to: {}\n" \
    "data\n" \
    "Subject: Erinnerung: Office Logger starten!\n" \
    "\n" \
    "Hallo {}\n\n" \
    "Danke, dass du an unserer Studie teilnimmst.\n" \
    "Bitte vergesse nicht den Office Logger zu starten.\n\n" \
    "Vielen Dank!\n\n" \
    "Mit freundlichen Gruessen,\n" \
    "Marcel Gohsen\n" \
    ".\n"


def broadcast_mail():
    with open("../../data/mailing-list.csv") as mailing_list:
        for contact in mailing_list:
            if not contact.startswith("#"):
                attr = contact.replace("\n", "").split(",")

                name = attr[0].strip("\"")
                mail = attr[1].strip("\"")

                os.system("echo \"" + mail_template.format(mail, name) + "\" | telnet mailgate.uni-weimar.de 25")


def main():
    while True:
        today = datetime.datetime.today()
        # tomorrow = today
        tomorrow = today.replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        delta = tomorrow - today

        timer = Timer(delta.total_seconds(), broadcast_mail)
        timer.run()


if __name__ == '__main__':
    main()