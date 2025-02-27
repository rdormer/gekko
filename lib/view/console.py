class Console:
    def __init__(self, config, args):
        defaults = {'headers': True}
        self.config = defaults | config['output']
        self.columns = self.config.get('columns', [])
        self.delimiter = "\t" if args.usetabs else ','

    def text(self, report):
        textbuf = self.__fmt_headers()
        textbuf += self.__table_expr(report)
        textbuf += self.__fmt_tables(report)
        return textbuf

    def __table_expr(self, report):
        if 'expression' in self.config:
            columns = self.config.get('columns', None)
            lvalue = report.eval(self.config['expression'])
            return self.__text(lvalue, columns)
        else:
            return ''

    def __fmt_headers(self):
        textbuf = ''
        if self.config['headers']:
            if self.columns:
                textbuf += ''.join(col + self.delimiter for col in self.columns[0:-1])
                textbuf += str(self.columns[-1]) + "\n"

        return textbuf

    def __fmt_tables(self, report):
        textbuf = ''
        if 'tables' in self.config:
            for out in self.config['tables']:
                table = report.get_table(out)
                textbuf += self.__text(table, self.columns)

        return textbuf

    def __text(self, table, headers_to_print):
        buffer = ''
        headers = table.get_headers()

        def row_fmt(row, memo):
            nonlocal buffer
            buffer += self.__row_format(row, headers, headers_to_print)

        table.each_row(row_fmt)
        return buffer

    def __row_format(self, row, headers, headers_to_print):
        if headers_to_print:
            line = ''.join(str(row[key]) + self.delimiter for key in headers_to_print)
        else:
             line = ''.join(row[key] + self.delimiter for key in row)

        return line[:-1] + "\n"
