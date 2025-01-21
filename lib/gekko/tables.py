import csv

class Table:
    @staticmethod
    def from_definition(definition):
        return CSVTable(definition)

    def __init__(self, definition):
        self.definition = definition
        self.columns = {}
        self.rows = []

    # returns the *total* size of the set, not the number
    # of currently loaded rows, which should probably
    # stay internal to whatever subclass is implementing this

    def size(self):
        return 0

    def each_row(self, iterator):
        if not self.rows:
            self.load_rows(0, 1000)

        for idx in range(self.size()):
            iterator(self.rows[idx], self.columns, idx)

    def load_rows(self, start, length):
        pass

    def header_indices(self, headers):
        if len(headers) == 0:
            return list(range(len(self.columns)))
        else:
            return [self.columns.index(header) for header in headers]

class CSVTable(Table):
    def __init__(self, definition):
        super().__init__(definition)
        defaults = {'delimiter': ",", 'newline': "\n"}
        self.definition = defaults | self.definition

    def load_rows(self, start, length):
        with open(self.definition['csvfile'], newline=self.definition['newline']) as csvfile:
            tablereader = csv.reader(csvfile, delimiter=self.definition['delimiter'])
            for row in tablereader:
                self.rows.append(row)

            self.columns = self.rows[0]
            del self.rows[0]

    def size(self):
        return len(self.rows)
