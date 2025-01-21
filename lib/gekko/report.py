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
        defaults = {'headers': True}
        self.definition = defaults | definition
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

        columns = self.definition['output'].get('columns', [])

        if self.definition['headers']:
            textbuf += ''.join(col + ',' for col in columns[0:-1])
            textbuf += str(columns[-1]) + "\n"

        for out in self.definition['output']['sets']:
            textbuf += self.sets[out].text(columns)

        return textbuf

    def dump_as_string(self):
        return yaml.dump(self.definition)
