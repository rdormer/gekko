NO_GROUP_KEY = '--none--'

class Table:
    def __init__(self, config, report):
        self.source = report.get_source
        self.table = report.get_table
        self.config = config
        self.groups = {}

    def evaluate(self):
        if 'table' in self.config:
            for table in self.config['table']:
                self.table(table).evaluate()

        if 'source' in self.config:
            for source in self.config['source']:
                data = self.source(source)

                if 'group' in self.config:
                    data.each_row(self.collect_groups)
                else:
                    self.groups[NO_GROUP_KEY] = []
                    data.each_row(self.append_row)

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

    def text(self, columns_to_print):
        self.evaluate()
        headers = self.header_indices(columns_to_print)
        return self.print_groups(self.groups, headers)

    def rows_to_text(self, group, headers):
        buf = ''
        for row in group:
            line = ''.join(str(row[idx]) + ',' for idx in headers)
            line = line[:-1] + "\n"
            buf += line

        return buf

    # look for headers from one of our sources, otherwise defer
    # to one of our child tables to get them

    def header_indices(self, columns_to_print):
        if 'source' in self.config:
            for current in self.config['source']:
                mysource = self.source(current)
                return mysource.header_indices(columns_to_print)

        if 'table' in self.config:
            for current in self.config['table']:
                mytable = self.table(current)
                return mytable.header_indices(columns_to_print)

    def print_groups(self, groups, headers):
        if isinstance(groups, dict):
            return ''.join(self.print_groups(groups[group], headers) for group in groups)
        else:
            return self.rows_to_text(groups, headers)
