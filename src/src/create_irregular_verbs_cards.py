import sqlite3
import os
from operator import index

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

TEXT_HEX                        = int(os.getenv("VERB_TEXT_COLOR", "0xFFFFFF"), 16)
T_R, T_G, T_B                   = ((TEXT_HEX >> 16) & 0xFF), ((TEXT_HEX >> 8) & 0xFF), (TEXT_HEX & 0xFF)
LAST_WORD_HEX                   = int(os.getenv("VERB_TRANSLATION_COLOR", "0xFF0000"), 16)
LW_R, LW_G, LW_B                = ((LAST_WORD_HEX >> 16) & 0xFF), ((LAST_WORD_HEX >> 8) & 0xFF), (LAST_WORD_HEX & 0xFF)
FONT                            = os.getenv("FONT", "arial.ttf")

CARTS_WIDTH                     = int(os.getenv("CARTS_WIDTH", 800))
CARTS_HEIGHT                    = int(os.getenv("CARTS_HEIGHT", 450))
CARTS_TEXT_SIZE                 = int(os.getenv("CARTS_TEXT_SIZE", 40))
CARTS_BACKGROUND_HEX            = int(os.getenv("CARTS_BACKGROUND_COLOR", "0x000000ff"), 16)
CB_R, CB_G, CB_B, C_ALPHA_CANAL = ((CARTS_BACKGROUND_HEX >> 24) & 0xFF),((CARTS_BACKGROUND_HEX>> 16) & 0xFF), ((CARTS_BACKGROUND_HEX >> 8) & 0xFF), (CARTS_BACKGROUND_HEX & 0xFF)

TABLE_WIDTH                     = int(os.getenv("TABLE_WIDTH", 1600))
TABLE_HEIGHT                    = int(os.getenv("TABLE_HEIGHT", 900))
TABLE_BACKGROUND_COLOR          = int(os.getenv("TABLE_BACKGROUND_COLOR", "0x000000ff"), 16)
TB_R, TB_G, TB_B, T_ALPHA_CANAL = ((TABLE_BACKGROUND_COLOR >> 24) & 0xFF), ((TABLE_BACKGROUND_COLOR >> 16) & 0xFF), ((TABLE_BACKGROUND_COLOR >> 8) & 0xFF), (TABLE_BACKGROUND_COLOR & 0xFF)
TABLE_HEADER_TEXT_COLOR         = int(os.getenv("TABLE_HEADER_TEXT_COLOR", "0xFF0000"), 16)
TH_R, TH_G, TH_B                = ((TABLE_HEADER_TEXT_COLOR >> 16) & 0xFF), ((TABLE_HEADER_TEXT_COLOR >> 8) & 0xFF), (TABLE_HEADER_TEXT_COLOR & 0xFF)
TABLE_HEADER_TEXT_SIZE          = int(os.getenv("TABLE_HEADER_TEXT_SIZE", 30))
TABLE_TEXT_SIZE                 = int(os.getenv("TABLE_TEXT_SIZE", 20))

ROW                             = int(os.getenv("VERB_ON_PAGE", 15))

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
    background_color = (CB_R, CB_G, CB_B, C_ALPHA_CANAL)
    text_color = (T_R, T_G, T_B)
    last_word_color = (LW_R, LW_G, LW_B)

    if not os.path.exists(PATH_TO_CRD):
        os.makedirs(PATH_TO_CRD)

    try:
        background = Image.open(os.path.join(PATH_TO_IMG, file)).convert("RGBA")
    except IOError:
        raise ValueError(f"Фоновое изображение не найдено по пути {PATH_TO_IMG}")

    verbs = get_array_irregular_verbs()

    for verb in verbs:
        img  = Image.new("RGBA", (CARTS_WIDTH, CARTS_HEIGHT), background_color)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT, CARTS_TEXT_SIZE)
        except IOError:
            font = ImageFont.load_default()

        padding = 25
        x_start = CARTS_WIDTH // 2
        y_start = 0
        offset_y = (CARTS_HEIGHT - 50) // 4

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

def create_irregular_verbs_table():
    background_color  = (TB_R, TB_G, TB_B, T_ALPHA_CANAL)
    text_color        = (0, 0, 0)
    last_word_color   = (LW_R, LW_G, LW_B)
    grid_color        = (100, 100, 100)

    header_text_color = (TH_R, TH_G, TH_B)

    verbs = get_array_irregular_verbs()

    cols  = 4
    rows  = ROW + 1

    cell_width  = TABLE_WIDTH // 4
    cell_height = TABLE_HEIGHT // rows

    indx = 1
    for i in range(0, len(verbs), rows - 1):
        img  = Image.new("RGB", (TABLE_WIDTH, TABLE_HEIGHT), background_color)
        draw = ImageDraw.Draw(img)

        try:
            text_font   = ImageFont.truetype(FONT, TABLE_TEXT_SIZE)
            header_font = ImageFont.truetype(FONT, TABLE_HEADER_TEXT_SIZE)
        except IOError:
            text_font   = ImageFont.load_default()
            header_font = ImageFont.load_default()

        for row in range(rows + 1):
            y = row * cell_height
            draw.line([(0, y), (TABLE_WIDTH, y)], fill=grid_color, width=2)

        for col in range(cols + 1):
            x = col * cell_width
            draw.line([(x, 0), (x, TABLE_HEIGHT)], fill=grid_color, width=2)

        header = ["Present Simple", "Past Simple", "Past Participle", "Translation"]

        offset_y = 0
        for j in range(0, len(header)):
            word = header[j]
            x = 20 + j * cell_width
            y = 20 + offset_y
            draw.text((x, y), word, font=header_font, fill=header_text_color)

        offset_y += cell_height
        for j in range(i, i + rows):
            if j == len(verbs):
                break
            offset_x = 0
            for k in range(1, cols + 1):
                text = verbs[j][k].capitalize()
                x = 20 + offset_x
                y = 20 + offset_y
                if k == cols:
                    draw.text((x, y), text, font=text_font, fill=last_word_color)
                else:
                    draw.text((x, y), text, font=text_font, fill=text_color)
                offset_x += cell_width
            offset_y += cell_height

        file_path = os.path.join(PATH_TO_CRD, f"table_{indx}.png")
        img.save(file_path)
        indx += 1
        print(f"Изображение таблицы сохранено в {file_path}\n")

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

    ans = input("Вам нужно создавать таблицу? (Y/N): ")
    if ans == "Y" or ans == "y":
        create_irregular_verbs_table()
        print("Таблица с неправильными глаголами была создана!\n\n")

    print("Завершение работы: 'create_irregular_verbs_cards.py'\n")
    print("------------------------------------------------\n")

if __name__ == "__main__":
    main()