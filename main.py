import os
import telebot
from quotexpy import Quotex
import threading

# Leer el token desde variables de entorno
TOKEN = os.getenv('TOKEN')  # Asegúrate de configurar esto en Render

bot = telebot.TeleBot(TOKEN)
users = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Envíame tu correo y clave separados por coma (ej: correo@gmail.com,123456)")
    bot.register_next_step_handler(m, recibir_credenciales)

def recibir_credenciales(m):
    try:
        correo, clave = m.text.split(",")
        users[m.chat.id] = {"email": correo.strip(), "password": clave.strip()}
        bot.send_message(m.chat.id, "¿Qué activo quieres operar? (ej: EURUSD, BTCUSD)")
        bot.register_next_step_handler(m, recibir_activo)
    except:
        bot.send_message(m.chat.id, "Formato inválido. Intenta de nuevo usando coma para separar.")

def recibir_activo(m):
    activo = m.text.strip().upper()
    datos = users.get(m.chat.id)
    if datos:
        threading.Thread(target=conectar_quotex, args=(m.chat.id, datos["email"], datos["password"], activo)).start()

def conectar_quotex(chat_id, correo, clave, activo):
    try:
        with Quotex(email=correo, password=clave) as q:
            if q.check_connect():
                bot.send_message(chat_id, f"✅ Conectado a Quotex. Operando en {activo}")
            else:
                bot.send_message(chat_id, "❌ Error al conectar con Quotex. Verifica tus datos.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

# Iniciar el bot
print("Bot iniciado...")
bot.polling()
