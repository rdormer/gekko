import datetime

class Expression:
    def __init__(self, expression):
        self.expression = expression
        setattr(self, 'round', self.__round)
        setattr(self, 'count', self.__count)
        setattr(self, 'add_column', self.__add_column)
        setattr(self, 'as_percent', self.__as_percent)
        setattr(self, 'accumulate', self.__accumulate)
        setattr(self, 'pluck', self.__pluck)
        setattr(self, 'datetime', datetime)
        self.counter = 0

    def eval(self, symbols, memo={}):
        for var in symbols:
            setattr(self, var, symbols[var])

        self.memo = memo
        self.symbols = symbols

        return eval(self.expression, self.__dict__)

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
        return round(value, places)

    def __count(self, filter=True):
        if filter:
            self.counter += 1
        return self.counter

    def __pluck(self, index, col):
        next_idx = self.memo.get('__idx', -1) + 1
        self.memo['__idx'] = next_idx

        if index == next_idx:
            self.memo[self.expression] = self.symbols[col]

        return self.memo[self.expression]
