class Row:
    def __init__(self, data):
        self.data = {}
        for key in data:
            self.data[key] = self.__cast_type(data[key])

    def to_h(self):
        return self.data

    def col(self, col):
        return self.data[col]

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
