class Set:
    def __init__(self, config, report):
        self.table = report.get_table
        self.set = report.get_set
        self.config = config
        self.groups = {}

    def evaluate(self):
        if 'sets' in self.config:
            for subset in self.config['sets']:
                self.set(subset).evaluate()

        if 'table' in self.config:
            data = self.table(self.config['table'])

            if 'group' in self.config:
                data.each_row(self.collect_groups)

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


    def text(self):
        self.evaluate()
        return self.print_groups(self.groups)

    def rows_to_text(self, group):
        buf = ''
        for row in group:
            buf += ''.join(str(x) + ',' for x in row)
            buf += "\n"
        return buf

    def print_groups(self, groups):
        if isinstance(groups, dict):
            return ''.join(self.print_groups(groups[group]) for group in groups)
        else:
            return self.rows_to_text(groups)
