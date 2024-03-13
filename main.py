"""
Script para actualizar los datos de data/founders.csv desde el CRM

Requiere las variables de entorno API_URL y API_KEY para acceder al CRM

Ejecución:
    python main.py
"""
import os
import csv
import requests
from pathlib import Path


TAG_ID = "7698c2db-4593-429e-82e1-ef699c1c41d9" # WantBecomeFoundingMember
API_KEY = os.environ.get("API_KEY")
API_URL = os.environ.get("API_URL")
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "data" / "founders.csv"


def get_taggings_page(page: int) -> list:
    response = requests.get(
        f"{API_URL}tags/{TAG_ID}/taggings?page={page}",
        headers={
            "Content-Type": "application/json",
            "OSDI-API-Token": API_KEY,
        },
    )
    data = response.json()
    if data.get("error"):
        raise Exception(data["error"])
    return data["_embedded"]["osdi:taggings"]


def get_people_ids() -> list:
    print("Obteniendo taggings...")
    people = []
    page = 0
    while True:
        page += 1
        print(f"Página {page}")
        taggings = get_taggings_page(page)
        if len(taggings) == 0:
            break
        for item in taggings:
            if item.get("_links") is None or item["_links"].get("osdi:person") is None:
                continue
            person_id = item["_links"]["osdi:person"]["href"].split("/")[-1]
            people.append(person_id)
        break
    return people


def get_person_data(person_id: str) -> str:
    response = requests.get(
        f"{API_URL}people/{person_id}",
        headers={
            "Content-Type": "application/json",
            "OSDI-API-Token": API_KEY,
        },
    )
    data = response.json()
    if data.get("error"):
        raise Exception(data["error"])
    return data


def clean_name(name: str) -> str:
    return name.replace("  ", " ").strip()


def get_people_names(ids: list) -> list:
    names = []
    for i, person_id in enumerate(ids):
        print(f"Nombre {i+1}/{len(ids)}")
        data = get_person_data(person_id)
        names.append([
            clean_name(data.get("given_name", "")),
            clean_name(data.get("family_name", "")),
        ])
    return names


def save_names_to_csv(people: list):
    with open(OUTPUT_FILE, "w") as file:
        writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["firstname", "lastname"])
        for person in people:
            writer.writerow(person)


def main():
    people_ids = get_people_ids()
    people_names = get_people_names(people_ids)
    save_names_to_csv(people_names)
    print(f"File saved to {OUTPUT_FILE}")



if __name__ == "__main__":
    if API_URL is None:
        raise Exception("Variable de entorno API_URL no definida.")

    if API_KEY is None:
        raise Exception("Variable de entorno API_KEY no definida.")
    main()
