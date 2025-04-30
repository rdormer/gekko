class Row:
    def __init__(self, data):
        self.data = data

    def to_h(self):
        return self.data

    def col(self, col):
        return self.data[col]
