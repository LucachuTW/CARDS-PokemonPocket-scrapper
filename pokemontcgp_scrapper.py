import requests
from bs4 import BeautifulSoup
import re
import json
import time

BASE_URL = 'https://pocket.limitlesstcg.com/cards/'

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

probabilitys_per_row = rate_by_rarity = {
    "1-3 card": {
        "◊": "100.000%",
        "◊◊": "0.000%",
        "◊◊◊": "0.000%",
        "◊◊◊◊": "0.000%",
        "☆": "0.000%",
        "☆☆": "0.000%",
        "☆☆☆": "0.000%",
        "♛": "0.000%",
    },
    "4 card": {
        "◊": "0.000%",
        "◊◊": "90.000%",
        "◊◊◊": "5.000%",
        "◊◊◊◊": "1.666%",
        "☆": "2.572%",
        "☆☆": "0.500%",
        "☆☆☆": "0.222%",
        "♛": "0.040%",
    },
    "5 card": {
        "◊": "0.000%",
        "◊◊": "60.000%",
        "◊◊◊": "20.000%",
        "◊◊◊◊": "6.664%",
        "☆": "10.288%",
        "☆☆": "2.000%",
        "☆☆☆": "0.888%",
        "♛": "0.160%",
    },
}

crafting_cost = {
    "◊": 35,
    "◊◊": 70,
    "◊◊◊": 150,
    "◊◊◊◊": 500,
    "☆": 400,
    "☆☆": 1250,
    "☆☆☆": 1500,
    "♛": 2500,
}

FullArt_Rarities = ['☆', '☆☆', '☆☆☆', 'Crown Rare']

packs = ['Pikachu pack', 'Charizard pack', 'Mewtwo pack']

sets = ['A1', 'P-A']


def map_attack_cost(cost_elements):
    cost_list = []

    for cost in cost_elements:
        cost_symbol = cost.text.strip()

        if len(cost_symbol) > 1:
            for letter in cost_symbol:
                cost_type = type_mapping.get(letter, 'Unknown')
                if cost_type == 'Unknown':
                    print(f"Warning: unrecognized symbol '{letter}'.")
                cost_list.append(cost_type)
        else:
            cost_type = type_mapping.get(cost_symbol, 'Unknown')
            if cost_type == 'Unknown':
                print(f"Warning: unrecognized symbol '{cost_symbol}'.")
            cost_list.append(cost_type)

    return cost_list if cost_list else ['No Cost']


def get_probabilities_by_rarity(rarity):
    probabilities = {}
    for row, rates in rate_by_rarity.items():
        if rarity in rates:
            probabilities[row] = rates[rarity]
    return probabilities


def extract_card_info(soup):
    card_info = {}
    card_info['id'] = extract_id(soup)
    card_info['name'] = extract_name(soup)
    card_info['hp'] = extract_hp(soup)
    card_info['card_type'], card_info['evolution_type'] = extract_card_and_evolution_type(soup)
    card_info['image'] = extract_image(soup)
    card_info['attacks'] = extract_attacks(soup)
    card_info['ability'] = extract_ability(soup, card_info['card_type'])
    card_info['weakness'], card_info['retreat'] = extract_weakness_and_retreat(soup)
    card_info['rarity'], card_info['fullart'] = extract_rarity_and_fullart(soup)
    card_info['ex'] = extract_ex_status(card_info['name'])
    card_info['set_details'], card_info['pack'] = extract_set_and_pack_info(soup)
    card_info['alternate_versions'] = extract_alternate_versions(soup)
    card_info['artist'] = extract_artist(soup)
    card_info['probability'] = get_probabilities_by_rarity(card_info['rarity'])
    card_info['crafting_cost'] = extract_crafting_cost(card_info['rarity'])
    return card_info


def extract_id(soup):
    title = soup.find('p', class_='card-text-title')
    return title.find('a')['href'].split('/')[-1]


def extract_name(soup):
    title = soup.find('p', class_='card-text-title')
    return title.find('a').text.strip()


def extract_hp(soup):
    title = soup.find('p', class_='card-text-title')
    return re.sub(r'\D', '', title.text.split(' - ')[-1])


def extract_card_and_evolution_type(soup):
    card_type = re.sub(r'\s+', ' ', soup.find('p', class_='card-text-type').text.strip())
    evolution_info = card_type.split('-')
    evolution_type = evolution_info[1].strip() if len(evolution_info) > 1 else 'Basic'
    return card_type, evolution_type


def extract_image(soup):
    return soup.find('div', class_='card-image').find('img')['src']


def extract_attacks(soup):
    attack_section = soup.find_all('div', class_='card-text-attack')
    attacks = []
    for attack in attack_section:
        attack_info_section = attack.find('p', class_='card-text-attack-info')
        attack_effect_section = attack.find('p', class_='card-text-attack-effect')

        if attack_info_section:
            cost_elements = attack_info_section.find_all('span', class_='ptcg-symbol')
            attack_cost = map_attack_cost(cost_elements)

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
    return attacks


