import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_order_email(user_email, order_details):
    """
    Отправляет детали заказа на указанную почту.

    Args:
    user_email (str): Адрес электронной почты получателя.
    order_details (str): Текст с деталями заказа.
    """
    # Электронная почта и пароль отправителя
    sender_email = "your-email@gmail.com"
    sender_password = "your-password"
    
    # Создание сообщения
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = user_email
    message['Subject'] = "Детали вашего заказа"

    # Добавление текста письма
    body = f"Здравствуйте! Спасибо за ваш заказ.\n\nДетали заказа:\n{order_details}"
    message.attach(MIMEText(body, 'plain'))

    # Подключение к серверу и отправка
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Активация TLS
            server.login(sender_email, sender_password)
            text = message.as_string()
            server.sendmail(sender_email, user_email, text)
            print("Письмо отправлено успешно!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
