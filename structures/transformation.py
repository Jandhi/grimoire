class Transformation:
    def __init__(self,
        offset : tuple[int, int, int] = None,
        mirror : tuple[bool, bool, bool] = None,
        diagonal_mirror : bool = False,
    ) -> None:
        self.offset = offset or (0, 0, 0)
        self.mirror = mirror or (False, False, False)
        self.diagonal_mirror = diagonal_mirror