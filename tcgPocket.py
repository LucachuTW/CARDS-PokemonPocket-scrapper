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
