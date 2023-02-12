class Field(dict):
    @property
    def name(self):
        return self.get('name')

    @property
    def selector(self):
        return self.get('selector')

    @property
    def type(self):
        return self.get('type')

    @property
    def attribute(self):
        return self.get('attribute')
