import csv
from config import BASE_DIR

metadata_path = BASE_DIR / "dumps" / "fedstatru" / "fedstatru" / "data" / "metdata.csv"

with open(metadata_path, mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Пропускаем строку-заголовок, если она есть
    
    # row[1] — это данные из второго столбца
    code_name = {row[0]:row[1] for row in reader}
    # my_list = [row[1] for row in reader]
code_name