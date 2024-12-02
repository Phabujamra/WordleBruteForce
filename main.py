from browser_game import BrowserGame
from constants import GameConfig
from game_logic import GameLogic


DRIVER_PATH = GameConfig.DRIVER_PATH
URL_WORDLE = GameConfig.URL_WORDLE
WORDS_PATH = GameConfig.WORDS_PATH
GAME_WORD_LENGTH = GameConfig.GAME_WORD_LENGTH


def play_game(bot: BrowserGame, game: GameLogic) -> None:
    """
    Automates playing the Wordle game using the given bot and game logic.

    Args:
        bot (BrowserGame): The bot that interacts with the browser.
        game (GameLogic): The logic that handles word filtering and selection.
    """
    # Do first steps to start the game
    bot.init_game()

    while game.current_game_row <= 6:
        game.increase_game_current_row()
        word = game.randomize_word_based_on_row()
        bot.write_word(word=word)
        bot.submit_word()

        letters = bot.get_word_properties(row=game.current_game_row, word_len=GAME_WORD_LENGTH)
        if game.check_for_win(letters=letters):
            return True, f"Game won with word {word}"

        game.filter_words_options(properties=letters)

    return False, f"Last word tried: {word}"

def main() -> None:
    """
    Main function to start and run the Wordle bot game.
    """
    try:
        # Initialize the driver
        bot = BrowserGame(driver_path=DRIVER_PATH, url=URL_WORDLE, headless=False)
        
        # Start game class to proceed with actions
        game = GameLogic(words_file_path=WORDS_PATH, words_len=GAME_WORD_LENGTH)

        # Play game to the end
        win, message = play_game(bot=bot, game=game)
        print(f"Win: {win}, Message: {message}")
    except Exception as e:
        raise
    finally:
        # input("Press any key to exit...")
        # So far quit() is after the end so we can check the browser
        bot.quit()


if __name__ == "__main__":
    main()
