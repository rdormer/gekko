import csv
import os

class Source:
    @staticmethod
    def from_definition(definition):
        if 'command' in definition:
            return CmdSource(definition)

        if 'csvfile' in definition:
            return CSVSource(definition)

    def __init__(self, definition):
        if 'defcolumns' in definition:
            self.columns = definition['defcolumns']
        else:
            self.columns = {}

        self.definition = definition
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

    # Checks columns for consistency.  If no columns are defined then there is no defcolumns
    # directive, so grab the first line you come across on the assumption it's a header. From
    # then on, compare the first line of every subsequent set of lines against this to ensure
    # all sets of lines have the same headers (but not if defcolumns is present).  Then remove
    # the headers, returning a lineset stripped of those headers for inclusion in a source

    def validate_headers(self, lines):
        if not self.columns:
            self.columns = lines[0]

        if not 'defcolumns' in self.definition:
            if self.columns != lines[0]:
                return False
            else:
                del lines[0]

        return True

    def header_indices(self, headers):
        if len(headers) == 0:
            return list(range(len(self.columns)))
        else:
            return [self.columns.index(header) for header in headers]

class CSVSource(Source):
    def __init__(self, definition):
        super().__init__(definition)
        defaults = {'delimiter': ",", 'newline': "\n"}
        self.definition = defaults | self.definition

        if type(self.definition['csvfile']) == str:
            self.definition['csvfile'] = [ self.definition['csvfile'] ]

    def load_rows(self, start, length):
        for fname in self.definition['csvfile']:
            linebuf = []
            with open(fname, newline=self.definition['newline']) as csvfile:
                tablereader = csv.reader(csvfile, delimiter=self.definition['delimiter'])
                for row in tablereader:
                    linebuf.append(row)

            if self.validate_headers(linebuf):
                self.rows.extend(linebuf)

class CmdSource(Source):
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

        self.validate_headers(self.rows)

    def concatenate_rows(self, rows, size):
        catlines = []

        for x in range(0, len(rows), size):
          line = rows[x:x+size]
          line = [x + self.definition['delimiter'] for x in line]
          catlines.append(''.join(line))

        return catlines
