from mappings import Type, Rarity, AttackCost
from bs4 import BeautifulSoup
import requests
import random
import time
import re


class Card:
    """
    Class representing a Card object.
    """

    def __init__(self, url: str) -> None:
        """
        Initialize Card object.

        Args:
            - url (str): The URL of the card

        Returns:
            - None
        """
        self.url = url

        response = requests.get(url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.content, "html.parser")

        self.setAll()

        # Random sleep to not overload requests
        time.sleep(random.random())

    def setAll(self) -> None:
        """
        Set all attributes of the card.

        Args:
            - None

        Returns:
            - None
        """
        self.setID()
        self.setName()
        self.setHP()
        self.setType()
        self.setCardType()
        self.setEvolutionType()
        self.setImage()
        self.setAttacks()
        self.setAbility()
        self.setWeakness()
        self.setRetreat()
        self.setRarity()
        self.setFullArt()
        self.setShiny()
        self.setExStatus()
        self.setSetDetails()
        self.setPack()
        self.setAlternateVersions()
        self.setArtist()
        self.setFlavorText()
        self.setProbabilities()
        self.setCraftingCost()

    def setID(self) -> None:
        """
        Set the ID of the card.

        Args:
            - None

        Returns:
            - None
        """
        titleElement = self.soup.find("p", class_="card-text-title")
        self.id = int(titleElement.find("a")["href"].split("/")[-1])

    def setName(self) -> None:
        """
        Set the name of the card.

        Args:
            - None

        Returns:
            - None
        """
        name = self.soup.find("p", class_="card-text-title").find("a")

        if not name:
            raise ValueError(f"Card name not found on page: {self.url}")

        self.name = name.get_text(strip=True)

    def setHP(self) -> None:
        """
        Set the HP of the card.

        Args:
            - None

        Returns:
            - None
        """
        titleElement = self.soup.find("p", class_="card-text-title")
        hpText = re.sub(r"\D", "", titleElement.text.split(" - ")[-1])

        # If no HP is found (like in trainer cards), set to None
        self.hp = int(hpText) if hpText else None

    def setType(self) -> None:
        """
        Set the type of the card.

        Args:
            - None

        Returns:
            - None
        """
        cType = None
        titleElement = self.soup.find("p", class_="card-text-title")
        if titleElement and titleElement.text:
            parts = titleElement.text.split(" - ")

            # Get the known type names from the Type class
            known_type_names = Type.getTypeList()

            # Search for a known type name in the parts
            for part in parts:
                cleaned_part = part.strip()
                if cleaned_part in known_type_names:
                    cType = cleaned_part

        if not cType:
            cType = "Unknown Type"
            # print(f"DEBUG: Could not find a known type in the parts: {parts}")

        self.type = cType

    def setCardType(self) -> None:
        """
        Set the card type of the card.

        Args:
            - None

        Returns:
            - None
        """
        # Placeholder for card type logic
        self.cardType = re.sub(
            r"\s+", " ", self.soup.find("p", class_="card-text-type").text.strip()
        )

    def setEvolutionType(self) -> None:
        """
        Set the evolution type of the card.

        Args:
            - None

        Returns:
            - None
        """
        evolutionInfo = self.cardType.split("-")
        self.evolutionType = (
            evolutionInfo[1].strip() if len(evolutionInfo) > 1 else "Basic"
        )

    def setImage(self) -> None:
        """
        Set the image URL of the card.

        Args:
            - None

        Returns:
            - None
        """
        self.image = self.soup.find("div", class_="card-image").find("img")["src"]

    def setAttacks(self) -> None:
        """
        Set the attacks of the card.

        Args:
            - None

        Returns:
            - None
        """
        attackSections = self.soup.find_all("div", class_="card-text-attack")
        self.attacks = []

        for attack in attackSections:
            attackInfoSection = attack.find("p", class_="card-text-attack-info")
            attackEffectSection = attack.find("p", class_="card-text-attack-effect")

            if attackInfoSection:
                costElements = attackInfoSection.find_all("span", class_="ptcg-symbol")
                attackCost = AttackCost.mapAttackCost(costElements)

                attackText = attackInfoSection.text.strip()
                for costElement in costElements:
                    attackText = attackText.replace(costElement.text, "").strip()

                attackParts = attackText.rsplit(" ", 1)
                attackName = (
                    attackParts[0].strip() if len(attackParts) > 1 else "Unknown"
                )
                attackDamage = attackParts[1].strip() if len(attackParts) > 1 else "0"
                attackEffect = (
                    attackEffectSection.text.strip()
                    if attackEffectSection
                    else "No effect"
                )

                self.attacks.append(
                    {
                        "cost": attackCost,
                        "name": attackName,
                        "damage": attackDamage,
                        "effect": attackEffect,
                    }
                )

    def setAbility(self) -> None:
        """
        Set the ability of the card.

        Args:
            - None

        Returns:
            - None
        """
        ability = None

        if self.cardType.startswith("Trainer"):
            abilitySection = self.soup.find("div", class_="card-text-section")
            if abilitySection:
                nextSection = abilitySection.find_next(
                    "div", class_="card-text-section"
                )
                ability = nextSection.text.strip() if nextSection else "No effect"
            else:
                ability = "No effect"

        else:
            abilitySection = self.soup.find("div", class_="card-text-ability")
            if abilitySection:
                abilityNameSection = abilitySection.find(
                    "p", class_="card-text-ability-info"
                )
                abilityEffectSection = abilitySection.find(
                    "p", class_="card-text-ability-effect"
                )
                abilityName = (
                    abilityNameSection.text.replace("Ability:", "").strip()
                    if abilityNameSection
                    else "Unknown"
                )
                abilityEffect = (
                    re.sub(r"\[.*?\]", "", abilityEffectSection.text).strip()
                    if abilityEffectSection
                    else "No effect"
                )
                ability = {"name": abilityName, "effect": abilityEffect}
            else:
                ability = {"name": "No ability", "effect": "N/A"}

        self.ability = ability

    def setWeakness(self) -> None:
        """
        Set the weakness of the card.

        Args:
            - None

        Returns:
            - None
        """
        weakeness = "N/A"
        weaknessRetreatSection = self.soup.find("p", class_="card-text-wrr")

        if weaknessRetreatSection:
            text = [
                line.strip() for line in weaknessRetreatSection.text.strip().split("\n")
            ]
            if len(text) > 0 and ": " in text[0]:
                weakeness = text[0].split(": ")[1].strip()

        self.weakness = weakeness

    def setRetreat(self) -> None:
        """
        Set the retreat cost of the card.

        Args:
            - None

        Returns:
            - None
        """
        retreat = "N/A"
        weaknessRetreatSection = self.soup.find("p", class_="card-text-wrr")

        if weaknessRetreatSection:
            text = [
                line.strip() for line in weaknessRetreatSection.text.strip().split("\n")
            ]
            if len(text) > 1 and ": " in text[1]:
                retreat = int(text[1].split(": ")[1].strip())

        self.retreat = retreat

    def setRarity(self) -> None:
        """
        Set the rarity of the card.

        Args:
            - None

        Returns:
            - None
        """
        rarity = "Unknown"
        raritySection = self.soup.find("table", class_="card-prints-versions")

        if raritySection:
            currentVersion = raritySection.find("tr", class_="current")
            if currentVersion:
                rarity = currentVersion.find_all("td")[-1].text.strip()

        self.rarity = rarity

    def setFullArt(self) -> None:
        """
        Set the Full Art status of the card.

        Args:
            - None

        Returns:
            - None
        """
        self.fullart = Rarity.isFullArt(self.rarity)

    def setExStatus(self) -> None:
        """
        Set the ex status of the card.

        Args:
            - None

        Returns:
            - None
        """
        self.ex = "ex" in self.name.split(" ")

    def setShiny(self) -> None:
        """
        Set the shiny status of the card.

        This is not detected in each card, it is changed
        afterwards based on the information of:
        https://pocket.limitlesstcg.com/cards/?q=is:shiny,sfa&show=all

        Args:
            - None

        Returns:
            - None
        """
        self.shiny = False

    def setSetDetails(self) -> None:
        """
        Set the set details of the card.

        Args:
            - None

        Returns:
            - None
        """
        setDetails = "Unknown"
        setInfo = self.soup.find("div", class_="card-prints-current")

        if setInfo:
            setDetailsElement = setInfo.find("span", class_="text-lg")
            if setDetailsElement:
                setDetails = setDetailsElement.text.strip()
                setDetails = " ".join(setDetails.split())

        self.setDetails = setDetails

    def setPack(self) -> None:
        """
        Set the pack information of the card.

        Args:
            - None

        Returns:
            - None
        """
        pack = None
        setInfo = self.soup.find("div", class_="card-prints-current")

        if setInfo:
            packTempElement = setInfo.find_all("span")[-1]
            packTemp = packTempElement.text.strip() if packTempElement else ""

            if len(packTemp.split("·")) > 2:
                packInfo = packTemp.split("·")[2].strip()
                pack = " ".join(packInfo.split())
            else:
                pack = "Every pack"

        else:
            pack = "Unknown"

        self.pack = pack

    def setAlternateVersions(self) -> None:
        """
        Set the alternate versions of the card.

        Args:
            - None

        Returns:
            - None
        """
        # Will be empty if no alternate versions are found
        self.alternateVersions = []
        versions = self.soup.find_all("tr")

        for version in versions:
            versionName = version.find("a")
            rarityCells = version.find_all("td")
            rarityCell = rarityCells[-1] if rarityCells else None

            versionText = (
                versionName.text.replace("\n", "").strip() if versionName else None
            )

            # Some cards (Promo-A) may not have rarity info
            rarityText = rarityCell.text.strip() if rarityCell else ""

            if versionText:
                versionText = " ".join(versionText.split())

                setName, id = versionText.split("#")

                # Do not add the card as an alternate version of itself
                if setName.strip() not in self.setDetails or int(id.strip()) != self.id:

                    self.alternateVersions.append(
                        {
                            "set": setName.strip(),
                            "id": int(id.strip()),
                            "rarity": rarityText if rarityText != "Crown Rare" else "♛",
                        }
                    )

    def setArtist(self) -> None:
        """
        Set the artist of the card.

        Args:
            - None

        Returns:
            - None
        """
        artist = "Unknown"
        artistSection = self.soup.find(
            "div", class_="card-text-section card-text-artist"
        )

        if artistSection:
            artistLink = artistSection.find("a")
            if artistLink:
                artist = artistLink.text.strip()

        self.artist = artist

    def setFlavorText(self) -> None:
        """
        Set the flavor text of the card.

        Args:
            - None

        Returns:
            - None
        """
        flavorText = ""
        flavorSection = self.soup.find(
            "div", class_="card-text-section card-text-flavor"
        )

        if flavorSection:
            flavorText = flavorSection.text.strip()

        self.flavorText = flavorText

    def setProbabilities(self) -> None:
        """
        Set the probabilities of the card based on rarity.

        Args:
            - None

        Returns:
            - None
        """
        self.probabilities = Rarity.getProbabilitiesByRarity(self.rarity)

    def setCraftingCost(self) -> None:
        """
        Set the crafting cost of the card.

        Args:
            - None

        Returns:
            - None
        """
        craftingCost = "Unknown"

        if self.rarity:
            craftingCost = Rarity.getCraftingCost(self.rarity)

        self.craftingCost = craftingCost

    def getData(self) -> dict:
        """
        Get card data as a dictionary

        Args:
            - None

        Returns:
            - dict: Dictionary containing all card attributes
        """
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "type": self.type,
            "card_type": self.cardType,
            "evolution_type": self.evolutionType,
            "image": self.image,
            "attacks": self.attacks,
            "ability": self.ability,
            "weakness": self.weakness,
            "retreat": self.retreat,
            "rarity": self.rarity,
            "fullart": self.fullart,
            "shiny": self.shiny,
            "ex": self.ex,
            "set_details": self.setDetails,
            "pack": self.pack,
            "alternate_versions": self.alternateVersions,
            "artist": self.artist,
            "flavorText": self.flavorText,
            "probabilities": self.probabilities,
            "crafting_cost": self.craftingCost,
        }
