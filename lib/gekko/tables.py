NO_GROUP_KEY = '--none--'

class Table:
    def __init__(self, config, report):
        self.source = report.get_source
        self.table = report.get_table
        self.headers = None
        self.config = config
        self.groups = {}

    def evaluate(self):
        if not 'group' in self.config:
            self.groups[NO_GROUP_KEY] = []

        if 'table' in self.config:
            for table in self.config['table']:
                table_obj = self.table(table)
                table_obj.evaluate()
                self.set_headers_if(table_obj)
                self.append(table_obj)

        if 'source' in self.config:
            for source in self.config['source']:
                data = self.source(source)
                self.set_headers_if(data)

                if 'group' in self.config:
                    data.each_row(self.collect_groups)
                else:
                    data.each_row(self.append_row)

    def append(self, srctable):
        for group in srctable.groups:
            for row in srctable.groups[group]:
                if 'group' in self.config:
                    self.collect_groups(row, [], -1)
                else:
                    self.append_row(row, [], -1)

    def each_row(self, fn, data=None):
        data = data or self.groups

        if type(data) == list:
            for row in data:
                fn(row)
        else:
            for group in data:
                self.each_row(fn, data[group])

    def set_headers_if(self, srcobj):
        if not self.headers and srcobj.headers:
            self.headers = srcobj.headers

    # Grouping method.  Takes each row, traverses down the groups map, creating
    # new keys as it goes along, until it gets to the last group, where it either
    # creates or appends to an array of the rows for that group

    def collect_groups(self, row, headers, idx):
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

    def append_row(self, row, headers, idx):
        self.groups[NO_GROUP_KEY].append(row)

    def text(self, headers_to_print):
        self.evaluate()
        buffer = ''

        def row_fmt(row):
            nonlocal buffer
            filtered = self.headers.filter_tuple(row, headers_to_print)
            line = ''.join(str(x) + ',' for x in filtered)
            buffer += line[:-1] + "\n"

        self.each_row(row_fmt)
        return buffer
