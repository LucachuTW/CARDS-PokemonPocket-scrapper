from urllib.parse import urlparse
from bs4 import BeautifulSoup
import dateutil
import requests
import card
import tqdm


class Set:
    def __init__(self, url: str) -> None:
        """
        Initialize the Set object.

        Args:
            - url (str): The URL of the set.

        Returns:
            - None
        """
        self.url = url

        response = requests.get(url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.content, "html.parser")

        self.setAll()
        self.checkAssumptions()

    def setAll(self) -> None:
        """
        Set all attributes of the Set class based on the URL.

        Args:
            - None

        Returns:
            - None
        """
        self.setName()
        self.setReleaseDate()
        self.setCardCount()
        self.setCardInfo()
        self.setPacks()

    def setName(self) -> None:
        """
        Set the name of the set based on the URL.

        Args:
            - None

        Returns:
            - None
        """
        name = self.soup.find(class_="infobox-heading sm")

        if not name:
            raise ValueError(f"Set name not found on page: {self.url}")

        self.name = name.get_text(strip=True)

    def setReleaseDate(self) -> None:
        """
        Set the release date of the set based on the URL.

        Args:
            - None

        Returns:
            - None
        """
        infoLine = self.soup.find("div", class_="infobox-line")
        date = None

        # Extract text and split by the bullet (•)
        if infoLine:
            parts = [
                part.strip()
                for part in infoLine.get_text(strip=True, separator="•").split("•")
            ]

            for part in parts:
                try:
                    date = dateutil.parser.parse(part.strip(), fuzzy=False)

                    # Add one second to make the Promos go first
                    date = date + dateutil.relativedelta.relativedelta(seconds=1)
                    break
                except (ValueError, TypeError):
                    continue

            if date is None:
                # This should only be for Promo sets
                if "Promo" not in self.name:
                    print(f"WARNING: Release date not found on page: {self.url}")

                # We use Serebii.net to try and fill in the date
                url = "https://www.serebii.net/tcgpocket/" + self.name.lower().replace(
                    " ", ""
                )
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                # Find the <i> tag containing "Release Date:"
                releaseInfo = soup.find("i", string="Release Date:")
                if releaseInfo:
                    # Get the parent element and extract the full text
                    parent_text = releaseInfo.parent.get_text(strip=True)
                    # Remove the "Release Date:" label and parse the remaining text
                    date_text = (
                        parent_text.replace("Release Date:", "")
                        .split("Amount of Cards")[0]
                        .strip()
                    )
                    date = dateutil.parser.parse(date_text)

        else:
            raise ValueError(f"Release date not found on page: {self.url}")

        self.releaseDate = date

    def setCardCount(self) -> None:
        """
        Set the card count of the set based on the URL.

        Args:
            - None

        Returns:
            - None
        """
        infoLine = self.soup.find("div", class_="infobox-line")
        cardCount = None

        # Extract text and split by the bullet (•)
        if infoLine:
            parts = [
                part.strip()
                for part in infoLine.get_text(strip=True, separator="•").split("•")
            ]

            for part in parts:
                if "cards" in part.lower():
                    # Remove the "cards" part and convert to integer
                    cardCount = int(part.lower().replace("cards", "").strip())
                    break

        if not cardCount:
            raise ValueError(f"Card count not found on page: {self.url}")
        self.cardCount = cardCount

    def setCardInfo(self) -> None:
        """
        Set the card information for the set.

        Args:
            - None

        Returns:
            - None
        """
        self.cards: list[card.Card] = []

        parsedUrl = urlparse(self.url)
        origin = f"{parsedUrl.scheme}://{parsedUrl.hostname}"

        cardsElement = self.soup.find("div", class_="card-search-grid")

        # for a in cardsElement.find_all("a", href=True):
        for a in tqdm.tqdm(
            cardsElement.find_all("a", href=True), desc=f"{self.name} cards"
        ):
            self.cards.append(card.Card(url=f"{origin}{a['href']}"))

    def setPacks(self) -> None:
        """
        Set the packs available for the set.

        Args:
            - None

        Returns:
            - None
        """
        self.packs: list[str] = list(
            {c.pack for c in self.cards if c.pack != "Every pack"}
        )

    def checkAssumptions(self) -> None:
        """
        Check assumptions about the cards.

        Args:
            - None

        Returns:
            - None
        """
        self.checkCardCount()
        self.checkCorrectSet()

    def checkCardCount(self) -> None:
        """
        Check if the number of cards matches the expected card count.

        Args:
            - None

        Returns:
            - None
        """
        if self.cardCount != len(self.cards):
            print(f"There is an inconsistency with the number of cards in {self.name}")

    def checkCorrectSet(self) -> None:
        """
        Check that all the cards have the same name as the set.

        Args:
            - None

        Returns:
            - None
        """
        for card in self.cards:
            assert (
                self.name == card.setDetails
            ), f"Card set {card.setDetails} is not set name {self.name}"

    def getCardData(self) -> list:
        """
        Get the card information for the set.

        Args:
            - None

        Returns:
            - List of Card objects
        """
        return [card.getData() for card in self.cards]
