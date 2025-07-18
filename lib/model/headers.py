class HeaderSet:
    def __init__(self, definition):
        self.definition = definition
        if 'defcolumns' in self.definition:
            self.header_names = self.definition['defcolumns']
        else:
            self.header_names = []

    def add_column(self, colname):
        if colname not in self.header_names:
            self.header_names.append(colname)

    def row_map(self, row):
        return dict(zip(self.header_names, row))

    # if columns are defined, we don't care about the first line
    # if columns are not defined and we have none, grab the first line.  Those are your columns now.
    # if columns are not defined and we have some, compare them

    def handle_headers(self, lines):
        if 'defcolumns' in self.definition:
            self.header_names = self.definition['defcolumns']
            if 'file_column' in self.definition:
                self.header_names.append(self.definition['file_column'])
            return True
        else:
            if 'file_column' in self.definition:
                lines[0].pop()
                lines[0].append(self.definition['file_column'])

            lines[0] = self.__remap_columns(lines[0])

            if not self.header_names:
                self.header_names = lines[0]

            if self.header_names == lines[0]:
                del lines[0]
                return True
            else:
                return False

    def to_text(self):
        ''.join(self.header_names[idx] + ',' for idx in headers)

    def equal_to(self, other_headers):
        return len(self.header_names) == len(other_headers.header_names)

    def __remap_columns(self, cols):
        if 'rename_columns' in self.definition:
            def rename_if(x):
                return self.definition['rename_columns'][x] if x in self.definition['rename_columns'] else x
            return [rename_if(x) for x in cols ]
        else:
            return cols
