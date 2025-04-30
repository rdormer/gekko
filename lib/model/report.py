from lib.expr.expression import Expression
from lib.model.sources import Source
from lib.model.tables import Table
from lib.model.schema import Schema

class Report:
    def __init__(self, definition):
        self.definition = definition
        self.schema = None
        self.sources = {}
        self.tables = {}

        for source in definition['sources']:
            tabledef = definition['sources'][source]
            self.sources[source] = Source.from_definition(tabledef)

        if 'tables' in definition:
            for table in definition['tables']:
                tabledef = definition['tables'][table]
                self.tables[table] = Table(tabledef, self)
                self.tables[table].evaluate()

        if 'schema' in definition:
            schemadef = definition['schema']
            self.schema = Schema(schemadef, self)
            self.schema.evaluate()


    def get_source(self, name):
        return self.sources[name]

    def get_table(self, name):
        return self.tables[name]

    def eval(self, expr):
        return Expression(expr).eval(self.tables)
