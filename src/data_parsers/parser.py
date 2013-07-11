class ParserError(Exception):
    pass


class Parser:
    parser_output = None

    def __init__(self):
        pass

    def get_file_ext(self):
        raise NotImplementedError('Parser::get_file_ext() not implemented')

    def parse(self, atlas_data):
        raise NotImplementedError('Parser::parse() not implemented')

    def is_ready_to_save(self):
        return self.parser_output is not None and len(self.parser_output) > 0

    def save(self, filename):
        if not self.is_ready_to_save():
            raise ParserError('Cannot save to file - no data, please parse data before trying to save')

        file = open(filename, 'w')
        file.write(self.parser_output)
