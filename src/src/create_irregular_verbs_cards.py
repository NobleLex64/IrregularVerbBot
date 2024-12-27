import sqlite3
import os
from PIL    import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Параметры из .env
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    raise ValueError("Путь к базе данных не найден! Убедитесь, что файл .env существует и содержит DB_PATH.")

PATH_TO_CRD = os.getenv("IRREGULAR_VERB_CARDS_PATH")
if not PATH_TO_CRD:
    raise ValueError("Путь к карточкам не найден! Убедитесь, что файл .env существует и содержит IRREGULAR_VERB_CARDS_PATH.")

PATH_TO_IMG = os.getenv("BACKGROUND_IMG_PATH")
if not PATH_TO_IMG:
    raise ValueError("Путь к картинке на заднем фоне не найден! Убедитесь, что файл .env существует и содержит BACKGROUND_IMG_PATH.")

IMG_WIDTH        = int(os.getenv("WIDTH", 800))
IMG_HEIGHT       = int(os.getenv("HEIGHT", 450))

BACKGROUND_HEX   = int(os.getenv("HEX_BACKGROUND_RGB", "0x000000"), 16)
B_R, B_G, B_B    = ((BACKGROUND_HEX >> 16) & 0xFF), ((BACKGROUND_HEX >> 8) & 0xFF), (BACKGROUND_HEX & 0xFF)
ALPHA_CANAL      = int(os.getenv("ALPHA", 150))

TEXT_HEX         = int(os.getenv("HEX_TEXT_RGB", "0xFFFFFF"), 16)
T_R, T_G, T_B    = ((TEXT_HEX >> 16) & 0xFF), ((TEXT_HEX >> 8) & 0xFF), (TEXT_HEX & 0xFF)

LAST_WORD_HEX    = int(os.getenv("HEX_LAST_WORD_RGB", "0xFF0000"), 16)
LW_R, LW_G, LW_B = ((LAST_WORD_HEX >> 16) & 0xFF), ((LAST_WORD_HEX >> 8) & 0xFF), (LAST_WORD_HEX & 0xFF)

FONT             = os.getenv("FONT", "arial.ttf")
TEXT_SIZE        = int(os.getenv("TEXT_SIZE", 90))

# Функция для получения неправильных глаголов из базы данных
def get_array_irregular_verbs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM verbs")
        verbs = cursor.fetchall()
    finally:
        conn.close()  # Закрытие подключения к БД
    return verbs

# Удаляем все карточки в папке py_bot/data/irregular_verbs_cards/
def delete_cards():
    for file_name in os.listdir(PATH_TO_CRD):
        file_path = os.path.join(PATH_TO_CRD, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Функция для создания карточек
def create_cards(file):
    background_color = (B_R, B_G, B_B, ALPHA_CANAL)
    text_color = (T_R, T_G, T_B)
    last_word_color = (LW_R, LW_G, LW_B)

    # Проверка пути сохранения карточек
    if not os.path.exists(PATH_TO_CRD):
        os.makedirs(PATH_TO_CRD)

    # Загрузка фона
    try:
        background = Image.open(os.path.join(PATH_TO_IMG, file)).convert("RGBA")
    except IOError:
        raise ValueError(f"Фоновое изображение не найдено по пути {PATH_TO_IMG}")

    verbs = get_array_irregular_verbs()
    for verb in verbs:
        img  = Image.new("RGBA", (IMG_WIDTH, IMG_HEIGHT), background_color)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT, TEXT_SIZE)
        except IOError:
            font = ImageFont.load_default()

        padding = 25
        x_start = IMG_WIDTH // 2
        y_start = 0
        offset_y = (IMG_HEIGHT - 50) // 4

        indx = verb[0]
        for i in range(1, len(verb)):
            text = verb[i].capitalize()
            y_line = (y_start + ((i - 1) * offset_y)) + padding
            x_line = x_start - (len(verb[i]) // 2) * 18
            if i == (len(verb) - 1):
                draw.text((x_line, y_line), text, font=font, fill=last_word_color)
            else:
                draw.text((x_line, y_line), text, font=font, fill=text_color)

        # Сохранение изображения
        combined = Image.alpha_composite(background, img)
        file_path = os.path.join(PATH_TO_CRD, f"{indx}.png")
        combined.save(file_path, "PNG")

def main():
    print("\n------------------------------------------------\n")
    print("Начало работы: 'create_irregular_verbs_cards.py'\n\n")

    ans = input("Вам нужно удалить существующие карточки? (Y/N): ")
    if ans == "Y" or ans == "y":
        delete_cards()
        print("Карточки с неправильными глаголами были удаленны!\n\n")

    files = os.listdir(PATH_TO_IMG)
    if not files:
        raise ValueError(f"В папке {PATH_TO_IMG} не найдено изображений для фона.")

    ans = input("Вам нужно создавать карточки? (Y/N): ")
    if ans == "Y" or ans == "y":
        create_cards(files[0])
        print("Карточки с неправильными глаголами были созданны!\n\n")

    print("Завершение работы: 'create_irregular_verbs_cards.py'\n")
    print("------------------------------------------------\n")

if __name__ == "__main__":
    main()