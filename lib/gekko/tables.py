from lib.gekko.expression import Expression

class Table:
    NO_GROUP_KEY = '--none--'

    def __init__(self, config, report):
        self.source = report.get_source
        self.table = report.get_table
        self.headers = None
        self.config = config
        self.groups = {}
        self.data = {}

    def get_headers(self):
        return self.headers

    def each_group(self, fn, data=None, path=None):
        data = data or self.data
        path = path or []

        if type(data) == list:
            fn(data, path)
        else:
            for group in data:
                self.each_group(fn, data[group], path + [group])

    def each_row(self, row_fn, data=None):
        data = data or self.data

        def group_fn(data, path):
            nonlocal row_fn
            for row in data:
                row_fn(row)

        self.each_group(group_fn, data)

    def evaluate(self):
        if not 'group' in self.config:
            self.data[self.NO_GROUP_KEY] = []

        self.__load_data()

        if 'per_row' in self.config:
            self.each_row(self.__row_evaluate)

        if 'per_group' in self.config:
            self.each_group(self.__group_evaluate)

    def __row_evaluate(self, row):
        header_vars = self.headers.row_map(row)
        for expr in self.config['per_row']:
            changes = Expression(expr).eval(header_vars)
            for newcol in changes:
                self.headers.add_column(newcol)
                row.append(changes[newcol])

    def __group_evaluate(self, group, path):
        group_memo = {}
        expressions = [ Expression(expr) for expr in self.config['per_group'] ]

        for row in group:
            row_map = self.headers.row_map(row)
            for expr in expressions:
                expr.eval(row_map, group_memo)

        self.__upsert(self.groups, path, lambda val: group_memo)

    def __load_data(self):
        if 'table' in self.config:
            for table in self.config['table']:
                table_obj = self.table(table)
                table_obj.evaluate()
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
        for group in srctable.data:
            for row in srctable.data[group]:
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
        header_idxs = [headers.index(group) for group in self.config['group']]
        path = [row[idx] for idx in header_idxs]
        appendrow = lambda value: [row] if value == None else value + [row]
        self.__upsert(self.data, path, appendrow)

    # Default method for when no grouping is defined.  Just throw each row
    # into a single internal key used to indicate that no explicit group exists

    def __append_row(self, row, headers, idx):
        self.data[self.NO_GROUP_KEY].append(row)

    def __upsert(self, target, path, val_fn):
        current = target
        for key in path[:-1]:
            if key in target:
                current = target[key]
            else:
                current = {}
                target[key] = current

        key = path[-1:][0]
        target[key] = val_fn(target.get(key))
