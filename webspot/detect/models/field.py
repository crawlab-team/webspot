class Field(dict):
    @property
    def name(self):
        return self.get('name')

    @property
    def selector(self):
        return self.get('selector')
