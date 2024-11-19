import requests
from bs4 import BeautifulSoup
import csv
import json
import re

# URL del sito delle carte
url = 'https://pocket.limitlesstcg.com/cards/A1?display=compact'

# Realizziamo la richiesta HTTP per ottenere il contenuto della pagina
response = requests.get(url)
html_content = response.text

# Analizziamo l'HTML con BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Troviamo tutte le carte nella pagina
cards = soup.find_all('div', class_='card-classic')

# Lista per memorizzare i dati delle carte
card_data = []

# Estrarre i dettagli di ogni carta
for card in cards:
    card_info = {}

    # Nome della carta
    name_section = card.find('span', class_='card-text-name')
    if name_section:
        card_info['name'] = name_section.text.strip()

    # Tipo e HP della carta
    type_hp_section = card.find('p', class_='card-text-title')
    if type_hp_section:
        type_hp_text = type_hp_section.text.strip()
        # Estrarre il tipo e HP (esempio: "Grass - 70 HP")
        type_hp = type_hp_text.split(' - ')
        if len(type_hp) > 0:
            card_info['type'] = type_hp[0].strip()  # Tipo di carta (esempio: "Grass")
        else:
            card_info['type'] = 'N/A'
        if len(type_hp) > 1:
            card_info['hp'] = type_hp[1].strip()  # HP (esempio: "70 HP")
        else:
            card_info['hp'] = 'N/A'

    # Tipo di carta
    card_type_section = card.find('p', class_='card-text-type')
    if card_type_section:
        card_info['card_type'] = card_type_section.text.strip()

    # Dizionario di mappatura per le lettere e le tipologie
    type_mapping = {
        'G': 'Grass',
        'R': 'Fire',
        'W': 'Water',
        'L': 'Lightning',
        'P': 'Psychic',
        'F': 'Fighting',
        'D': 'Darkness',
        'M': 'Metal',
        'Y': 'Fairy',
        'C': 'Colorless'
    }

    # Attacchi della carta
    attack_section = card.find_all('div', class_='card-text-attack')
    attacks = []
    card_info['attacks'] = attacks

    for attack in attack_section:
        attack_info_section = attack.find('p', class_='card-text-attack-info')
        if attack_info_section:
            # Estrarre il costo dell'attacco
            cost_elements = attack_info_section.find('span', class_='ptcg-symbol')
            attack_cost = [type_mapping.get(symbol, 'Unknown') for symbol in cost_elements.text.strip()] if cost_elements else []
            attack_text = attack_info_section.text.replace(cost_elements.text, '').strip() if cost_elements else attack_info_section.text.strip()
            attack_parts = attack_text.split(' ')
            attack_name = ' '.join(attack_parts[:-1]) if len(attack_parts) > 1 else 'Unknown'
            attack_damage = attack_parts[-1] if len(attack_parts) > 1 else '0'
            attacks.append({'name': attack_name, 'cost': attack_cost, 'damage': attack_damage})
        else:
            card_info['attacks'] = []  # Se non ha attacchi, assegniamo una lista vuota

    # Debolezza e costo di ritirata
    weakness_retreat_section = card.find('p', class_='card-text-wrr')
    if weakness_retreat_section:
        text = weakness_retreat_section.text.strip().split('\n')
        card_info['weakness'] = text[0].split(': ')[1] if len(text) > 0 and ': ' in text[0] else 'N/A'
        card_info['retreat'] = text[1].split(': ')[1] if len(text) > 1 and ': ' in text[1] else 'N/A'

    # Estrarre l'URL dell'immagine
    image_section = card.find('img', class_='card shadow max-xs')
    if image_section and 'src' in image_section.attrs:
        card_info['image_url'] = image_section.attrs['src']

    # Aggiungere i dati estratti alla lista
    card_data.append(card_info)

# Salvare i risultati in un file CSV
csv_filename = 'pokemon_cards.csv'
csv_fields = ['name', 'type', 'hp', 'card_type', 'attacks', 'weakness', 'retreat', 'image_url']

with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
    writer.writeheader()
    for card in card_data:
        # Convertire gli attacchi in una stringa per scrivere nel CSV
        card['attacks'] = ', '.join([f"{attack['name']} {attack['damage']}" for attack in card['attacks']]) if card['attacks'] else 'N/A'
        writer.writerow(card)

# Salvare i risultati in un file JSON
json_filename = 'pokemon_cards.json'
with open(json_filename, mode='w', encoding='utf-8') as jsonfile:
    json.dump(card_data, jsonfile, indent=4, ensure_ascii=False)

# Mostrare i risultati sulla console
for card in card_data:
    print(f"Name: {card['name']}")
    print(f"Type: {card.get('type', 'N/A')}")
    print(f"HP: {card.get('hp', 'N/A')}")
    print(f"Card Type: {card.get('card_type', 'N/A')}")
    print(f"Image URL: {card.get('image_url', 'N/A')}")
    print(f"Weakness: {card.get('weakness', 'N/A')}")
    print(f"Retreat Cost: {card.get('retreat', 'N/A')}")
    
    # Controlliamo se la carta ha attacchi prima di tentare di stamparli
    if card['attacks']:
        print(f"Attacks: {card['attacks']}")
    else:
        print("Attacks: N/A")
    
    print('-' * 40)
