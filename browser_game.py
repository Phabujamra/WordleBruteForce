from selenium.webdriver.common.by import By

import browser
from constants import Timeouts, XPaths


class BrowserGame(browser.Browser):
    """
    BrowserGame class extends the Browser class to encapsulate all 
    interactions specific to playing the Wordle game in the browser.
    """

    def init_game(self) -> None:
        """
        Initializes the game by navigating to the given URL and performing initial setup steps.

        Args:
            url (str): The URL of the Wordle game.
        """
        self.goto(url=self.url)
        self.click_element(by=By.XPATH, value=XPaths.button_cookies_reject, timeout=Timeouts.M)
        self.click_element(by=By.XPATH, value=XPaths.button_terms_continue, timeout=Timeouts.S)
        self.click_element(by=By.XPATH, value=XPaths.button_play, timeout=Timeouts.S)
        self.click_element(by=By.XPATH, value=XPaths.button_close_instructions, timeout=Timeouts.S)

    def write_word(self, word: str) -> None:
        """
        Writes a word into the Wordle game input by simulating keyboard clicks.

        Args:
            word (str): The word to be input into the game.
        """
        for letter in word:
            letter_xpath = XPaths.letter_on_keyboard(value=letter)
            self.click_element(by=By.XPATH, value=letter_xpath, timeout=Timeouts.S)

    def submit_word(self) -> None:
        """
        Submits the currently entered word in the game by simulating a click on the Enter key.
        """
        value_xpath = XPaths.letter_on_keyboard("↵")
        self.click_element(by=By.XPATH, value=value_xpath, timeout=Timeouts.S)

    def read_tile_value(self, row: int, column: int) -> str:
        """
        Reads the value (letter) displayed on a tile at a specific row and column.

        Args:
            row (int): The row number of the tile.
            column (int): The column number of the tile.

        Returns:
            str: The letter value on the specified tile.
        """
        value_xpath = XPaths.tile_after_check(row=row, column=column)
        return self.get_element_text(by=By.XPATH, value=value_xpath, timeout=Timeouts.S)

    def get_tile_property(self, row: int, column: int, property_name: str) -> str:
        """
        Retrieves a specific property of a tile at a given row and column.

        Args:
            row (int): The row number of the tile.
            column (int): The column number of the tile.
            property_name (str): The name of the property to retrieve.

        Returns:
            str: The value of the specified property for the tile.
        """
        value_xpath = XPaths.tile_after_check(row=row, column=column)
        element = self.wait_for_element(by=By.XPATH, value=value_xpath, timeout=Timeouts.S)
        return element.get_dom_attribute(name=property_name)

    def get_word_properties(self, row: int, word_len: int) -> list[dict]:
        """
        Retrieve properties for each tile in a specified row.

        Args:
            row (int): The row number to retrieve tile properties from.
            word_len (int): The length of the word, determining the number of tiles to process.

        Returns:
            list[dict]: A list of dictionaries where each dictionary contains 'value' and 'type' of the tile.
        """
        word_info = []
        
        if row < 0:
            raise ValueError("Invalid row. Row must be non-negative.")
        if word_len <= 0:
            raise ValueError("Invalid word length. Word length must be positive.")
        
        for i in range(1, word_len + 1):
            letter_info = {}
            idx = i - 1
            try:
                letter_info["value"] = self.read_tile_value(row=row, column=i).lower()
                letter_info["type"] = self.get_tile_property(row=row, column=i, property_name="data-state")
                letter_info["idx"] = idx
            except Exception as e:
                # Handle any potential errors, raise with additional context
                raise RuntimeError(f"Error retrieving properties for tile at row {row}, column {i}: {e}")
            
            word_info.append(letter_info)
        
        return word_info
