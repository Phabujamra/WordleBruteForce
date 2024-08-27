import random

from selenium.webdriver.common.by import By

import browser
import tools


GAME_WORD_LENGTH = 5

WORDS_PATH = "./dependencies/FLW.txt"

URL_WORDLE = "https://www.nytimes.com/games/wordle/index.html"
DRIVER_PATH = "./dependencies/chromedriver"


class XPaths:
    # Home page buttons
    button_cookies_reject = "//button[text()='Reject all']"
    button_play = "//button[text()='Play']"

    # Play page buttons
    button_close_instructions = "//h2[text()='How To Play']/following-sibling::button[@aria-label='Close']"

    # Letter on keyboard XPATH
    @staticmethod
    def letter_on_keyboard(value):
        if len(value) > 1:
            raise ValueError(f"The value can only contain one letter. Value = {value}")
        return f"//button[@data-key='{value}']"
    
    # Tile value based on row and column
    @staticmethod
    def tile(row, column):
        return f"//div[@role='group' and @aria-label='Row {row}']//div[@aria-roledescription='tile' and contains(@aria-label, '{column}')]"
    
    # This will return the XPATH of the tile after the confirmation of the input (ENTER pressed)
    @staticmethod
    def tile_after_check(row, column):
        return f"//div[@role='group' and @aria-label='Row {row}']//div[@aria-roledescription='tile' and contains(@aria-label, '{column}') and (@data-state='correct' or @data-state='present' or @data-state='absent')]"


class Timeouts:
    XXS = 1
    XS = 2
    S = 5
    M = 10
    L = 30


class BrowserGame(browser.Browser):
    def init_game(self, url: str):
        self.goto(url=url)
        self.click_element(by=By.XPATH, value=XPaths.button_cookies_reject, timeout=Timeouts.M)
        self.click_element(by=By.XPATH, value=XPaths.button_play, timeout=Timeouts.S)
        self.click_element(by=By.XPATH, value=XPaths.button_close_instructions, timeout=Timeouts.S)

    
    def write_word(self, word: str):
        if len(word) != 5:
            raise ValueError(f"Words need to have 5 letters. Current word {word} has {len(word)} letters.")
        for letter in word:
            letter_xpath = XPaths.letter_on_keyboard(value=letter)
            self.click_element(by=By.XPATH, value=letter_xpath, timeout=Timeouts.S)

    
    def submit_word(self) -> None:
        value_xpath = XPaths.letter_on_keyboard("↵")
        self.click_element(by=By.XPATH, value=value_xpath, timeout=Timeouts.S)

    
    def read_tile_value(self, row: int, column: int):
        value_xpath = XPaths.tile_after_check(row=row, column=column)
        return self.get_element_text(by=By.XPATH, value=value_xpath, timeout=Timeouts.S)


    def get_tile_property(self, row: int, column: int, property_name: str):
        # Calculates the XPath of the element
        value_xpath = XPaths.tile_after_check(row=row, column=column)
        # Gets the element once available
        element = self.wait_for_element(by=By.XPATH, value=value_xpath, timeout=Timeouts.S)
        # Use get_dom_attribute because it is JS managed
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
        
        for i in range(1, word_len+1, 1):
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
    

