from typing import Optional

from atlas.atlas_data import AtlasData


class ParserError(Exception):
    pass


class Parser:
    """Base class for atlas manifest output formats (xml, json, ...).

    Subclasses implement parse() to render an AtlasData into
    self.parser_output, and get_file_ext() to name the output format;
    save() then writes that rendered output to disk.
    """

    parser_output: Optional[str] = None

    def __init__(self) -> None:
        pass

    def get_file_ext(self) -> str:
        """Return the file extension (without a leading dot) this parser writes, e.g. 'xml'."""
        raise NotImplementedError('Parser::get_file_ext() not implemented')

    def parse(self, atlas_data: AtlasData) -> None:
        """Render the given AtlasData into self.parser_output."""
        raise NotImplementedError('Parser::parse() not implemented')

    def is_ready_to_save(self) -> bool:
        return self.parser_output is not None and len(self.parser_output) > 0

    def save(self, filename: str) -> None:
        """Write self.parser_output to filename. Raises ParserError if parse() hasn't run yet."""
        if not self.is_ready_to_save() or self.parser_output is None:
            raise ParserError('Cannot save to file - no data, please parse data before trying to save')

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(self.parser_output)
