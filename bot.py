import telebot, re, datetime, json, gspread
from telebot import types
from oauth2client.service_account import ServiceAccountCredentials

bot = telebot.TeleBot("1998040406:AAEx-rUrdM_Z6YA068RzkcLh9VDsNwJsapk", parse_mode=None) 
# You can set parse_mode by default. HTML or MARKDOWN

user_dict = {}
        
scopes = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name("bot-clienti-trust-6f040f2e6b58.json", scopes) #access the json key you downloaded earlier 
file = gspread.authorize(credentials) # authenticate the JSON key with gspread
sheet = file.open("Call clienti Trust Investing")  #open sheet
sheet = sheet.sheet1  #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

class User:
    def __init__(self, name):
        self.name = None
        self.email = None
        self.date = None
        self.time = None

@bot.callback_query_handler(lambda query: query.data == "cb_newappt")
def send_welcome(message):
    try:
        msg = bot.reply_to(message, "Ciao! Fissa una video call con uno dei nostri rappresentanti 🚀😎\nSapranno chiarire tutti i tuoi dubbi 💸.\n\nDimmi il tuo nome: 👋")
        bot.register_next_step_handler(msg, process_name_step)
    except Exception as e:
        bot.reply_to(message, '❌ Oooops! Abbiamo riscontrato un errore, ci scusiamo!')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        msg = bot.reply_to(message, "Ciao! Fissa una video call con uno dei nostri rappresentanti 🚀😎\nSapranno chiarire tutti i tuoi dubbi 💸.\n\nDimmi il tuo nome: 👋")
        bot.register_next_step_handler(msg, process_name_step)
    except Exception as e:
        bot.reply_to(message, '❌ Oooops! Abbiamo riscontrato un errore, ci scusiamo!')
    
def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        user.name = name
        msg = bot.reply_to(message, 'Ora dimmi la tua e-mail in modo che possiamo contattarti: 📧')
        bot.register_next_step_handler(msg, process_email_step)
    except Exception as e:
        bot.reply_to(message, '❌ Oooops! Abbiamo riscontrato un errore, ci scusiamo!')
        
def process_email_step(message):
    try:
        chat_id = message.chat.id
        email = message.text
        
        if not (re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)):
            msg = bot.reply_to(message, '❌ Questo è un ID e-mail non valido. Ora dimmi la tua e-mail in modo che possiamo contattarti: 📧')
            bot.register_next_step_handler(msg, process_email_step)
            return

        user = user_dict[chat_id]
        user.email = email
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

        drss = []
        for i in range (1,32):
            drss.append((datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%d-%m-%Y"))
        
        markup.add(drss[0], drss[1], drss[2], drss[3], drss[4], drss[5], drss[6], drss[7], drss[8], drss[9], drss[10], drss[11], drss[12], drss[13], drss[14], drss[15], drss[16], drss[17], drss[18], drss[19], drss[20], drss[21], drss[22], drss[23], drss[24], drss[25], drss[26], drss[27], drss[28], drss[29])
        msg = bot.reply_to(message, "Scegli una data per l'appuntamento: 📅", reply_markup=markup)
        bot.register_next_step_handler(msg, process_date_step)
    except Exception as e:
        print(e)
        bot.reply_to(message, '❌ Oooops! Abbiamo riscontrato un errore, ci scusiamo!')

def process_date_step(message):
    try:
        chat_id = message.chat.id
        date = message.text
        user = user_dict[chat_id]
        user.date = date
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("9 AM - 10 AM", "10 AM - 11 AM", "11 AM - 12 PM", )
        msg = bot.reply_to(message, "Seleziona una fascia oraria per il tuo appuntamento: 🕐", reply_markup=markup)
        bot.register_next_step_handler(msg, process_time_step)
    except Exception as e:
        print(e)
        bot.reply_to(message, '❌ Oooops! Abbiamo riscontrato un errore, ci scusiamo!')

def process_time_step(message):
    try:
        chat_id = message.chat.id
        time = message.text
        user = user_dict[chat_id]
        bot.send_message(chat_id, r"Aspetta mentre confermo il tuo appuntamento. ")
        next_row = next_available_row(sheet)
        #insert on the next available row
        sheet.update_acell("A{}".format(next_row), str(user.name))
        sheet.update_acell("B{}".format(next_row), str(user.email))
        sheet.update_acell("C{}".format(next_row), str(user.date))
        sheet.update_acell("D{}".format(next_row), str(time))
        bot.send_message(chat_id, r"✅ Grande! " + str(user.name) + ", il tuo appuntamento è stato fissato per " + str(user.date) + " al momento: " + str(time) + ".\n\nTocca /start per prenotare un altro appuntamento.")

    except Exception as e:
        print(e)
        bot.reply_to(message, '❌ Oooops! Abbiamo riscontrato un errore, ci scusiamo!')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
        bot.send_message(m.chat.id, "Ciao! Fai una videochiamata con un nostro incaricato 🚀😎 \nSapranno chiarire tutti i tuoi dubbi 💸. \n\nPremi /start per continuare!")

bot.polling()