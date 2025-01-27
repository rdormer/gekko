class View:
    def __init__(self, config):
        self.config = config['output']
        self.columns = self.config.get('columns', [])

    def fmt_headers(self):
        textbuf = ''
        if self.config['headers']:
            if self.columns:
                textbuf += ''.join(col + ',' for col in self.columns[0:-1])
                textbuf += str(self.columns[-1]) + "\n"

        return textbuf

    def fmt_tables(self, report):
        textbuf = ''
        for out in self.config['tables']:
            table = report.get_table(out)
            textbuf += self.__text(table, self.columns)

        return textbuf

    def __text(self, table, headers_to_print):
        buffer = ''
        headers = table.get_headers()

        def row_fmt(row):
            nonlocal buffer
            filtered = headers.filter_tuple(row, headers_to_print)
            line = ''.join(str(x) + ',' for x in filtered)
            buffer += line[:-1] + "\n"

        table.each_row(row_fmt)
        return buffer
