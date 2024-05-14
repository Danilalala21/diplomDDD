import os

# роли пользователей в системе
ADMINISTRATOR = 'admin'

# Путь к текущему каталогу
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Путь к папке "static" в текущем каталоге
STATIC_FOLDER = os.path.join(CURRENT_DIRECTORY, 'static')

# Путь к папке 'logs" в текущем каталоге
LOG_FOLDER = os.path.join(CURRENT_DIRECTORY, 'logs')

# Путь к папке "images" в текущем каталоге
IMAGES_FOLDER = os.path.join(STATIC_FOLDER, 'img')
