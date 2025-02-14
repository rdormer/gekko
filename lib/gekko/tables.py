from lib.gekko.expression import Expression
from lib.gekko.headers import HeaderSet

class Table:
    NO_GROUP_KEY = '--none--'

    def __init__(self, config, report):
        self.sortdir = config.get('desc', False)

        self.headers = None
        self.config = config
        self.groups = {}
        self.data = {}

        if report != None:
            self.source = report.get_source
            self.table = report.get_table

    def get_headers(self):
        cols = self.config.get('columns')
        rval = self.headers

        if cols:
            rval = HeaderSet(self.config)
            line = [ cols ]
            rval.handle_headers(line)

        return rval

    def each_group(self, fn, data=None, path=None):
        data = data or self.data
        path = path or []

        if type(data) == list:
            fn(data, path)
        else:
            for group in sorted(data, reverse=self.sortdir):
                if len(data[group]) > 0:
                    self.each_group(fn, data[group], path + [group])

    def each_row(self, row_fn, data=None):
        data = data or self.groups
        data = data or self.data

        def group_fn(data, path):
            nonlocal row_fn
            for row in data:
                row_fn(row)

        self.each_group(group_fn, data)

    def evaluate(self):
        if self.data:
            return

        self.__load_data()

        if 'per_row' in self.config:
            self.each_row(self.__row_evaluate)

        if 'row_filter' in self.config:
            self.each_group(self.__filter_rows)

        if 'per_group' in self.config:
            self.each_group(self.__group_evaluate)

    def __row_evaluate(self, row):
        for expr in self.config['per_row']:
            changes = Expression(expr).eval(row)
            for newcol in changes:
                self.headers.add_column(newcol)

    def __group_evaluate(self, group, path):
        group_memo = dict(zip(self.config['group'], path))
        expressions = [ Expression(expr) for expr in self.config['per_group'] ]

        for row in group:
            new_row = row | group_memo

            for expr in expressions:
                expr.eval(new_row)

        self.__upsert(self.groups, path, lambda val: [new_row])

    def __filter_rows(self, data, path):
        def predicate(row):
            for filter in self.config['row_filter']:
                if Expression(filter).eval(row):
                    return False

            return True

        data[:] = [x for x in data if predicate(x)]

    def __load_data(self):
        if not 'group' in self.config:
            self.data[self.NO_GROUP_KEY] = []
        else:
            self.group_expressions = [Expression(group) for group in self.config['group']]

        if 'tables' in self.config:
            for table in self.config['tables']:
                table_obj = self.table(table)
                table_obj.evaluate()
                self.__set_or_validate_headers(table_obj, table)
                self.__append(table_obj)

        if 'sources' in self.config:
            for source in self.config['sources']:
                data = self.source(source)
                self.__set_or_validate_headers(data, source)

                if 'group' in self.config:
                    data.each_row(self.__collect_groups)
                else:
                    data.each_row(self.__append_row)

    def __append(self, srctable):
        def switch_on_row(row):
            nonlocal srctable

            if self.config.get('columns'):
                row = [row[key] for key in self.config['columns']]

            if 'group' in self.config:
                self.__collect_groups(row, [], -1)
            else:
                self.__append_row(row, [], -1)

        srctable.each_row(switch_on_row)

    def __set_or_validate_headers(self, srcobj, name):
        if self.headers:
            if not self.headers.equal_to(srcobj.get_headers()):
                raise Exception(name + ": header mismatch")
        else:
            if srcobj.get_headers():
                self.headers = srcobj.get_headers()

    # Grouping method.  Takes each row, traverses down the groups map, creating
    # new keys as it goes along, until it gets to the last group, where it either
    # creates or appends to an array of the rows for that group

    def __collect_groups(self, row, headers, idx):
        path = [group.eval(row) for group in self.group_expressions]
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

    def __sub__(self, other):
        my_data = self.groups or self.data
        their_data = other.groups or other.data
        my_keys = set( [key for key in my_data] )
        their_keys = set( [key for key in their_data] )

        new_table = Table({}, None)
        new_keys = my_keys - their_keys

        for key in new_keys:
            new_table.data[key] = self.data[key]

        return new_table
