class Expression:
    def __init__(self, expression):
        self.expression = expression
        setattr(self, 'round', self.__round)
        setattr(self, 'count', self.__count)
        setattr(self, 'as_var', self.__as_var)
        setattr(self, 'add_column', self.__add_column)
        setattr(self, 'as_percent', self.__as_percent)
        self.memoize_as = self.expression

    def eval(self, symbols, memo=None):
        for var in symbols:
            obj = self.__cast_type(symbols[var])
            setattr(self, var, obj)

        self.memo = memo
        self.symbols = symbols
        return eval(self.expression, self.__dict__)

    def __cast_type(self, value):
        value = value.replace(',', '')
        value = value.replace('%', '')

        try:
            return float(value)
        except:
            return value

    def __add_column(self, name, value):
        if not name in self.symbols:
            self.symbols[name] = value
            return {name: value}

    def __as_percent(self, denom, numerator):
        return (denom / numerator) * 100.0

    def __round(self, value, places=2):
        return str(round(value, places))

    def __count(self, filter=True):
        self.memo.setdefault(self.memoize_as, 0)

        if filter:
            self.memo[self.memoize_as] += 1

    def __as_var(self, varname, value):
        srckey = self.memoize_as
        if self.memoize_as != varname:
            self.memo[varname] = self.memo[srckey]
            self.memoize_as = varname
            del self.memo[srckey]

        setattr(self, varname, self.memo[varname])
