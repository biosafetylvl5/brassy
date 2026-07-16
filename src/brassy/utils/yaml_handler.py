"""Load YAML safely, rejecting duplicate keys."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml
from yaml.constructor import ConstructorError

if TYPE_CHECKING:
    from pathlib import Path


class DuplicateKeyError(ConstructorError):
    """
    Raised when a mapping declares the same key more than once.

    Parameters
    ----------
    key : Any
        The key that was declared more than once.
    first_mark : yaml.Mark
        Position of the first occurrence.
    second_mark : yaml.Mark
        Position of the offending repeat occurrence.
    """

    def __init__(
        self, key: Any, first_mark: yaml.Mark, second_mark: yaml.Mark,
    ) -> None:
        self.key = key
        self.first_mark = first_mark
        self.second_mark = second_mark
        super().__init__(
            "while constructing a mapping",
            first_mark,
            f"found duplicate key {key!r}",
            second_mark,
        )


class UniqueKeySafeLoader(yaml.SafeLoader):
    """
    A ``yaml.SafeLoader`` that rejects mappings containing duplicate keys.

    PyYAML follows the permissive reading of the spec and keeps only the last
    of a set of duplicate keys, so a release note declaring ``bug fix:`` twice
    silently loses the first block of entries. This loader raises instead.
    """

    def construct_mapping(
        self, node: yaml.MappingNode, deep: bool = False,
    ) -> dict[Any, Any]:
        """
        Construct a mapping, raising if any key appears more than once.

        Parameters
        ----------
        node : yaml.MappingNode
            The mapping node being constructed.
        deep : bool
            Whether to construct child nodes eagerly.

        Returns
        -------
        dict[Any, Any]
            The constructed mapping.

        Raises
        ------
        DuplicateKeyError
            If a key appears more than once in the mapping.
        """
        # Merge keys ("<<") have no constructor until they are expanded, so the
        # node must be flattened before any key is constructed below.
        self.flatten_mapping(node)
        seen: dict[Any, yaml.Mark] = {}
        for key_node, _value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError:
                continue  # PyYAML raises its own "found unhashable key" below
            if key in seen:
                raise DuplicateKeyError(key, seen[key], key_node.start_mark)
            seen[key] = key_node.start_mark
        return super().construct_mapping(node, deep)


def load_yaml(stream: Any, file_path: str | Path) -> Any:
    """
    Parse a YAML document, rejecting duplicate keys and malformed syntax.

    Parameters
    ----------
    stream : Any
        An open file object or string containing YAML.
    file_path : str | Path
        Path to the source file, used in the error message.

    Returns
    -------
    Any
        The parsed YAML content.

    Raises
    ------
    ValueError
        If the document contains duplicate keys or is not valid YAML.
    """
    try:
        return yaml.load(stream, Loader=UniqueKeySafeLoader)  # noqa: S506
    except DuplicateKeyError as e:
        raise ValueError(
            f"Duplicate key {e.key!r} in {file_path} on line "
            f"{e.second_mark.line + 1}, first defined on line "
            f"{e.first_mark.line + 1}. Combine the two entries or remove one.",
        ) from e
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}:\n{e}") from e