class GameLogic():
    def __init__(self, words_file_path: str) -> None:
        self.words_list = self._read_words_from_file(file_path=words_file_path)
        self.current_game_row = 0


    def _read_words_from_file(self, file_path: str):
        words = tools.get_text_from_file(file_path=file_path)
        print(f"Loaded {len(words)} words from the file.")
        return words


    def randomize_non_repeating_letters_word(self):
        words_list = self.words_list[:]
        # Do the loop until a result is found
        while True:
            # Choose a random word
            rand_word = random.choice(words_list)
            # If the word len == 5, and there are no repeting letters
            if len(set(rand_word)) == len(rand_word):
                # Return the word
                return rand_word
            # Otherwise we remove the word from the list, so if cannot be selected again
            words_list.remove(rand_word)

    
    def randomize_word(self):
        # Choose a random word
        rand_word = random.choice(self.words_list)
        # Delete from the words_list
        self.words_list.remove(rand_word)
        # Return the word
        return rand_word
    

    def randomize_word_based_on_row(self):
        if not self.words_list:
            raise ValueError("Word list is empty. Cannot randomize word.")
        if self.current_game_row == 1:
            word = self.randomize_non_repeating_letters_word()
        else:
            word = self.randomize_word()

        return word

    # # Removes all words that have the absent_letter    
    # def filter_words_absent(self, absent_letter: str):
    #     self.words_list = [word for word in self.words_list if absent_letter not in word]


    # # Removes all the words that doesn't have the correct letter in the idx index    
    # def filter_words_correct(self, correct_letter: str, idx: int):
    #     self.words_list = [word for word in self.words_list if (correct_letter == word[idx])]


    # Removes all the words that does not contain the contained_letter, or that have it in the specific index    
    def filter_words_correct(self, correct_letter: str, idx: int):
        original_length = len(self.words_list)
        self.words_list = [word for word in self.words_list if (correct_letter == word[idx])]
        print(f"Filtered words correct '{correct_letter}' at index {idx}. {original_length} -> {len(self.words_list)}")

    def filter_words_present(self, present_letter: str, idx: int):
        original_length = len(self.words_list)
        self.words_list = [word for word in self.words_list if ((present_letter != word[idx]) and (present_letter in word))]
        print(f"Filtered words present '{present_letter}' not at index {idx}. {original_length} -> {len(self.words_list)}")

    def filter_words_absent(self, absent_letter: str, occurrence: int) -> None:
        original_length = len(self.words_list)
        self.words_list = [word for word in self.words_list if not word.count(absent_letter) >= occurrence]
        print(f"Filtered words multiple absent '{absent_letter}' {occurrence} times. {original_length} -> {len(self.words_list)}")


    def filter_words_based_on_type(self, letter: str, type: str, idx: int = None, ocurrence: int = None):
        if type.lower() == "absent":
            if ocurrence is None:
                # TODO: Change variable input type later
                raise ValueError("Ocurrence (ocurrence) must be provided for 'absent' type")
            self.filter_words_absent(absent_letter=letter, occurrence=ocurrence)

        elif type.lower() == "present":
            if idx is None:
                # TODO: Change variable input type later
                raise ValueError("Index (idx) must be provided for 'present' type.")
            self.filter_words_present(present_letter=letter, idx=idx)

        elif type.lower() == "correct":
            if idx is None:
                # TODO: Change variable input type later
                raise ValueError("Index (idx) must be provided for 'correct' type.")
            self.filter_words_correct(correct_letter=letter, idx=idx)
        else:
            raise ValueError(f"Invalid type '{type}' specified. Use 'absent', 'correct', or 'present'.")
        

    def increase_game_current_row(self):
        self.current_game_row += 1

    
    def get_word_based_on_row(self):
        if self.current_game_row == 1:
            return self.randomize_non_repeating_letters_word()
        elif self.current_game_row != 1:
            return self.randomize_word


    # Order by place, presence, absence?
    # Lock the already filtered chars?
    def filter_words_options(self, properties: list) -> None:
        # Order by Present, Correct, Absent?
        # Define custom order for filtering
        order = {"correct": 0, "present": 1, "absent": 2} # This is important not to filter repeated absent letter words
        # Sort the dict in the correct order
        sorted_properties = sorted(properties, key=lambda item: order[item["type"]])
        already_filtered = [] # Declared empty so it can store looped letters

        for idx, letter in enumerate(sorted_properties):
            letter_value = letter["value"]
            already_filtered.append(letter_value)
            self.filter_words_based_on_type(
                letter=letter.get("value"),
                type=letter.get("type"),
                idx=letter.get("idx"),
                ocurrence=already_filtered.count(letter_value)
            )


def play_game(bot, game):
    # Do first steps to start the game
    bot.init_game(url=URL_WORDLE)

    while game.current_game_row <= 6:
        game.increase_game_current_row()
        word = game.randomize_word_based_on_row()
        bot.write_word(word=word)
        bot.submit_word()

        letters = bot.get_word_properties(row=game.current_game_row, word_len=GAME_WORD_LENGTH)
        game.filter_words_options(properties=letters)


def main():
    try:
        # Initialize the driver
        bot = BrowserGame(driver_path=DRIVER_PATH, headless=False)
        
        # Start game class to proceed with actions
        game = GameLogic(words_file_path=WORDS_PATH)

        # Play game to the end
        play_game(bot=bot, game=game)
    except Exception as e:
        raise
    finally:
        input("Press any key to exit...")


if __name__ == "__main__":
    main()
