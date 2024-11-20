# Pokémon TCG Pocket Web Scraper

This Python script scrapes the Pokémon TCG Pocket website to extract card information such as name, type, HP, attacks, weaknesses, and more. 
It then converts this data into JSON and optionally saves it to a CSV file.

## Features
- Scrapes card information from the Pokémon TCG Pocket website.
- Extracts data like name, type, HP, attacks, weaknesses, and image URLs.
- Saves the extracted data in JSON format.

## Requirements

This project requires Python 3.x. To run the script, you need to install the following Python packages:

- `requests`: To make HTTP requests to fetch the webpage content.

   ```python
   pip install requests beautifulsoup4
### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pokemon-tcg-scraper.git
   cd pokemon-tcg-scraper
## Data Source

The data for Pokémon cards was obtained from the [Pocket Limitless TCG](https://pocket.limitlesstcg.com/cards/A1?display=text) website.

This data was used for the creation of the dataset in JSON.