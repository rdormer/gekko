from lib.gekko.headers import HeaderSet
import glob
import csv
import os

class Source:
    @staticmethod
    def from_definition(definition):
        if 'command' in definition:
            return CmdSource(definition)

        if 'csvfile' in definition:
            return CSVSource(definition)

        if 'glob' in definition:
            return CSVSource(definition)

    def __init__(self, definition):
        defaults = {'delimiter': ",", 'newline': "\n"}
        self.definition = defaults | definition
        self.headers = HeaderSet(definition)
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
            iterator(self.rows[idx], self.headers, idx)

    def __load_rows(self, start, length):
        pass

    def get_headers(self):
        return self.headers

class CSVSource(Source):
    def __init__(self, definition):
        super().__init__(definition)

    def load_rows(self, start, length):
        if 'csvfile' in self.definition:
            for fname in self.definition['csvfile']:
                self.__load_csv(fname)

        if 'glob' in self.definition:
            filelist = glob.glob(self.definition['glob'])
            for fname in filelist:
                self.__load_csv(fname)

    def __load_csv(self, fname):
        linebuf = []
        with open(fname, newline=self.definition['newline']) as csvfile:
            tablereader = csv.reader(csvfile, delimiter=self.definition['delimiter'])
            for row in tablereader:
                if 'file_column' in self.definition:
                    row.append(fname)

                linebuf.append(row)

        if self.headers.handle_headers(linebuf):
            mapped_lines = [self.headers.row_map(row) for row in linebuf]
            self.rows.extend(mapped_lines)
        else:
            raise Exception(fname + ": failed handling headers")

class CmdSource(Source):
    def __init__(self, definition):
        super().__init__(definition)

    def load_rows(self, start, length):
        rawdata = os.popen(self.definition['command']).read().strip()
        rawdata = rawdata.split(self.definition['newline'])

        if 'rowlines' in self.definition:
            rawdata = self.__concatenate_rows(rawdata, self.definition['rowlines'])

        linebuf = []
        tablereader = csv.reader(rawdata, delimiter=self.definition['delimiter'])
        for row in tablereader:
            linebuf.append(row)

        if self.headers.handle_headers(linebuf):
            mapped_lines = [self.headers.row_map(row) for row in linebuf]
            self.rows.extend(mapped_lines)

    def __concatenate_rows(self, rows, size):
        catlines = []

        for x in range(0, len(rows), size):
          line = rows[x:x+size]
          line = [x + self.definition['delimiter'] for x in line]
          catlines.append(''.join(line))

        return catlines
