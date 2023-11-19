import helper
import logging
from telebot import types
from datetime import datetime

option = {}

# Main run function
def run(message, bot):
    helper.read_json()
    chat_id = message.chat.id
    option.pop(chat_id, None)  # remove temp choice
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    print("Account Categories:")
    for c in helper.getAccountCategories():
        print("\t", c)
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup = markup)
    bot.register_next_step_handler(msg, post_category_selection, bot)

# Contains step to run after the category is selected
def post_category_selection(message, bot):
    try:
        chat_id = message.chat.id
        selected_category = message.text
        if selected_category not in helper.getAccountCategories():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognize this category \"{}\"!".format(selected_category))

        option[chat_id] = selected_category
        message = bot.send_message(chat_id, 'How much money you want to add in {} account? \n(Enter numeric values only)'.format(str(option[chat_id])))
        bot.register_next_step_handler(message, post_amount_input, bot, selected_category)
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, 'Oh no! ' + str(e))
        display_text = ""
        commands = helper.getCommands()
        for c in commands:  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, 'Please select a menu option from below:')
        bot.send_message(chat_id, display_text)

# Contains step to run after the amount is inserted
def post_amount_input(message, bot, selected_category):
    try:
        chat_id = message.chat.id
        amount_entered = message.text
        amount_value = helper.validate_entered_amount(amount_entered)  # validate
        option[selected_category] = amount_value
        print("For {}.{}".format(chat_id, amount_value))
        if amount_value == 0:  # cannot be $0 spending
            raise Exception("Spent amount has to be a non-zero number.")

        date_of_entry = datetime.today().strftime(helper.getDateFormat() + ' ' + helper.getTimeFormat())
        account_str = option[selected_category]
        amount_str = str(amount_value)
        date_str = str(date_of_entry)

        helper.write_json(add_user_record(chat_id, "{},{},Inflow {}".format(date_str, selected_category, amount_str)))
        helper.write_json(update_account_balance_add(chat_id, selected_category, amount_value))
        bot.send_message(chat_id, 'The following expenditure has been recorded: You have Added ${} to {} account on {}'.format(amount_str, account_str, date_str))
        bot.send_message(chat_id, 'New Balance in {} account is: {}'.format(selected_category, helper.get_account_balance(message, bot, selected_category)))
        helper.display_account_balance(message, bot, selected_category)
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, 'Oh no. ' + str(e))

def update_account_balance_add(chat_id, cat, val):
    user_list = helper.read_json()
    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = helper.createNewUserRecord()

    if user_list[str(chat_id)]['balance'][cat] is None:
        user_list[str(chat_id)]['balance'][cat] = str(val)
    else:
        user_list[str(chat_id)]['balance'][cat] = str(float(val) + float(user_list[str(chat_id)]['balance'][cat]))
    return user_list

# Contains step to on user record addition
def add_user_record(chat_id, record_to_be_added):
    user_list = helper.read_json()
    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = helper.createNewUserRecord()

    user_list[str(chat_id)]['balance_data'].append(record_to_be_added)
    return user_list