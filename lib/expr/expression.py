import datetime
import re

class Expression:
    def __init__(self, expression):
        self.expression = expression
        setattr(self, 'max', self.__max)
        setattr(self, 'min', self.__min)
        setattr(self, 'round', self.__round)
        setattr(self, 'count', self.__count)
        setattr(self, 'pluck', self.__pluck)
        setattr(self, 'add_column', self.__add_column)
        setattr(self, 'as_percent', self.__as_percent)
        setattr(self, 'accumulate', self.__accumulate)
        setattr(self, 'crossover', self.__crossover)
        setattr(self, 'datetime', datetime)
        setattr(self, 're', re)
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
        self.__getset_memo_value(0.0)

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

    def __max(self, value):
        self.__getset_memo_value(value)
        if value > self.memo[self.expression]:
            self.memo[self.expression] = value

        return self.memo[self.expression]

    def __min(self, value):
        self.__getset_memo_value(value)
        if value < self.memo[self.expression]:
            self.memo[self.expression] = value

        return self.memo[self.expression]

    def __crossover(self, value, target):
        previous_value = self.memo.get(self.expression, value)
        self.memo[self.expression] = value
        return (previous_value <= target and value > target) or (previous_value >= target and value < target)

    def __getset_memo_value(self, value):
        if not self.memo.get(self.expression, False):
            self.memo[self.expression] = value
