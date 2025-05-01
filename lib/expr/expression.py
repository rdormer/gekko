import datetime

class Expression:
    def __init__(self, expression):
        self.expression = expression
        setattr(self, 'round', self.__round)
        setattr(self, 'count', self.__count)
        setattr(self, 'as_var', self.__as_var)
        setattr(self, 'add_column', self.__add_column)
        setattr(self, 'as_percent', self.__as_percent)
        setattr(self, 'accumulate', self.__accumulate)
        setattr(self, 'datetime', datetime)
        self.counter = 0

    def eval(self, symbols, memo={}):
        for var in symbols:
            obj = self.__cast_type(symbols[var])
            setattr(self, var, obj)
            symbols[var] = obj

        self.memo = memo
        self.symbols = symbols
        return eval(self.expression, self.__dict__)

    # TO DO: remove this once table is fully deprecated
    def __cast_type(self, value):
        if type(value) != str:
            return value

        value = value.replace(',', '')
        value = value.replace('%', '')

        try:
            return int(value)
        except:
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

    def __accumulate(self, name):
        if not self.memo.get(self.expression, False):
            self.memo[self.expression] = 0.0

        current = float(self.symbols[name])
        self.memo[self.expression] += current
        return self.memo[self.expression]

    def __round(self, value, places=2):
        return str(round(value, places))

    def __count(self, filter=True):
        if filter:
            self.counter += 1
        return self.counter

    def __as_var(self, varname, value):
        self.symbols[varname] = value
        setattr(self, varname, self.symbols[varname])
