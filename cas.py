import csv
import requests
import os
from xml.etree import ElementTree as ET

def check_api_availability(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_substance_info(cas_number):
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/synonyms/xml"
    try:
        response = requests.get(base_url.format(cas_number), timeout=5)
        #print(base_url.format(cas_number))  # Печатаем URL запроса
        
        if response.status_code == 200:
            # Обработка ответа
            data = response.text
            #print(data)  # Печатаем ответ API для проверки

            # Парсинг XML
            root = ET.fromstring(data)

            # Печатаем все элементы для отладки
            #for elem in root.iter():
            #    print(elem.tag, elem.text)

            # Извлечение синонимов с учетом пространства имён
            namespace = {'pug': 'http://pubchem.ncbi.nlm.nih.gov/pug_rest'}
            synonyms = [syn.text for syn in root.findall('.//pug:Synonym', namespace)]
            name = synonyms[0] if synonyms else "Not Found"
            return name, synonyms[:3]  # Возвращаем имя и первые 3 синонима
        else:
            return "Not Found", []
    except requests.exceptions.RequestException as e:
        return "API Error", []

def main():
    input_file = "cas.csv"
    output_file = "res_cas.csv"

    # Проверка наличия файла
    if not os.path.exists(input_file):
        print(f"Файл {input_file} не найден.")
        return

    # Проверка доступности API
    chk_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/7778-77-0/synonyms/xml"
    if not check_api_availability(chk_url):
        print("API недоступен. Попробуйте позже.")
        return

    # Множество для хранения уникальных CAS номеров
    processed_cas = set()

    # Подготовка для записи результата
    with open(output_file, mode='w', newline='', encoding='utf-8') as resultfile:
        csv_writer = csv.writer(resultfile)
        csv_writer.writerow(["cas", "name", "synonyms"])  # Запись заголовков

        # Чтение CAS номеров из файла
        with open(input_file, newline='', encoding='utf-8') as csvfile:
            cas_numbers = csv.reader(csvfile)

            for row in cas_numbers:
                cas = row[0].strip()
                if cas not in processed_cas:
                    # Добавляем CAS в множество
                    processed_cas.add(cas)
                    name, synonyms = get_substance_info(cas)
                    csv_writer.writerow([cas, name, ", ".join(synonyms)])  # Объединяем синонимы в строку
                    print(f"CAS: {cas}, Name: {name}, Synonyms: {', '.join(synonyms)}")  # Отладочная информация

if __name__ == "__main__":
    main()
