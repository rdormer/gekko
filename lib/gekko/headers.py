class HeaderSet:
    def __init__(self, definition):
        self.definition = definition
        if 'defcolumns' in self.definition:
            self.header_names = self.definition['defcolumns']
        else:
            self.header_names = []

    def __indices__(self, headers):
        if len(headers) == 0:
            return list(range(len(self.header_names)))
        else:
            return [self.header_names.index(header) for header in headers]

    def add_column(self, colname):
        if colname not in self.header_names:
            self.header_names.append(colname)

    def filter_tuple(self, tuple, headers):
        return [tuple[idx] for idx in self.__indices__(headers)]

    def index(self, name):
        return self.header_names.index(name)

    def row_map(self, row):
        t = {}
        for idx in range(len(row)):
            key = self.header_names[idx]
            t[key] = row[idx]

        return t

    # if columns are defined, we don't care about the first line
    # if columns are not defined and we have none, grab the first line.  Those are your columns now.
    # if columns are not defined and we have some, compare them

    def handle_headers(self, lines):
        if not 'defcolumns' in self.definition:
            if not self.header_names:
                self.header_names = lines[0]

            if self.header_names == lines[0]:
                del lines[0]
                return True
            else:
                return False

        return True

    def to_text(self):
        ''.join(self.header_names[idx] + ',' for idx in headers)
