class MissingAPIKey(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"{name} is not configured")


class ModelError(Exception):
    pass


class TranscriptionError(Exception):
    pass
