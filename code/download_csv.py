import helper
import logging
from telegram import InputFile
from telegram.error import TelegramError
from telebot import types
import csv
import os

def run(message, bot):
    try:
        chat_id = message.chat.id
        user_history = helper.getUserHistory(chat_id)
        
        if not user_history:
            bot.send_message(chat_id, "you have no history to generate CSV file.")
            return None

        file_path = 'code/Expenses_Data.csv'
        column_names = ['Date and Time', 'Category', 'Amount', 'Account Type']

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            writer.writerows(csv.reader(user_history, delimiter=','))

        with open(file_path, 'rb') as file:
            try:
                bot.send_document(chat_id, document=file)
            except Exception as send_error:
                logging.error(f"Error sending document: {str(send_error)}")
                bot.send_message(chat_id, "Error: Failed to send the document.")
                return None

        return file_path

    except FileNotFoundError as e:
        logging.error(f"File not found error: {str(e)}")
        bot.send_message(chat_id, "Error: File not found.")
    except PermissionError as e:
        logging.error(f"Permission error: {str(e)}")
        bot.send_message(chat_id, "Error: Permission issue while accessing the file.")
    except csv.Error as e:
        logging.error(f"CSV error: {str(e)}")
        bot.send_message(chat_id, "Error: CSV file generation failed.")
    except TelegramError as e:
        logging.error(f"Telegram error: {str(e)}")
        bot.send_message(chat_id, "Error: Telegram communication issue.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        bot.send_message(chat_id, "An unexpected error occurred. Please try again later.")