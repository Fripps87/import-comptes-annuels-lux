import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json
import os

DATASET_URL = "https://data.public.lu/fr/datasets/donnees-comptes-annuels/"

def get_xml_links():
    html = requests.get(DATASET_URL).text
    soup = BeautifulSoup(html, "html.parser")
    links = [
        a["href"] for a in soup.find_all("a", href=True)
        if a["href"].endswith(".xml")
    ]
    return links

def parse_xml(xml_content):
    root = ET.fromstring(xml_content)
    results = []

    for company in root.findall(".//company"):
        entry = {
            "name": company.findtext("name"),
            "year": company.findtext("year"),
            "nace": company.findtext("nace"),
            "balance_total": company.findtext("balance/total"),
        }
        results.append(entry)

    return results

def push_to_d365(data):
    url = os.environ["D365_URL"]
    token = os.environ["D365_TOKEN"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    for entry in data:
        requests.post(url, json=entry, headers=headers)

def main():
    links = get_xml_links()

    for link in links:
        xml_data = requests.get(link).content
        parsed = parse_xml(xml_data)
        push_to_d365(parsed)

if __name__ == "__main__":
    main()
