from lib.expr.expression import Expression
from lib.model.sources import Source
from lib.model.schema import Schema

class Report:
    def __init__(self, definition):
        self.definition = definition
        self.schemas = {}
        self.sources = {}
        self.tables = {}

        for source in definition['sources']:
            tabledef = definition['sources'][source]
            self.sources[source] = Source.from_definition(tabledef)

        if 'schemas' in definition:
            for schema in definition['schemas']:
                schemadef = definition['schemas'][schema]
                self.schemas[schema] = Schema(schemadef, self)
                self.schemas[schema].evaluate()

    def get_source(self, name):
        return self.sources[name]

    def get_schema(self, name):
        return self.schemas[name]

    def eval(self, expr):
        return Expression(expr).eval(self.schemas)
