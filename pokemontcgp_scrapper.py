import requests
from bs4 import BeautifulSoup
import json
import re

# URL of the card site
url = 'https://pocket.limitlesstcg.com/cards/A1?display=compact'

# Make the HTTP request to get the page content
response = requests.get(url)
html_content = response.text

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all the cards on the page
cards = soup.find_all('div', class_='card-classic')

# List to store card data
card_data = []

# Mapping dictionary for letters and types
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

# Function to map symbols to types, with splitting for longer strings
def map_attack_cost(cost_elements):
    cost_list = []  # List to store energy types
    
    for cost in cost_elements:
        cost_symbol = cost.text.strip()  # Extract the energy symbol
        
        # If the symbol consists of multiple letters, split it
        if len(cost_symbol) > 1:
            for letter in cost_symbol:
                cost_type = type_mapping.get(letter, 'Unknown')
                if cost_type == 'Unknown':
                    print(f"Warning: unrecognized symbol '{letter}'.")
                cost_list.append(cost_type)
        else:
            # Case where the symbol is a single letter
            cost_type = type_mapping.get(cost_symbol, 'Unknown')
            if cost_type == 'Unknown':
                print(f"Warning: unrecognized symbol '{cost_symbol}'.")
            cost_list.append(cost_type)

    # Return the list of costs
    return cost_list if cost_list else ['No Cost']


# Extract the details of each card
for card in cards:
    card_info = {}

    # Card ID
    card_set_info_section = card.find('div', class_='card-set-info')
    if card_set_info_section:
        card_info['card_id'] = card_set_info_section.text.strip().replace(' ', '')
    else:
        card_info['card_id'] = 'UnknownID'


    # Card name
    name_section = card.find('span', class_='card-text-name')
    card_info['name'] = name_section.text.strip() if name_section else 'Unknown'

    # Card type and HP
    type_hp_section = card.find('p', class_='card-text-title')
    if type_hp_section:
        # Remove the card name and split the rest
        content = type_hp_section.text.replace(card_info['name'], '').strip()
        # Remove extra dashes and split the remaining text
        parts = [part.strip() for part in content.split('-') if part.strip()]

        if len(parts) >= 2:
            card_info['type'] = parts[0]  # Type (e.g., "Grass")
            # Extract only the numeric value of HP
            card_info['hp'] = re.sub(r'\D', '', parts[1])  # Removes everything except numbers
        else:
            card_info['type'] = 'N/A'
            card_info['hp'] = 'N/A'


    # Card type
    card_type_section = card.find('p', class_='card-text-type')
    stages = ['Basic', 'Stage 1', 'Stage 2']
    card_info['card_type'] = next((stage for stage in stages if stage in card_type_section.text), 'Unknown') if card_type_section else 'Unknown'

    # Card attacks
    attack_section = card.find_all('div', class_='card-text-attack')
    attacks = []
    for attack in attack_section:
        attack_info_section = attack.find('p', class_='card-text-attack-info')
        attack_effect_section = attack.find('p', class_='card-text-attack-effect')

        if attack_info_section:
            cost_elements = attack_info_section.find_all('span', class_='ptcg-symbol')
            attack_cost = map_attack_cost(cost_elements)  # Use the improved function

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

    # Card ability
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

    # Weakness and retreat cost
    weakness_retreat_section = card.find('p', class_='card-text-wrr')
    if weakness_retreat_section:
        text = weakness_retreat_section.text.strip().split('\n')
        card_info['weakness'] = text[0].split(': ')[1] if len(text) > 0 and ': ' in text[0] else 'N/A'
        card_info['retreat'] = text[1].split(': ')[1] if len(text) > 1 and ': ' in text[1] else 'N/A'

    # Image URL
    image_section = card.find('img', class_='card shadow max-xs')
    card_info['image_url'] = image_section.attrs['src'] if image_section and 'src' in image_section.attrs else 'N/A'

    # Add the extracted data to the list
    card_data.append(card_info)

# Save the results in JSON format
json_filename = 'pokemon_cards.json'
with open(json_filename, mode='w', encoding='utf-8') as jsonfile:
    json.dump(card_data, jsonfile, indent=4, ensure_ascii=False)

# Output for confirmation
print(json.dumps(card_data, indent=4, ensure_ascii=False))


# Display the results on the console
for card in card_data:
    print(f"Card ID: {card['card_id']}")
    print(f"Name: {card['name']}")
    print(f"Type: {card.get('type', 'N/A')}")
    print(f"HP: {card.get('hp', 'N/A')}")
    print(f"Card Type: {card.get('card_type', 'N/A')}")
    #print(f"Image URL: {card.get('image_url', 'N/A')}")
    print(f"Weakness: {card.get('weakness', 'N/A')}")
    print(f"Retreat Cost: {card.get('retreat', 'N/A')}")
    
    # Check if the card has attacks before attempting to print them
    if card['attacks']:
        print(f"Attack cost: {attack_cost}")
        print(f"Attacks: {card['attacks']}")
    else:
        print("Attacks: N/A")
    
    print('-' * 40)
