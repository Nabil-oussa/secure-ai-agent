class SecurityContext:
    def __init__(
        self,
        identity: str,
        attributes: dict,
    ):
        self.identity = identity
        self.attributes = attributes