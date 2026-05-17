import requests
from bs4 import BeautifulSoup
import re
import json 

def scrape_problems_and_answers(page_url, start_problem_num):
    try:
        response = requests.get(page_url)
        response.raise_for_status()  # исключения для ошибок
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL {page_url}: {e}")
        return [], 0

    soup = BeautifulSoup(response.text, 'html.parser')
    problems_data_on_page = []

    problem_containers = soup.find_all('div', class_='prob_view')

    if not problem_containers:
        print(f"No problem containers found on {page_url}. Please check the class name.")
        return [], 0

    current_problem_num = start_problem_num
    for problem_container in problem_containers:
        problem_text = "N/A"
        answer_text = "N/A"

        # получаем все содержимое
        full_content = problem_container.get_text(separator=' ', strip=True)
        # убираем лишнее
        full_content = full_content.replace('\xad', '').replace('\u202f', ' ').strip()

        # конец текста задания (на 'Ответ:' или 'Пояснение')
        answer_keyword_index = full_content.find("Ответ:")
        explanation_start_match = re.search(r'Пояснение[\s.:]', full_content)
        explanation_index = explanation_start_match.start() if explanation_start_match else -1

        end_of_problem_text_index = len(full_content) 

        if answer_keyword_index != -1 and explanation_index != -1:
            end_of_problem_text_index = min(answer_keyword_index, explanation_index)
        elif answer_keyword_index != -1:
            end_of_problem_text_index = answer_keyword_index
        elif explanation_index != -1:
            end_of_problem_text_index = explanation_index

        # начало с 'Укажите варианты ответов'
        start_problem_text_marker = "Укажите варианты ответов"
        problem_start_index = full_content.find(start_problem_text_marker)

        if problem_start_index != -1:
            problem_text = full_content[problem_start_index:end_of_problem_text_index].strip()
        else:
            # если маркера нет
            problem_text = full_content[:end_of_problem_text_index].strip()

        if not problem_text: # если нет текста задания
            problem_text = "N/A"

        # ответ начиная с 'Ответ:' в формате 'Ответ: [digits]'
        answer_match = re.search(r'Ответ:\s*(\d+)[.|]?', full_content, re.IGNORECASE)
        if answer_match:
            answer_value = answer_match.group(1).strip()
            answer_text = f"Ответ: {answer_value}"
        else:
            answer_text = "Ответ не найден."

        # Post-process problem_text to add newlines for numbered options
        if problem_text != "N/A":
            # чиним пробелы
            problem_text = re.sub(r'\s*(\d+\)\s*)', r'###OPTION_START###\1', problem_text)
            # отступы (абзацы)
            problem_text = problem_text.replace('###OPTION_START###1)', '\n\n1)', 1)
            problem_text = problem_text.replace('###OPTION_START###', '\n')
            problem_text = re.sub(r'\n{3,}', '\n\n', problem_text)
            # опять пробелы
            problem_text = problem_text.strip()

        problem_text = problem_text.replace('\xad', '').replace('\u202f', ' ').replace('...', '..').strip()
        answer_text = answer_text.replace('\xad', '').replace('\u202f', ' ').strip()

        # добавляем только если есть задание и ответ
        if problem_text != "N/A" and answer_text != "Ответ не найден.":
            problems_data_on_page.append({
                'problem_number': current_problem_num,
                'problem_text': problem_text,
                'answer': answer_text
            })
            current_problem_num += 1
        else:
            print(f"DEBUG: Skipping problem {current_problem_num} due to extraction issues. Page: {page_url}. Problem Text: '{problem_text}' (Length: {len(problem_text)}). Answer Text: '{answer_text}' (Length: {len(answer_text) if answer_text else 0}).")
            current_problem_num += 1 

    return problems_data_on_page, current_problem_num

ege_tasks_1_data = [] # для хранения обработанных данных
global_next_problem_num = 1

url1 = "https://rus-ege.sdamgia.ru/test?category_id=380&filter=all"
print(f"Scraping from: {url1}")
for page_num in range(1, 3): 
    page_url = f"{url1}&page={page_num}" if page_num > 1 else url1
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url2 = "https://rus-ege.sdamgia.ru/test?category_id=358&filter=all"
print(f"\nScraping from: {url2}")
for page_num in range(1, 10): 
    page_url = f"{url2}&page={page_num}" if page_num > 1 else url2
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url3 = "https://rus-ege.sdamgia.ru/test?category_id=259&filter=all"
print(f"\nScraping from: {url3}")
for page_num in range(1, 18):
    page_url = f"{url3}&page={page_num}" if page_num > 1 else url3
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url4 = "https://rus-ege.sdamgia.ru/test?category_id=381&filter=all"
print(f"\nScraping from: {url4}")
for page_num in range(1, 5):
    page_url = f"{url4}&page={page_num}" if page_num > 1 else url4
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url5 = "https://rus-ege.sdamgia.ru/test?category_id=344&filter=all"
print(f"\nScraping from: {url5}")
for page_num in range(1, 6):
    page_url = f"{url5}&page={page_num}" if page_num > 1 else url5
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url6 = "https://rus-ege.sdamgia.ru/test?category_id=348&filter=all"
print(f"\nScraping from: {url6}")
for page_num in range(1, 20):
    page_url = f"{url6}&page={page_num}" if page_num > 1 else url6
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url7 = "https://rus-ege.sdamgia.ru/test?category_id=382&filter=all"
print(f"\nScraping from: {url7}")
for page_num in range(1, 5):
    page_url = f"{url7}&page={page_num}" if page_num > 1 else url7
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url8 = "https://rus-ege.sdamgia.ru/test?category_id=343&filter=all"
print(f"\nScraping from: {url8}")
for page_num in range(1, 5):
    page_url = f"{url8}&page={page_num}" if page_num > 1 else url8
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url9 = "https://rus-ege.sdamgia.ru/test?category_id=351&filter=all"
print(f"\nScraping from: {url9}")
for page_num in range(1, 21): 
    page_url = f"{url9}&page={page_num}" if page_num > 1 else url9
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url10 = "https://rus-ege.sdamgia.ru/test?category_id=383&filter=all"
print(f"\nScraping from: {url10}")
for page_num in range(1, 4):
    page_url = f"{url10}&page={page_num}" if page_num > 1 else url10
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url11 = "https://rus-ege.sdamgia.ru/test?category_id=346&filter=all"
print(f"\nScraping from: {url11}")
for page_num in range(1, 6):
    page_url = f"{url11}&page={page_num}" if page_num > 1 else url11
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

url12 = "https://rus-ege.sdamgia.ru/test?category_id=350&filter=all"
print(f"\nScraping from: {url12}")
for page_num in range(1, 21):
    page_url = f"{url12}&page={page_num}" if page_num > 1 else url12
    page_problems, global_next_problem_num = scrape_problems_and_answers(page_url, global_next_problem_num)
    ege_tasks_1_data.extend(page_problems)

# сохраняем
if ege_tasks_1_data:
    with open("ege_tasks_1.json", "w", encoding="utf-8") as f:
        json.dump(ege_tasks_1_data, f, ensure_ascii=False, indent=4)
    print(f"Successfully scraped {len(ege_tasks_1_data)} problems and saved to ege_tasks_1.json")
else:
    print("Ничего не нашлось.")
