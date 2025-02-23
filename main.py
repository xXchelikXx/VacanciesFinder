import requests
import os
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_rub_salary_hh(salary):
    if salary:
        if salary['currency'] == 'RUR':
            if salary['from'] and salary['to']:
                return int((salary['from'] + salary['to']) / 2)
            elif salary['from']:
                return int(salary['from'] * 1.2)
            elif salary['to']:
                return int(salary['to'] * 0.8)
            else:
                return None
        else:
            return None


def predict_rub_salary_sj(vacancies_sj):
    if vacancies_sj:
        if vacancies_sj['currency'] == 'rub':
            if vacancies_sj['payment_from'] and vacancies_sj['payment_to']:
                return int((vacancies_sj['payment_from'] + vacancies_sj['payment_to']) / 2)
            elif vacancies_sj['payment_from']:
                return int(vacancies_sj['payment_from'] * 1.2)
            elif vacancies_sj['payment_to']:
                return int(vacancies_sj['payment_to'] * 0.8)
            else:
                return None
        else:
            return None


def table(statistic, title):
    table_data = [
        ["Язык программирования", "Найдено вакансий", "Обработано вакансий", "Средняя зарплата"],
    ]
    for language, vacancies in statistic.items():
        table_data.append([language, vacancies['vacancies_found'], vacancies['vacancies_processed'], vacancies['middle_salary']])
    table = AsciiTable(table_data, title+" Moscow")
    return table.table


def statistic_sj(superjob_token):
    languages_sj = ["C++", "JavaScript", "Java"]
    vacancies_sj_json = {}
    for language_sj in languages_sj:
        salaries_sj = []
        for page in count(0):
            params = {
                "keyword": language_sj,
                "town": "Москва",
                "page": page
            }
            headers = {
                "X-Api-App-Id": superjob_token
            }
            response = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=headers, params=params)
            response.raise_for_status()
            vacancies_found_sj = response.json()["total"]
            if not response.json()["objects"]:
                break
            for vacancies_sj in response.json()["objects"]:
                predicted_salary_sj = predict_rub_salary_sj(vacancies_sj)
                if predicted_salary_sj:
                    salaries_sj.append(predicted_salary_sj)
        if salaries_sj:
            middle_salary_sj = int(sum(salaries_sj)/len(salaries_sj))
        else:
            middle_salary_sj = None
        vacancies_sj_json[language_sj] = {
            "vacancies_found": vacancies_found_sj,
            "vacancies_processed": len(salaries_sj),
            "middle_salary": middle_salary_sj
        }
    return vacancies_sj_json


def statistic_hh():
    languages_hh = ["Shell", "Swift", "Scala"]
    vacancies_hh_json = {}
    for language_hh in languages_hh:
        salaries = []
        for page in count(0):
            params = {
                "area": 1,
                "period": 30,
                "text": language_hh,
                "page": page
            }
            response = requests.get('https://api.hh.ru/vacancies', params=params)
            response.raise_for_status()
            if page >= response.json()["pages"]:
                break
            vacancies_found_hh = response.json()["found"]
            for items in response.json()["items"]:
                salary = items["salary"]
                predicted_salary_hh = predict_rub_salary_hh(salary)
                if predicted_salary_hh:
                    salaries.append(predicted_salary_hh)
        if salaries:
            middle_salary_hh = int(sum(salaries) / len(salaries))
        else:
            middle_salary_hh = None
        vacancies_hh_json[language_hh] = {
            "vacancies_found": vacancies_found_hh,
            "vacancies_processed": len(salaries),
            "middle_salary": middle_salary_hh
        }
    return vacancies_hh_json


def main():
    load_dotenv()
    superjob_token = os.getenv("SJ_TOKEN")
    print(table(statistic_sj(superjob_token), "SuperJob"))
    print(table(statistic_hh(), "HeadHunter"))


if __name__ == '__main__':
    main()
