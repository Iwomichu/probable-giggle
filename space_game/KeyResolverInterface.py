from space_game.KeyProtocol import KeyProtocol
from space_game.domain_names import KeyId


class KeyResolverInterface:
    def resolve(self, event: KeyId) -> KeyProtocol:
        pass