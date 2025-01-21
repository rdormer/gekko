from lib.gekko.tables import Table
from lib.gekko.sets import Set
import yaml

class Report:
    @staticmethod
    def load_file(report_path):
        with open(report_path) as repfile:
            report = yaml.safe_load(repfile)
            return Report(report)

    def __init__(self, definition):
        self.definition = definition
        self.tables = {}
        self.sets = {}

        for table in definition['tables']:
            tabledef = definition['tables'][table]
            self.tables[table] = Table.from_definition(tabledef)

        for set in definition['sets']:
            setdef = definition['sets'][set]
            self.sets[set] = Set(setdef, self)

    def get_table(self, name):
        return self.tables[name]

    def get_set(self, name):
        return self.sets[name]

    def text(self):
        textbuf = ''

        for out in self.definition['output']['sets']:
            textbuf += self.sets[out].text()

        return textbuf

    def dump_as_string(self):
        return yaml.dump(self.definition)