def extract_ability(soup, card_type):
    if card_type.startswith('Trainer'):
        ability_section = soup.find('div', class_='card-text-section')
        if ability_section:
            next_section = ability_section.find_next('div', class_='card-text-section')
            return next_section.text.strip() if next_section else 'No effect'
        return 'No effect'
    else:
        ability_section = soup.find('div', class_='card-text-ability')
        if ability_section:
            ability_name_section = ability_section.find('p', class_='card-text-ability-info')
            ability_effect_section = ability_section.find('p', class_='card-text-ability-effect')
            ability_name = ability_name_section.text.replace('Ability:', '').strip() if ability_name_section else 'Unknown'
            ability_effect = re.sub(r'\[.*?\]', '', ability_effect_section.text).strip() if ability_effect_section else 'No effect'
            return {'name': ability_name, 'effect': ability_effect}
        return {'name': 'No ability', 'effect': 'N/A'}


def extract_weakness_and_retreat(soup):
    weakness_retreat_section = soup.find('p', class_='card-text-wrr')
    if weakness_retreat_section:
        text = [line.strip() for line in weakness_retreat_section.text.strip().split('\n')]
        weakness = text[0].split(': ')[1].strip() if len(text) > 0 and ': ' in text[0] else 'N/A'
        retreat = text[1].split(': ')[1].strip() if len(text) > 1 and ': ' in text[1] else 'N/A'
        return weakness, retreat
    return 'N/A', 'N/A'


def extract_rarity_and_fullart(soup):
    rarity_section = soup.find('table', class_='card-prints-versions')
    if rarity_section:
        current_version = rarity_section.find('tr', class_='current')
        rarity = current_version.find_all('td')[-1].text.strip() if current_version else 'Unknown'
    else:
        rarity = 'Unknown'
    fullart = 'Yes' if rarity in FullArt_Rarities else 'No'
    return rarity, fullart


def extract_ex_status(name):
    return 'Yes' if 'ex' in name.split(" ") else 'No'


def extract_set_and_pack_info(soup):
    set_info = soup.find('div', class_='card-prints-current')
    if set_info:
        set_details = set_info.find('span', class_='text-lg')
        set_number = set_info.find('span').next_sibling
        set_details = set_details.text.strip() if set_details else 'Unknown'
        pack_temp = set_info.find_all('span')[-1].text.strip()
        pack_info = ' '.join(pack_temp.split('·')[-1].split())
        return set_details, pack_info if pack_info in packs else 'Every pack'
    return 'Unknown', 'Unknown'


def extract_alternate_versions(soup):
    alternate_versions = []
    versions = soup.find_all('tr')
    for version in versions:
        version_name = version.find('a')
        rarity_cell = version.find_all('td')[-1] if version.find_all('td') else None
        version_text = version_name.text.replace("\n", "").strip() if version_name else None
        rarity_text = rarity_cell.text.strip() if rarity_cell else None
        if version_text and rarity_text:
            version_text = " ".join(version_text.split())
            alternate_versions.append({'version': version_text, 'rarity': rarity_text if rarity_text != 'Crown Rare' else '♛'})
    if not alternate_versions:
        alternate_versions.append({'version': 'Unknown', 'rarity': 'Unknown'})
    return alternate_versions


def extract_artist(soup):
    artist_section = soup.find('div', class_='card-text-section card-text-artist')
    return artist_section.find('a').text.strip() if artist_section else 'Unknown'


def extract_crafting_cost(rarity):
    return crafting_cost[rarity] if rarity in crafting_cost else 'Unknown'


def iterate_per_set(set_name, start_id, end_id):
    for i in range(start_id, end_id + 1):
        url = f'{BASE_URL}{set_name}/{i}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            card_info = extract_card_info(soup)
        except Exception as e:
            print(f'Error processing card {i}: {e}')
            continue

        for key, value in card_info.items():
            print(f'{key}: {value}')
        print('-' * 40)


def iterate_all_sets():
    for set_name in sets:
        iterate_per_set(set_name, 1, 285)


def convert_cards_to_json(start_id, end_id, filename):
    cards = []
    error_tracker = 0
    for set_name in sets:
        for i in range(start_id, end_id + 1):
            url = f'{BASE_URL}{set_name}/{i}'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                card_info = extract_card_info(soup)
                print(f'Card {i} processed.')
                error_tracker = 0
            except Exception as e:
                print(f'Error processing card {i}: {e}')
                error_tracker += 1
                if error_tracker > 4:
                    print(f'Terminado en la carta {i}')
                    break
                continue

            cards.append(card_info)
    with open(filename, 'w') as file:
        json.dump(cards, file, ensure_ascii=False, indent=4)


# Ejemplo de uso
init_time = time.time()
start_id = 1
end_id = 286
filename = 'cards_data.json'
# convert_cards_to_json(start_id, end_id, filename)
iterate_per_set('A1', 260, 280)
# iterate_per_set('P-A', 1, 30)
end_time = time.time()
print(f'Datos guardados en {filename}, tiempo total: {end_time - init_time} segundos.')