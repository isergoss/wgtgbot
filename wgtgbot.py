import logging
import subprocess
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Начало диалога для получения имени пользователя
GET_USERNAME = range(1)

# Начало диалога для выбора DNS-сервера
GET_DNS_SERVER = range(1)

# Функция для обработки команды /start
def start(update, context):
    reply_keyboard = [['Купить']]
    update.message.reply_text(
        'Привет! Я помогу тебе создать файл конфигурации для WireGuard. Нажми "Купить", чтобы начать.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return GET_USERNAME

# Функция для обработки команды /buy и начала диалога
def buy(update, context):
    reply_keyboard = [['Google', '1.1.1.1'], ['AdGuard', 'OpenDNS'], ['Отмена']]
    update.message.reply_text(
        'Введите ваше имя пользователя.',
        reply_markup=ReplyKeyboardRemove()
    )
    return GET_USERNAME

# Функция для обработки сообщения с именем пользователя
def get_username(update, context):
    context.user_data['username'] = update.message.text
    update.message.reply_text(
        'Выберите DNS-сервер:',
        reply_markup=ReplyKeyboardMarkup(
            [['Google', '1.1.1.1'], ['AdGuard', 'OpenDNS'], ['Отмена']],
            one_time_keyboard=True
        )
    )
    return GET_DNS_SERVER

# Функция для обработки сообщения с выбранным DNS-сервером
def get_dns_server(update, context):
    dns_server = update.message.text
    if dns_server == 'Отмена':
        update.message.reply_text(
            'Операция отменена.',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    username = context.user_data['username']
    try:
        # Выполняем команды на сервере для создания файла конфигурации
        subprocess.run(['sudo', 'wg', 'genkey'], check=True, capture_output=True, text=True)
        output = subprocess.run(['sudo', 'wg', 'pubkey'], check=True, capture_output=True, text=True, input=stdin)
        pubkey = output.stdout.strip()
        subprocess.run(['sudo', 'touch', f'/etc/wireguard/{username}.conf'], check=True)
        subprocess.run(['sudo', 'chmod', '600', f'/etc/wireguard/{username}.conf'], check=True)
        with open(f'/etc/wireguard/{username}.conf', 'w') as f:
            f.write(f'[Interface]\nPrivateKey = {privkey}\nAddress = 10.0.0.1/24\nDNS = {dns_server}\n\n[Peer]\nPublicKey = {pubkey}\nAllowedIPs = 10.0.0.2/32')
        
        # Отправляем файл пользователю
        with open(f'/etc/wireguard/{username}.conf', 'rb') as f:
            update.message.reply_document(f, filename=f'{username}.conf')
        
        update.message.reply_text(
            'Файл конфигурации создан и отправлен вам.',
            reply_markup
