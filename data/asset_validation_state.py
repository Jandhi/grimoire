class AssetValidationState:
    def __init__(self, missing_args : list[tuple[str, type]] = None, surplus_args : list[tuple[str, type]] = None) -> None:
        self.missing_args = missing_args or []
        self.surplus_args = surplus_args or []

    def is_invalid(self):
        return len(self.missing_args) > 0