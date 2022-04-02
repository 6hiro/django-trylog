from django.core.mail import EmailMessage


class Util:
    # インスタンス化せずに呼び出せる関数（第一引数にselfを受け取らない）
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()
