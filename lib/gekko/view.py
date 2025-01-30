class View:
    def __init__(self, config, args):
        defaults = {'headers': True}
        self.config = defaults | config['output']
        self.columns = self.config.get('columns', [])
        self.delimiter = "\t" if args.usetabs else ','

    def text(self, report):
        textbuf = self.__fmt_headers()
        textbuf += self.__fmt_tables(report)

        return textbuf

    def __fmt_headers(self):
        textbuf = ''
        if self.config['headers']:
            if self.columns:
                textbuf += ''.join(col + self.delimiter for col in self.columns[0:-1])
                textbuf += str(self.columns[-1]) + "\n"

        return textbuf

    def __fmt_tables(self, report):
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
            buffer += self.__row_format(row, headers, headers_to_print)

        table.each_row(row_fmt)
        return buffer

    def __row_format(self, row, headers, headers_to_print):
        row_buffer = ''

        if type(row) == list:
            filtered = headers.filter_tuple(row, headers_to_print)
            line = ''.join(str(x) + self.delimiter for x in filtered)
        else:
            line = ''.join(str(row[key]) + self.delimiter for key in headers_to_print)

        row_buffer += line[:-1] + "\n"
        return row_buffer
