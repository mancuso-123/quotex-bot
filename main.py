import telebot
from quotexpy import Quotex
import threading

import os
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)
users = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Envíame tu correo y contraseña (ej: correo@gmail.com,clave123)")
    bot.register_next_step_handler(m, recibir_credenciales)

def recibir_credenciales(m):
    try:
        correo, clave = m.text.split(",")
        users[m.chat.id] = {"email": correo.strip(), "password": clave.strip(), "qx": None}
        bot.send_message(m.chat.id, "¿Quieres operar en cuenta demo o real? (responde: demo o real)")
        bot.register_next_step_handler(m, recibir_modo)
    except:
        bot.send_message(m.chat.id, "❌ Formato inválido. Usa: correo,contraseña")

def recibir_modo(m):
    modo = m.text.strip().lower()
    demo = True if modo == "demo" else False
    users[m.chat.id]["demo"] = demo
    bot.send_message(m.chat.id, "¿Cuánto quieres invertir por operación?")
    bot.register_next_step_handler(m, recibir_monto)

def recibir_monto(m):
    try:
        monto = float(m.text.strip())
        user = users[m.chat.id]
        qx = Quotex(email=user["email"], password=user["password"])
        if not qx.check_connect():
            bot.send_message(m.chat.id, "❌ Error al iniciar sesión en Quotex.")
            return
        qx.change_balance("demo" if user["demo"] else "real")
        user["qx"] = qx
        user["monto"] = monto
        bot.send_message(m.chat.id, "✅ Configurado. Escribe /iniciar para comenzar.")
    except:
        bot.send_message(m.chat.id, "❌ Monto inválido.")

@bot.message_handler(commands=['iniciar'])
def iniciar(m):
    user = users.get(m.chat.id)
    if not user or not user.get("qx"):
        bot.send_message(m.chat.id, "⚠️ Primero usa /start y configura tu cuenta.")
        return
    bot.send_message(m.chat.id, "🚀 Bot iniciado. Ejecutando operación...")
    threading.Thread(target=operar, args=(m.chat.id,)).start()

def operar(chat_id):
    user = users[chat_id]
    qx = user["qx"]
    success, id_op = qx.buy(amount=user["monto"], active="EURUSD", direction="call", duration=1)
    if success:
        bot.send_message(chat_id, "✅ Operación ejecutada con éxito.")
    else:
        bot.send_message(chat_id, "❌ Falló la operación.")

bot.polling()
