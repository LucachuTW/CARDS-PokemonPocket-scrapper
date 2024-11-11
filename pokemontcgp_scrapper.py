import requests
from bs4 import BeautifulSoup
import csv
import json

# URL del sitio de las cartas
url = 'https://pocket.limitlesstcg.com/cards/A1?display=compact'

# Realizamos la solicitud HTTP para obtener el contenido de la página
response = requests.get(url)
html_content = response.text

# Analizamos el HTML con BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Encontramos todas las cartas en la página
cards = soup.find_all('div', class_='card-classic')

# Lista para almacenar los datos de las cartas
card_data = []

# Extraemos los detalles de cada carta
for card in cards:
    card_info = {}

    # Nombre de la carta
    name_section = card.find('span', class_='card-text-name')
    if name_section:
        card_info['name'] = name_section.text.strip()

    # Tipo y HP de la carta
    type_hp_section = card.find('p', class_='card-text-title')
    if type_hp_section:
        type_hp_text = type_hp_section.text.strip()
        # Extraemos el tipo y HP (por ejemplo: "Grass - 70 HP")
        type_hp = type_hp_text.split(' - ')
        if len(type_hp) > 0:
            card_info['type'] = type_hp[0].strip()  # Tipo de carta (por ejemplo: "Grass")
        else:
            card_info['type'] = 'N/A'
        if len(type_hp) > 1:
            card_info['hp'] = type_hp[1].strip()  # HP (por ejemplo: "70 HP")
        else:
            card_info['hp'] = 'N/A'

    # Tipo de carta
    card_type_section = card.find('p', class_='card-text-type')
    if card_type_section:
        card_info['card_type'] = card_type_section.text.strip()

    # Ataques de la carta
    attack_section = card.find_all('p', class_='card-text-attack-info')
    if attack_section:
        attacks = []
        for attack in attack_section:
            attack_details = attack.text.strip()
            # Asegúrate de que haya al menos 3 partes (nombre, coste, daño)
            if len(attack_details.split()) >= 3:
                attack_name = attack_details.split()[1]  # Nombre del ataque
                attack_damage = attack_details.split()[2]  # Daño del ataque
                attacks.append({'name': attack_name, 'damage': attack_damage})
        card_info['attacks'] = attacks
    else:
        card_info['attacks'] = []  # Si no tiene ataques, asignamos una lista vacía

    # Debilidad y coste de retiro
    weakness_retreat_section = card.find('p', class_='card-text-wrr')
    if weakness_retreat_section:
        text = weakness_retreat_section.text.strip().split('\n')
        card_info['weakness'] = text[0].split(': ')[1] if len(text) > 0 else 'N/A'
        card_info['retreat'] = text[1].split(': ')[1] if len(text) > 1 else 'N/A'

    # Extraemos la URL de la imagen
    image_section = card.find('img', class_='card shadow max-xs')
    if image_section and 'src' in image_section.attrs:
        card_info['image_url'] = image_section.attrs['src']

    # Agregar los datos extraídos a la lista
    card_data.append(card_info)

# Guardar los resultados en un archivo CSV
csv_filename = 'pokemon_cards.csv'
csv_fields = ['name', 'type', 'hp', 'card_type', 'attacks', 'weakness', 'retreat', 'image_url']

with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
    writer.writeheader()
    for card in card_data:
        # Convertir ataques en una cadena para escribir en CSV
        card['attacks'] = ', '.join([f"{attack['name']} {attack['damage']}" for attack in card['attacks']])
        writer.writerow(card)

# Guardar los resultados en un archivo JSON
json_filename = 'pokemon_cards.json'
with open(json_filename, mode='w', encoding='utf-8') as jsonfile:
    json.dump(card_data, jsonfile, indent=4, ensure_ascii=False)

# Mostrar los resultados por consola
for card in card_data:
    print(f"Name: {card['name']}")
    print(f"Type: {card.get('type', 'N/A')}")
    print(f"HP: {card.get('hp', 'N/A')}")
    print(f"Card Type: {card.get('card_type', 'N/A')}")
    print(f"Image URL: {card.get('image_url', 'N/A')}")
    print(f"Weakness: {card.get('weakness', 'N/A')}")
    print(f"Retreat Cost: {card.get('retreat', 'N/A')}")
    
    # Comprobamos si la carta tiene ataques antes de intentar imprimirlos
    if card['attacks']:
        print(f"Attacks: {card['attacks']}")
    else:
        print("Attacks: N/A")
    
    print('-' * 40)
