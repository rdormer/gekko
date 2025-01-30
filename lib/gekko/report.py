from lib.gekko.sources import Source
from lib.gekko.tables import Table
from lib.gekko.view import View

class Report:
    def __init__(self, definition):
        self.definition = definition
        self.sources = {}
        self.tables = {}

        for source in definition['sources']:
            tabledef = definition['sources'][source]
            self.sources[source] = Source.from_definition(tabledef)

        for table in definition['tables']:
            tabledef = definition['tables'][table]
            self.tables[table] = Table(tabledef, self)
            self.tables[table].evaluate()

    def get_source(self, name):
        return self.sources[name]

    def get_table(self, name):
        return self.tables[name]
