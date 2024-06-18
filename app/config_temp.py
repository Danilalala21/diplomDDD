import logging
import datetime
import constant as c


today = datetime.date.today().strftime('%Y-%m-%d')


logging.basicConfig(
    level = logging.DEBUG,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format = '%(asctime)s - %(levelname)s - %(message)s',
    filename = f'{c.LOG_FOLDER}/{today}.log',  # Путь к файлу лога
    filemode = 'a'  # Режим записи (a - дополнение, w - перезапись)
)


DB_CONFIG = {
    'host':'localhost', 
    'user':'postgres',
    'password':'password',
    'dbname':'dbname',
    'port':5433}
