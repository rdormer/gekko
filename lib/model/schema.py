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
            self.table = report.get_table

    def evaluate(self):
        if self.data:
            return

        self.__load_data()

        if 'each_row' in self.config:
            self.each_row(self.__row_evaluate, self.data)

        if 'template' in self.config:
            self.__eval_template()

    def __eval_template(self):
        new_data = None
        template = self.config['template']

        def recurse(row, template):
            if type(template) == dict:
                data = {}

                for key in template:
                    datakey = row.col(key)
                    subschema = template[key]
                    #data[datakey] = recurse(row, subschema)

                return data

            if type(template) == list:
                return template
                #import pdb; pdb.set_trace()

        def expand_template(row, memo):
            nonlocal template, new_data
            new_data = recurse(row, template)

        if type(template) == dict:
            new_data = {}
        else:
            new_data = []

        self.each_row(expand_template, self.data)
        import pdb; pdb.set_trace()


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

    def each_row(self, fn, data):
        memo = {}
        if type(data) == list:
            for entry in data:
                if type(entry) == Row:
                    fn(entry, memo)
                if type(entry) == list:
                    self.each_row(fn, entry)

        if type(data) == dict:
            for key in data:
                self.each_row(fn, data[key])
