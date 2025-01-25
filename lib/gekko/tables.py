from lib.gekko.expression import Expression


class Table:
    NO_GROUP_KEY = '--none--'

    def __init__(self, config, report):
        self.source = report.get_source
        self.table = report.get_table
        self.headers = None
        self.config = config
        self.groups = {}

    def each_group(self, fn, data=None):
        data = data or self.groups

        if type(data) == list:
            fn(data)
        else:
            for group in data:
                self.each_group(fn, data[group])

    def each_row(self, row_fn, data=None):
        data = data or self.groups

        def group_fn(data):
            nonlocal row_fn
            for row in data:
                row_fn(row)

        self.each_group(group_fn, data)

    def text(self, headers_to_print):
        self.__evaluate()
        buffer = ''

        def row_fmt(row):
            nonlocal buffer
            filtered = self.headers.filter_tuple(row, headers_to_print)
            line = ''.join(str(x) + ',' for x in filtered)
            buffer += line[:-1] + "\n"

        self.each_row(row_fmt)
        return buffer

    def __evaluate(self):
        if not 'group' in self.config:
            self.groups[self.NO_GROUP_KEY] = []

        self.__load_data()

        if 'per_row' in self.config:
            self.each_row(self.__row_evaluate)

    def __row_evaluate(self, row):
        header_vars = self.headers.row_map(row)
        for expr in self.config['per_row']:
            changes = Expression(expr).eval(header_vars)
            for newcol in changes:
                self.headers.add_column(newcol)
                row.append(changes[newcol])

    def __load_data(self):
        if 'table' in self.config:
            for table in self.config['table']:
                table_obj = self.table(table)
                table_obj.__evaluate()
                self.__set_headers_if(table_obj)
                self.__append(table_obj)

        if 'source' in self.config:
            for source in self.config['source']:
                data = self.source(source)
                self.__set_headers_if(data)

                if 'group' in self.config:
                    data.each_row(self.__collect_groups)
                else:
                    data.each_row(self.__append_row)

    def __append(self, srctable):
        for group in srctable.groups:
            for row in srctable.groups[group]:
                if 'group' in self.config:
                    self.__collect_groups(row, [], -1)
                else:
                    self.__append_row(row, [], -1)

    def __set_headers_if(self, srcobj):
        if not self.headers and srcobj.headers:
            self.headers = srcobj.headers

    # Grouping method.  Takes each row, traverses down the groups map, creating
    # new keys as it goes along, until it gets to the last group, where it either
    # creates or appends to an array of the rows for that group

    def __collect_groups(self, row, headers, idx):
        group_keys = self.config['group']
        current_tree = self.groups

        for group in group_keys[:-1]:
            group_index = headers.index(group)
            group_value = row[group_index]

            if not group_value in current_tree:
                current_tree[group_value] = {}

            current_tree = current_tree[group_value]

        group_index = headers.index(group_keys[-1])
        last_group = row[group_index]

        if last_group in current_tree:
            current_tree[last_group] += [row]
        else:
            current_tree[last_group] = [row]

    # Default method for when no grouping is defined.  Just throw each row
    # into a single internal key used to indicate that no explicit group exists

    def __append_row(self, row, headers, idx):
        self.groups[self.NO_GROUP_KEY].append(row)
