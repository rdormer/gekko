class Expression:
    def __init__(self, expression):
        self.expression = expression
        setattr(self, 'round', self.__round)
        setattr(self, 'add_column', self.__add_column)
        setattr(self, 'as_percent', self.__as_percent)

    def eval(self, symbols):
        for var in symbols:
            obj = self.__cast_type(symbols[var])
            setattr(self, var, obj)

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
