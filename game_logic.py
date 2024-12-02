import random

import tools

class GameLogic:
    """
    GameLogic class handles the logic of filtering and selecting words during the Wordle game.
    """

    def __init__(self, words_file_path: str, words_len: int) -> None:
        """
        Initializes the GameLogic with a list of words from the specified file.

        Args:
            words_file_path (str): The path to the file containing the list of words.
        """
        self.words_list = self._read_words_from_file(file_path=words_file_path)
        self.words_len = words_len
        self.current_game_row = 0

    def _read_words_from_file(self, file_path: str) -> list[str]:
        """
        Reads words from a specified file.

        Args:
            file_path (str): The path to the file to read words from.

        Returns:
            list[str]: A list of words read from the file.
        """
        words = tools.get_text_from_file(file_path=file_path)
        print(f"Loaded {len(words)} words from the file.")
        return words

    def randomize_non_repeating_letters_word(self) -> str:
        """
        Randomly selects a word from the list that has no repeating letters.

        Returns:
            str: A randomly selected word with no repeating letters.
        """
        words_list = self.words_list[:]
        while True:
            rand_word = random.choice(words_list)
            if len(set(rand_word)) == len(rand_word):
                return rand_word
            words_list.remove(rand_word)

    def randomize_word(self) -> str:
        """
        Randomly selects and removes a word from the list.

        Returns:
            str: A randomly selected word.
        """
        rand_word = random.choice(self.words_list)
        self.words_list.remove(rand_word)
        return rand_word

    def randomize_word_based_on_row(self) -> str:
        """
        Randomly selects a word based on the current game row.

        Returns:
            str: A randomly selected word, with specific rules for row 1.
        """
        if not self.words_list:
            raise ValueError("Word list is empty. Cannot randomize word.")
        if self.current_game_row == 1:
            word = self.randomize_non_repeating_letters_word()
        else:
            word = self.randomize_word()

        return word

    def filter_words_correct(self, correct_letter: str, idx: int) -> None:
        """
        Filters the list of words to only include those with the correct letter in the specified position.

        Args:
            correct_letter (str): The letter that must be at the specified index.
            idx (int): The index at which the letter must be present.
        """
        original_length = len(self.words_list)
        self.words_list = [word for word in self.words_list if correct_letter == word[idx]]
        print(f"Filtered words correct '{correct_letter}' at index {idx}. {original_length} -> {len(self.words_list)}")

    def filter_words_present(self, present_letter: str, idx: int) -> None:
        """
        Filters the list of words to exclude those with the present letter at the specified position, 
        but include those with the letter elsewhere.

        Args:
            present_letter (str): The letter that must be present but not at the specified index.
            idx (int): The index at which the letter must not be present.
        """
        original_length = len(self.words_list)
        self.words_list = [word for word in self.words_list if (present_letter != word[idx]) and (present_letter in word)]
        print(f"Filtered words present '{present_letter}' not at index {idx}. {original_length} -> {len(self.words_list)}")

    def filter_words_absent(self, absent_letter: str, occurrence: int) -> None:
        """
        Filters the list of words to exclude those that contain the absent letter 
        more than or equal to the specified occurrence.

        Args:
            absent_letter (str): The letter that must not appear more than the given occurrence.
            occurrence (int): The maximum allowed occurrence of the letter.
        """
        original_length = len(self.words_list)
        self.words_list = [word for word in self.words_list if word.count(absent_letter) < occurrence]
        print(f"Filtered words multiple absent '{absent_letter}' {occurrence} times. {original_length} -> {len(self.words_list)}")

    def filter_words_based_on_type(self, letter: str, type: str, idx: int = None, occurrence: int = None) -> None:
        """
        Filters the list of words based on the type of letter information.

        Args:
            letter (str): The letter to be used for filtering.
            type (str): The type of filtering to apply ('correct', 'present', 'absent').
            idx (int, optional): The index position for 'correct' or 'present' filtering. Defaults to None.
            occurrence (int, optional): The maximum allowed occurrence for 'absent' filtering. Defaults to None.

        Raises:
            ValueError: If an invalid type is specified.
        """
        if type == "absent":
            self.filter_words_absent(absent_letter=letter, occurrence=occurrence)
        elif type == "present":
            self.filter_words_present(present_letter=letter, idx=idx)
        elif type == "correct":
            self.filter_words_correct(correct_letter=letter, idx=idx)
        else:
            raise ValueError(f"Invalid type '{type}' specified.")
        
    def increase_game_current_row(self) -> None:
        """
        Increments the current game row by 1.
        """
        self.current_game_row += 1

    def get_word_based_on_row(self) -> str:
        """
        Retrieves a word based on the current game row.

        Returns:
            str: A word selected based on the current game row.
        """
        if self.current_game_row == 1:
            return self.randomize_non_repeating_letters_word()
        elif self.current_game_row != 1:
            return self.randomize_word()

    def filter_words_options(self, properties: list[dict]) -> None:
        """
        Filters the list of words based on the provided properties of letters.

        Args:
            properties (list[dict]): A list of dictionaries containing letter properties with 'value', 'type', and 'idx'.
        """
        # Define custom order for sorting by 'type'
        order = {"correct": 0, "present": 1, "absent": 2}
        
        # Sort the properties list based on the custom order
        sorted_properties = sorted(properties, key=lambda item: order[item["type"]])

        # Using a dictionary to track occurrences
        already_filtered = {}

        # Loop values and add them to the dict
        for letter in sorted_properties:
            letter_value = letter["value"]
            letter_type = letter["type"]
            letter_idx = letter.get("idx")

            # Increment the occurrence count
            already_filtered[letter_value] = already_filtered.get(letter_value, 0) + 1
            
            self.filter_words_based_on_type(
                letter=letter_value,
                type=letter_type,
                idx=letter_idx,
                occurrence=already_filtered[letter_value]
            )

    def check_for_win(self, letters: list[dict]) -> bool:
        """
        Checks if the current information from the website indicates a win.

        Args:
            letters (list[dict]): A list of dictionaries where each dict is information about a letter.

        Returns:
            bool: Game won state.
        """
        # Loop the letters information, if all letters type are correct, return True
        # If not all types are correct, it means we didn't win the game
        for letter in letters:
            if letter["type"] != "correct":
                return False
        
        return True