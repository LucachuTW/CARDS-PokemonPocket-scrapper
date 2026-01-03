from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import set


class TGCPocket:

    def __init__(self):
        self.url = "https://pocket.limitlesstcg.com/cards"

        response = requests.get(self.url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.content, "html.parser")

        self.setAll()

    def setAll(self) -> None:
        """
        Set all attributes.

        Args:
            - None

        Returns:
            - None
        """
        self.setSets()
        self.setShiny()

    def setSets(self) -> None:
        """
        Set the card sets.

        Args:
            - None

        Returns:
            - None
        """
        self.sets: list[set.Set] = []

        parsedUrl = urlparse(self.url)
        origin = f"{parsedUrl.scheme}://{parsedUrl.hostname}"

        setsElement = self.soup.find("table", class_="data-table sets-table striped")

        for row in setsElement.find_all("tr"):
            link = row.find("a", href=True)

            if link:
                self.sets.append(set.Set(f"{origin}{link['href']}"))

    def setShiny(self) -> None:
        """
        Set shiny status for all sets.

        Args:
            - None

        Returns:
            - None
        """
        # Get the origin URL to use hrefs correctly
        parsedUrl = urlparse(self.url)
        origin = f"{parsedUrl.scheme}://{parsedUrl.hostname}"

        shinyUrl = f"{origin}/cards/?q=is:shiny,sfa&show=all"

        response = requests.get(shinyUrl)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # The cards are in a div with class "card-search-grid"
        cardsElement = soup.find("div", class_="card-search-grid")

        # Iterate through all card links
        for card in cardsElement.find_all("a", href=True):
            cardUrl = f"{origin}{card['href']}"
            setUrl = "/".join(cardUrl.split("/")[:-1])

            # Find the card with the matching URL and set shiny to True
            for setInstance in self.sets:
                if setInstance.url == setUrl:
                    for cardInstance in setInstance.cards:
                        if cardInstance.url == cardUrl:
                            cardInstance.shiny = True
                            # No need to continue searching
                            break

    def getCardData(self) -> list[dict]:
        """
        Get card data from all sets.

        Args:
            - None

        Returns:
            - list[dict]: List of dictionaries containing card data
        """
        cardData = []

        for setInstance in self.sets:
            cardData.extend(setInstance.getCardData())

        return cardData

    def getCardDataSorted(self) -> list[dict]:
        """
        Get card data from all sets, sorted by id.

        Args:
            - None

        Returns:
            - list[dict]: List of dictionaries containing card data
        """
        cardData = self.getCardData()

        sortedCardData = sorted(
            cardData,
            key=lambda card: (
                {s.name: s for s in self.sets}[card["set_details"]].releaseDate,
                int(card["id"]),
            ),
        )

        return sortedCardData
