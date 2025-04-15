from telebot import types


def button_upload_excel():
    """Кнопка загрузки для excel файла."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text="Загрузить excel файл",
                                    callback_data="excel",
                                          request_document=True,
                                          file_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                          max_file_size=10 * 1024 * 1024)

    keyboard.add(button_1)
    return keyboard
