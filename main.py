import requests
import os
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_predict_rub_salary(payment_to=None, payment_from=None):
    if payment_from and payment_to:
        return int((payment_from + payment_to) / 2)
    elif payment_from:
        return int(payment_from * 1.2)
    elif payment_to:
        return int(payment_to * 0.8)
    else:
        return None


def make_table(statistic, title):
    table_data = [
        ["Язык программирования", "Найдено вакансий", "Обработано вакансий", "Средняя зарплата"],
    ]
    for language, vacancies in statistic.items():
        table_data.append([language, vacancies['vacancies_found'], vacancies['vacancies_processed'], vacancies['middle_salary']])
    table = AsciiTable(table_data, title+" Moscow")
    return table.table


def get_statistic_sj(superjob_token, languages_sj):
    vacancies_statistic_sj = {}
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
            vacancies = response.json()
            vacancies_found_sj = vacancies["total"]
            if not vacancies["objects"]:
                break
            for vacancies_sj in vacancies["objects"]:
                predicted_salary_sj = get_predict_rub_salary(vacancies_sj.get('payment_from'), vacancies_sj.get('payment_to'))
                if predicted_salary_sj:
                    salaries_sj.append(predicted_salary_sj)
        if salaries_sj:
            middle_salary_sj = int(sum(salaries_sj)/len(salaries_sj))
        else:
            middle_salary_sj = None
        vacancies_statistic_sj[language_sj] = {
            "vacancies_found": vacancies_found_sj,
            "vacancies_processed": len(salaries_sj),
            "middle_salary": middle_salary_sj
        }
    return vacancies_statistic_sj


def get_statistic_hh(languages_hh):
    vacancies_statistic_hh = {}
    area = 1
    period = 30
    for language_hh in languages_hh:
        salaries = []
        for page in count(0):
            params = {
                "area": area,
                "period": period,
                "text": language_hh,
                "page": page
            }
            response = requests.get('https://api.hh.ru/vacancies', params=params)
            response.raise_for_status()
            vacancies = response.json()
            if page >= response.json()["pages"]:
                break
            vacancies_found_hh = vacancies["found"]
            for salary_inf in vacancies["items"]:
                salary = salary_inf["salary"]
                if salary and salary['currency'] == 'RUR':
                    predicted_salary_hh = get_predict_rub_salary(salary_inf['salary'].get('from'), salary_inf['salary'].get('to'))
                    if predicted_salary_hh:
                        salaries.append(predicted_salary_hh)
        if salaries:
            middle_salary_hh = int(sum(salaries) / len(salaries))
        else:
            middle_salary_hh = None
        vacancies_statistic_hh[language_hh] = {
            "vacancies_found": vacancies_found_hh,
            "vacancies_processed": len(salaries),
            "middle_salary": middle_salary_hh
        }
    return vacancies_statistic_hh


def main():
    load_dotenv()
    superjob_token = os.getenv("SJ_TOKEN")
    languages_sj = ["Python", "JavaScript", "Java"]
    languages_hh = ["Shell", "Swift", "Scala"]
    print(make_table(get_statistic_sj(superjob_token, languages_sj), "SuperJob"))
    print(make_table(get_statistic_hh(languages_hh), "HeadHunter"))


if __name__ == '__main__':
    main()
