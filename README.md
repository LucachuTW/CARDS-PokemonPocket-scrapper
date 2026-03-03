# Pokémon TCG Pocket Web Scraper

This [Python script](./pokemontcgp_scrapper.py) scrapes the Pokémon TCG Pocket website to extract card information such as name, type, HP, attacks, weaknesses, and more. It then converts this data into [JSON](https://github.com/LucachuTW/CARDS-PokemonPocket-scrapper/blob/main/pokemon_cards.json). This is run every Sunday by the workflow [main.yml](./.github/workflows/main.yml), so you should wait before creating an issue, because new cards may have been added in between Sundays.

## Features

- Scrapes card information from the Pokémon TCG Pocket website.
- Extracts data like name, type, HP, attacks, weaknesses, and image URLs.
- Saves the extracted data in JSON format.
- It can be used as an API by <https://raw.githubusercontent.com/LucachuTW/CARDS-PokemonPocket-scrapper/refs/heads/main/pokemon_cards.json>

## Requirements

This project requires Python 3.x. To run the script, you need to install the required packages listed in `requirements.txt`. You can install them using pip:

   ```bash
   pip install -r requirements.txt
   ```

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/LucachuTW/CARDS-PokemonPocket-scrapper.git pokemon-tcg-scraper
   cd pokemon-tcg-scraper
   ```

## Data Source

The data for Pokémon cards was obtained from the [Pocket Limitless TCG](https://pocket.limitlesstcg.com/cards) website.

This data was used for the creation of the dataset in JSON.
