from lib.gekko.sources import Source
from lib.gekko.tables import Table

class Report:
    def __init__(self, definition):
        defaults = {'headers': True}
        definition['output'] = defaults | definition['output']
        self.definition = definition
        self.sources = {}
        self.tables = {}

        for source in definition['sources']:
            tabledef = definition['sources'][source]
            self.sources[source] = Source.from_definition(tabledef)

        for table in definition['tables']:
            tabledef = definition['tables'][table]
            self.tables[table] = Table(tabledef, self)

    def get_source(self, name):
        return self.sources[name]

    def get_table(self, name):
        return self.tables[name]

    def text(self):
        textbuf = ''
        columns = self.definition['output'].get('columns', [])

        if self.definition['output']['headers']:
            if columns:
                textbuf += ''.join(col + ',' for col in columns[0:-1])
                textbuf += str(columns[-1]) + "\n"

        for out in self.definition['output']['tables']:
            textbuf += self.tables[out].text(columns)

        return textbuf
