import csv
import os

class Table:
    @staticmethod
    def from_definition(definition):
        if 'command' in definition:
            return CmdTable(definition)

        if 'csvfile' in definition:
            return CSVTable(definition)

    def __init__(self, definition):
        self.definition = definition
        self.columns = {}
        self.rows = []

    # returns the *total* size of the set, not the number
    # of currently loaded rows, which should probably
    # stay internal to whatever subclass is implementing this

    def total_size(self):
        return len(self.rows)

    def current_size(self):
        return len(self.rows)

    def each_row(self, iterator):
        if not self.rows:
            self.load_rows(0, 1000)

        for idx in range(self.total_size()):
            iterator(self.rows[idx], self.columns, idx)

    def load_rows(self, start, length):
        pass

    def define_headers(self):
        if 'defcolumns' in self.definition:
            self.columns = self.definition['defcolumns']
        else:
            self.columns = self.rows[0]
            del self.rows[0]

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

            self.define_headers()

class CmdTable(Table):
    def __init__(self, definition):
        super().__init__(definition)
        defaults = {'delimiter': ",", 'newline': "\n"}
        self.definition = defaults | self.definition

    def load_rows(self, start, length):
        rawdata = os.popen(self.definition['command']).read().strip()
        rawdata = rawdata.split(self.definition['newline'])

        if 'rowlines' in self.definition:
            rawdata = self.concatenate_rows(rawdata, self.definition['rowlines'])

        tablereader = csv.reader(rawdata, delimiter=self.definition['delimiter'])
        for row in tablereader:
            self.rows.append(row)

        self.define_headers()

    def concatenate_rows(self, rows, size):
        catlines = []

        for x in range(0, len(rows), size):
          line = rows[x:x+size]
          line = [x + self.definition['delimiter'] for x in line]
          catlines.append(''.join(line))

        return catlines
