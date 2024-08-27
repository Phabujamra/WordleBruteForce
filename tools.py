def get_text_from_file(file_path: str):
    with open(file=file_path, mode="r") as file:
        return [line.strip() for line in file.readlines()]
    