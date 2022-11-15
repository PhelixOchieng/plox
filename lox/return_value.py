class ReturnValue(Exception):
    def __init__(self, value, *args: object) -> None:
        super().__init__(*args)
        self.value = value
