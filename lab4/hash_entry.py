class HashEntry:

    def __init__(
        self,
        key=None,
        value=None,
        collision=False,
        occupied=False,
        terminal=True,
        link=False,
        deleted=False,
        p0=-1
    ):

        # ID
        self.key = key

        # Pi
        self.value = value

        # Flags
        self.collision = collision  # C
        self.occupied = occupied    # U
        self.terminal = terminal    # T
        self.link = link            # L
        self.deleted = deleted      # D

        # Pointer
        self.p0 = p0

    def __str__(self):
        return (
            f"{self.key} | "
            f"{self.collision} | "
            f"{self.occupied} | "
            f"{self.terminal} | "
            f"{self.link} | "
            f"{self.deleted} | "
            f"{self.p0} | "
            f"{self.value}"
        )