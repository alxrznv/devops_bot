import logging
import re
from dotenv import load_dotenv
import paramiko
import os

from typing import List

import psycopg2
from psycopg2 import Error

load_dotenv()

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database = os.getenv('DB_DATABASE')

token = os.getenv('TOKEN')
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

TOKEN = token

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

def find_phone_number(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+?7|8) \(\d{3}\) \d{3} \d{2} \d{2}|(?:\+?7|8)\d{10}|(?:\+?7|8)\(\d{3}\)\d{7}|(?:\+?7|8) \d{3} \d{3} \d{2} \d{2}|(?:\+?7|8)-\d{3}-\d{3}-\d{2}-\d{2}')  # формат 8 (000) 000-00-00

    global phoneNumberList

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    update.message.reply_text('Хотите сохранить данные? да/нет')

    return 'save_phone_numbers'

    return ConversationHandler.END

def save_phone_numbers(update: Update, context):
    user_input2 = update.message.text
    if user_input2 == 'нет':
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    if user_input2 == 'да':
        connection = None

        try:
            connection = psycopg2.connect(user=db_username,
                                            password=db_password,
                                            host=db_host,
                                            port=db_port,
                                            database=db_database)

            cursor = connection.cursor()
            for phone in phoneNumberList:
                cursor.execute("INSERT INTO phones (phone) VALUES (%s);", (phone,))
            connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text('Данные успешно сохранены')
            return ConversationHandler.END
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Не удалось сохранить данные')
            return ConversationHandler.END
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронных адресов: ')

    return 'find_email'

def find_email(update: Update, context):
    user_input = update.message.text

    emailRegex = re.compile(r'[A-Za-z0-9._%+-]{1,}\@[A-Za-z0-9.-]{1,}\.[A-Za-z]{2,}')

    global emailList

    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text('Электронные адреса не найдены')
        return ConversationHandler.END

    emails = ''
    for i in range(len(emailList)):
        emails += f'{i + 1}. {emailList[i]}\n'

    update.message.reply_text(emails)
    update.message.reply_text('Хотите сохранить данные? да/нет')
    return 'save_emails'

    return ConversationHandler.END

def save_emails(update: Update, context):
    user_input2 = update.message.text
    if user_input2 == 'нет':
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    if user_input2 == 'да':
        connection = None

        try:
            connection = psycopg2.connect(user=db_username,
                                            password=db_password,
                                            host=db_host,
                                            port=db_port,
                                            database=db_database)

            cursor = connection.cursor()
            for email in emailList:
                cursor.execute("INSERT INTO emails (email) VALUES (%s);", (email,))
            connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text('Данные успешно сохранены')
            return ConversationHandler.END
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Не удалось сохранить данные')
            return ConversationHandler.END
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки его сложности: ')

    return 'verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text

    passwordRegex = re.compile(r'(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*()])[0-9a-zA-Z!@#$%^&*()]{8,}')

    passwordList = passwordRegex.findall(user_input)

    if not passwordList:
        update.message.reply_text('Пароль простой')
        return ConversationHandler.END

    update.message.reply_text('Пароль сложный')
    return ConversationHandler.END

def getreleaseCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('cat /etc/os-release')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getunameCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getuptimeCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getdfCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getfreeCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getmpstatCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getwCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getauthsCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('last -10')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getcriticalCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('journalctl -p crit -n 5')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getpsCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getssCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ss -t -n')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getservicesCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('service --status-all')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getaptlistCommand(update: Update, context):
    update.message.reply_text('Если вы хотите посмотреть все пакеты, введите <allpack> Если вы хотите посмотреть информацию о конкретном пакете, введите его название')

    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text

    getRegex = re.compile(r'allpack')

    getList = getRegex.findall(user_input)

    if not getList:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command(f'dpkg -l | grep {user_input}')
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)
        return ConversationHandler.END

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('dpkg -l | head -n 30')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

    return ConversationHandler.END  # Завершаем работу обработчика диалога

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def getrepllogsCommand(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('tail -n 15 grep "replication" /var/log/postgresql/postgresql.log')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getemailsCommand(update: Update, context):
    connection = None

    try:
        connection = psycopg2.connect(user=db_username,
                                      password=db_password,
                                      host=db_host,
                                      port=db_port,
                                      database=db_database)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()

        message_text = ""
        for row in data:
            message_text += f"{row}\n"

        update.message.reply_text(message_text)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def getphonesCommand(update: Update, context):
    connection = None

    try:
        connection = psycopg2.connect(user=db_username,
                                      password=db_password,
                                      host=db_host,
                                      port=db_port,
                                      database=db_database)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phones;")
        data = cursor.fetchall()

        message_text = ""
        for row in data:
            message_text += f"{row}\n"

        update.message.reply_text(message_text)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'save_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, save_phone_numbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'save_emails': [MessageHandler(Filters.text & ~Filters.command, save_emails)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getaptlistCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", getreleaseCommand))
    dp.add_handler(CommandHandler("get_uname", getunameCommand))
    dp.add_handler(CommandHandler("get_uptime", getuptimeCommand))
    dp.add_handler(CommandHandler("get_df", getdfCommand))
    dp.add_handler(CommandHandler("get_free", getfreeCommand))
    dp.add_handler(CommandHandler("get_mpstat", getmpstatCommand))
    dp.add_handler(CommandHandler("get_w", getwCommand))
    dp.add_handler(CommandHandler("get_auths", getauthsCommand))
    dp.add_handler(CommandHandler("get_critical", getcriticalCommand))
    dp.add_handler(CommandHandler("get_ps", getpsCommand))
    dp.add_handler(CommandHandler("get_ss", getssCommand))
    dp.add_handler(CommandHandler("get_services", getservicesCommand))
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(CommandHandler("get_repl_logs", getrepllogsCommand))
    dp.add_handler(CommandHandler("get_emails", getemailsCommand))
    dp.add_handler(CommandHandler("get_phone_numbers", getphonesCommand))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
