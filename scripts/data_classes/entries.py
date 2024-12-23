from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List


@dataclass
class BaseEntry(ABC):
    """
    Abstract base class representing a biological entity with common properties.
    All specific entry types (e.g., GeneEntry, AnonymousEntry) inherit from this class.
    """
    name: str  # The name of the entity
    type: str  # The type of the entity (e.g., 'gene', 'group')

    @abstractmethod
    def get_details(self) -> str:
        """
        Abstract method to return detailed information about the entity.
        Must be implemented by subclasses.
        """
        pass


@dataclass
class GeneEntry(BaseEntry):
    link: str
    aliases: List[str]

    def get_details(self) -> str:
        """
        Returns a string containing detailed information about the gene.
        """
        return f"GeneEntry(name={self.name}, type={self.type}, link={self.link}, aliases={self.aliases})"


@dataclass
class MapEntry(BaseEntry):
    link: str
    aliases: List[str]

    def get_details(self) -> str:
        """
        Returns a string containing detailed information about the gene.
        """
        return f"MapEntry(name={self.name}, type={self.type}, link={self.link}, aliases={self.aliases})"


@dataclass
class CompoundEntry(BaseEntry):
    link: str
    aliases: List[str]

    def get_details(self) -> str:
        """
        Returns a string containing detailed information about the gene.
        """
        return f"CompoundEntry(name={self.name}, type={self.type}, link={self.link}, aliases={self.aliases})"


@dataclass
class GroupEntryNode(BaseEntry):
    """
    Represents an anonymous group entity with components.
    Inherits from BaseEntry.
    """

    components: List[BaseEntry]

    def get_details(self) -> str:
        """
        Returns a string containing detailed information about the group and its components.
        """
        component_names = [component.name for component in self.components]
        return f"AnonymousEntry(name={self.name}, type={self.type}, components={component_names})"


@dataclass
class GeneRelation:
    def __init__(self, entry1: BaseEntry, entry2: BaseEntry, relation_type: str, subtypes: List):
        self.entry1 = entry1
        self.entry2 = entry2
        self.relation_type = relation_type
        self.subtypes = subtypes
