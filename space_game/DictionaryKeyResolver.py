from typing import Dict

from space_game.KeyProtocol import KeyProtocol
from space_game.KeyResolverInterface import KeyResolverInterface
from space_game.domain_names import KeyId


class DictionaryKeyResolver(KeyResolverInterface):
    def __init__(self, dictionary: Dict[KeyId, KeyProtocol]) -> None:
        self.dictionary = dictionary

    def resolve(self, event: KeyId) -> KeyProtocol:
        return self.dictionary.get(event)