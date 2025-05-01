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
            self.each_row(self.__row_evaluate)

        if 'row_filter' in self.config:
            self.__filter_rows()

        if 'template' in self.config:
            self.__eval_template()

    def get_headers(self):
        cols = self.config.get('columns')
        rval = self.headers

        if cols:
            rval = HeaderSet(self.config)
            line = [ cols ]
            rval.handle_headers(line)

        return rval

    def __eval_template(self):

        def go_down(row, template, data):
            if type(template) == dict:
                for key in template:
                    subschema = template[key]
                    datakey = row.col(key)

                    if datakey not in data:
                        if type(subschema) == dict:
                            data[datakey] = {}
                        else:
                            data[datakey] = []

                    go_down(row, subschema, data[datakey])

            if type(template) == list:
                for item in template:
                    if item == '*':
                        data.append(row)
                    else:
                        raise 'subarray not implemented yet'

        def expand_template(row, memo):
            nonlocal template, new_data
            go_down(row, template, new_data)

        new_data = None
        template = self.config['template']

        if type(template) == dict:
            new_data = {}
        else:
            new_data = []

        self.each_row(expand_template)
        self.data = new_data

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

    def __row_evaluate(self, row, memo):
        for expr in self.config['each_row']:
            changes = Expression(expr).eval(row.to_h(), memo)
            for newcol in changes:
                self.headers.add_column(newcol)

    def each_row(self, fn):

        def row_iter(fn, data):
            memo = {}
            if type(data) == list:
                for entry in data:
                    if type(entry) == Row:
                        fn(entry, memo)
                    if type(entry) == list:
                        row_iter(fn, entry)

            if type(data) == dict:
                for key in data:
                    row_iter(fn, data[key])

        row_iter(fn, self.data)

    def __filter_rows(self):
        def predicate(row):
            for filter in self.config['row_filter']:
                if Expression(filter).eval(row.to_h()):
                    return False

            return True

        filtered = [x for x in self.data if predicate(x)]
        self.data = filtered

    def __sub__(self, other):
        my_data = self.data
        their_data = other.data
        my_keys = set( [key for key in my_data] )
        their_keys = set( [key for key in their_data] )

        new_schema = Schema({}, None)
        new_schema.data = {}

        new_keys = my_keys - their_keys
        for key in new_keys:
            new_schema.data[key] = self.data[key]

        return new_schema
