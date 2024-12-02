# This file should be used for holding every static value. From Xpaths, to timeouts
class GameConfig:
    """
    This holds multiple information regarding the model of the game
    """

    GAME_WORD_LENGTH = 5
    WORDS_PATH = "./dependencies/FLW.txt"
    URL_WORDLE =  "https://www.nytimes.com/games/wordle/index.html"
    DRIVER_PATH = "./dependencies/chromedriver"


class XPaths:
    """
    Holds XPaths for various elements on the web pages.
    """

    # Home page buttons
    button_cookies_reject = "//button[text()='Reject all']"
    button_terms_continue = "//div[@class='purr-blocker-card__content']//button[text()='Continue']"
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
    """
    Defines timeout durations in seconds for various operations.
    """

    XXS = 1
    XS = 2
    S = 5
    M = 10
    L = 30
