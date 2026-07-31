class ParserError(Exception):
    pass


class Parser:
    """Base class for atlas manifest output formats (xml, json, ...).

    Subclasses implement parse() to render an AtlasData into
    self.parser_output, and get_file_ext() to name the output format;
    save() then writes that rendered output to disk.
    """

    parser_output = None

    def __init__(self):
        pass

    def get_file_ext(self):
        """Return the file extension (without a leading dot) this parser writes, e.g. 'xml'."""
        raise NotImplementedError('Parser::get_file_ext() not implemented')

    def parse(self, atlas_data):
        """Render the given AtlasData into self.parser_output."""
        raise NotImplementedError('Parser::parse() not implemented')

    def is_ready_to_save(self):
        return self.parser_output is not None and len(self.parser_output) > 0

    def save(self, filename):
        """Write self.parser_output to filename. Raises ParserError if parse() hasn't run yet."""
        if not self.is_ready_to_save():
            raise ParserError('Cannot save to file - no data, please parse data before trying to save')

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(self.parser_output)
