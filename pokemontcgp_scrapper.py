import requests
from bs4 import BeautifulSoup
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

# Funzione per mappare i simboli al tipo, con separazione per le stringhe più lunghe
def map_attack_cost(cost_elements):
    cost_list = []  # Lista per contenere i tipi di energia
    
    for cost in cost_elements:
        cost_symbol = cost.text.strip()  # Estrae il simbolo di energia
        
        # Se il simbolo è composto da più lettere, lo separiamo
        if len(cost_symbol) > 1:
            for letter in cost_symbol:
                cost_type = type_mapping.get(letter, 'Unknown')
                if cost_type == 'Unknown':
                    print(f"Attenzione: simbolo non riconosciuto '{letter}'.")
                cost_list.append(cost_type)
        else:
            # Caso in cui il simbolo è una singola lettera
            cost_type = type_mapping.get(cost_symbol, 'Unknown')
            if cost_type == 'Unknown':
                print(f"Attenzione: simbolo non riconosciuto '{cost_symbol}'.")
            cost_list.append(cost_type)

    # Restituire la lista di costi
    return cost_list if cost_list else ['No Cost']


# Estrarre i dettagli di ogni carta
for card in cards:
    card_info = {}

    # ID della carta
    card_set_info_section = card.find('div', class_='card-set-info')
    if card_set_info_section:
        card_info['card_id'] = card_set_info_section.text.strip().replace(' ', '')
    else:
        card_info['card_id'] = 'UnknownID'


    # Nome della carta
    name_section = card.find('span', class_='card-text-name')
    card_info['name'] = name_section.text.strip() if name_section else 'Unknown'

    # Tipo e HP della carta
    type_hp_section = card.find('p', class_='card-text-title')
    if type_hp_section:
        # Rimuovere il nome della carta e dividere il resto
        content = type_hp_section.text.replace(card_info['name'], '').strip()
        # Rimuovere i trattini extra e dividere per i rimanenti
        parts = [part.strip() for part in content.split('-') if part.strip()]

        if len(parts) >= 2:
            card_info['type'] = parts[0]  # Tipo (esempio: "Grass")
            # Estrazione solo del valore numerico dell'HP
            card_info['hp'] = re.sub(r'\D', '', parts[1])  # Rimuove tutto tranne i numeri
        else:
            card_info['type'] = 'N/A'
            card_info['hp'] = 'N/A'


    # Tipo di carta
    card_type_section = card.find('p', class_='card-text-type')
    stages = ['Basic', 'Stage 1', 'Stage 2']
    card_info['card_type'] = next((stage for stage in stages if stage in card_type_section.text), 'Unknown') if card_type_section else 'Unknown'

    # Attacchi della carta
    attack_section = card.find_all('div', class_='card-text-attack')
    attacks = []
    for attack in attack_section:
        attack_info_section = attack.find('p', class_='card-text-attack-info')
        attack_effect_section = attack.find('p', class_='card-text-attack-effect')

        if attack_info_section:
            cost_elements = attack_info_section.find_all('span', class_='ptcg-symbol')
            attack_cost = map_attack_cost(cost_elements)  # Usa la funzione migliorata

            attack_text = attack_info_section.text.strip()
            for cost_element in cost_elements:
                attack_text = attack_text.replace(cost_element.text, '').strip()

            attack_parts = attack_text.rsplit(' ', 1)
            attack_name = attack_parts[0].strip() if len(attack_parts) > 1 else 'Unknown'
            attack_damage = attack_parts[1].strip() if len(attack_parts) > 1 else '0'

            attack_effect = attack_effect_section.text.strip() if attack_effect_section else 'No effect'

            attacks.append({
                'cost': attack_cost,
                'name': attack_name,
                'damage': attack_damage,
                'effect': attack_effect
            })
    card_info['attacks'] = attacks

    # Abilità della carta
    ability_section = card.find('div', class_='card-text-ability')
    if ability_section:
        ability_name_section = ability_section.find('p', class_='card-text-ability-info')
        ability_effect_section = ability_section.find('p', class_='card-text-ability-effect')
        ability_name = ability_name_section.text.replace('Ability:', '').strip() if ability_name_section else 'Unknown'
        ability_effect = ability_effect_section.text if ability_effect_section else 'No effect'
        ability_effect_cleaned = re.sub(r'\[.*?\]', '', ability_effect).strip()

        card_info['ability'] = {
            'name': ability_name,
            'effect': ability_effect_cleaned
        }
    else:
        card_info['ability'] = {'name': 'No ability', 'effect': 'N/A'}

    # Debolezza e costo di ritirata
    weakness_retreat_section = card.find('p', class_='card-text-wrr')
    if weakness_retreat_section:
        text = weakness_retreat_section.text.strip().split('\n')
        card_info['weakness'] = text[0].split(': ')[1] if len(text) > 0 and ': ' in text[0] else 'N/A'
        card_info['retreat'] = text[1].split(': ')[1] if len(text) > 1 and ': ' in text[1] else 'N/A'

    # URL dell'immagine
    image_section = card.find('img', class_='card shadow max-xs')
    card_info['image_url'] = image_section.attrs['src'] if image_section and 'src' in image_section.attrs else 'N/A'

    # Aggiungere i dati estratti alla lista
    card_data.append(card_info)

# Salvare i risultati in formato JSON
json_filename = 'pokemon_cards.json'
with open(json_filename, mode='w', encoding='utf-8') as jsonfile:
    json.dump(card_data, jsonfile, indent=4, ensure_ascii=False)

# Output per conferma
print(json.dumps(card_data, indent=4, ensure_ascii=False))


# Mostrare i risultati sulla console
for card in card_data:
    print(f"Card ID: {card['card_id']}")
    print(f"Name: {card['name']}")
    print(f"Type: {card.get('type', 'N/A')}")
    print(f"HP: {card.get('hp', 'N/A')}")
    print(f"Card Type: {card.get('card_type', 'N/A')}")
    #print(f"Image URL: {card.get('image_url', 'N/A')}")
    print(f"Weakness: {card.get('weakness', 'N/A')}")
    print(f"Retreat Cost: {card.get('retreat', 'N/A')}")
    
    # Controlliamo se la carta ha attacchi prima di tentare di stamparli
    if card['attacks']:
        #print(f"costo attacco: {attack_cost}")
        print(f"Attacks: {card['attacks']}")
    else:
        print("Attacks: N/A")
    
    print('-' * 40)
