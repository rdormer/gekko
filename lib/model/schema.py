from lib.expr.expression import Expression
from lib.model.headers import HeaderSet
from lib.model.row import Row

class Schema:
    def __init__(self, config, report):
        self.sortdir = config.get('desc', False)

        self.headers = None
        self.config = config
        self.data = []

        if report != None:
            self.source = report.get_source

    def evaluate(self):
        if self.data:
            return

        self.__load_data()

        if 'each_row' in self.config:
            memo = {}
            for row in self.data:
                self.__row_evaluate(row, memo, 'each_row')

        if 'row_filter' in self.config:
            self.data[:] = self.__filter_rows(self.data, self.config['row_filter'])

        if 'template' in self.config:
            self.__eval_template()

        if 'after_grouping' in self.config:
            self.each_row(lambda row, memo: self.__row_evaluate(row, memo, 'after_grouping'))

    def get_headers(self):
        cols = self.config.get('columns')
        rval = self.headers

        if cols:
            rval = HeaderSet(self.config)
            line = [ cols ]
            rval.handle_headers(line)

        return rval

    def __eval_template(self):
        self.data = self.__expand_dict_template(self.config['template'], self.data)

    def __expand_eval_template(self, template, rows):
        sortdir = template['eval'].get('desc', False)
        data = {}

        local_keys = [x for x in list(template['eval']) if x not in ['data', 'desc', 'slice', 'filter']]
        local_data = {}

        for key in local_keys:
            expr = Expression(template['eval'][key])
            memo = {}

            for row in rows:
                local_data[key] = expr.eval(row.to_h() | local_data, memo)

        if 'filter' in template['eval']:
            rows = self.__filter_rows(rows, template['eval']['filter'])

        if 'slice' in template['eval']:
            self.__slice_data(template['eval']['slice'], rows, local_data)

        data['meta'] = Row(local_data)

        if 'data' in template['eval']:
            sub_template = template['eval']['data']

            if type(sub_template) == dict:
                data['data'] = self.__expand_dict_template(sub_template, rows, sortdir)

            if type(sub_template) == list:
                data['data'] = self.__expand_list_template(sub_template, rows)

        return data

    def __expand_dict_template(self, template, rows, desc_sort=False):
        data = {}

        if 'eval' in template:
            data['eval'] = self.__expand_eval_template(template, rows)
        else:
            for template_key in template:
                raw_data = {}
                row_exp = Expression(template_key)

                for row in rows:
                    row_key = row_exp.eval(row.to_h())
                    raw_data.setdefault(row_key, [])
                    raw_data[row_key].append(row)

                for key in sorted(raw_data.keys(), reverse=desc_sort):
                    sub_template = template[template_key]
                    if type(sub_template) == dict:
                        data[key] = self.__expand_dict_template(sub_template, raw_data[key])

                    if type(sub_template) == list:
                        data[key] = self.__expand_list_template(sub_template, raw_data[key])

        return data

    def __expand_list_template(self, template, rows):
        data = []
        for row in rows:
            for item in template:
                if item == '*':
                    data.append(row)
                else:
                    raise 'subarray not implemented yet'

        return data

    def __slice_data(self, exprs, data, locals):
        self.headers.add_column('slice')
        predicates = [Expression(expr) for expr in exprs]
        slindex = 0

        for row in data:
            predflag = False
            for predicate in predicates:
                predflag = predicate.eval(row.to_h() | locals)
                if not predflag:
                    break

            if predflag:
                slindex += 1

            row.to_h()['slice'] = slindex

    def __load_data(self):
        if 'sources' in self.config:
            for source in self.config['sources']:
                data = self.source(source)
                self.__set_or_validate_headers(data, source)
                data.each_row(self.__load_row)

    def __set_or_validate_headers(self, srcobj, name):
        if self.headers:
            if not self.headers.equal_to(srcobj.get_headers()):
                raise Exception(name + ": header mismatch")
        else:
            if srcobj.get_headers():
                self.headers = srcobj.get_headers()

    def __load_row(self, row, headers, idx):
        self.data.append(Row(row))

    def __row_evaluate(self, row, memo, target):
        for expr in self.config[target]:
            changes = Expression(expr).eval(row.to_h(), memo)
            for newcol in changes:
                self.headers.add_column(newcol)

    def each_row(self, fn, filter=None):
        def row_iter(fn, data, memo):
            if type(data) == list:
                for entry in data:
                    if type(entry) == Row:
                        if filter == None or entry.has_cols(filter):
                            fn(entry, memo)
                    if type(entry) == list:
                        row_iter(fn, entry)

            if type(data) == dict:
                for key in data:
                    row_iter(fn, data[key], memo)

            if type(data) == Row:
                if filter == None or data.has_cols(filter):
                    fn(data, memo)

        row_iter(fn, self.data, {})

    def __filter_rows(self, indata, filter_predicates):
        filter_expressions = [Expression(exp) for exp in filter_predicates]

        def filter(data):
            if type(data) == dict:
                for key in data:
                    filter(data[key])

            if type(data) == list:
                def predicate(row):
                    for filter in filter_expressions:
                        if filter.eval(row.to_h()):
                            return False

                    return True

                return [x for x in data if predicate(x)]

        return filter(indata)

    def __sub__(self, other):
        my_data = self.data
        their_data = other.data
        my_keys = set( [key for key in my_data] )
        their_keys = set( [key for key in their_data] )

        new_schema = Schema({}, None)
        new_schema.data = {}

        new_keys = my_keys - their_keys
        for key in sorted(new_keys):
            new_schema.data[key] = self.data[key]

        return new_schema
