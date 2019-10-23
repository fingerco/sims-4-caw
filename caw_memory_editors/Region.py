class Region:
    def __init__(self, address, mapsize, name, count, info):
        self.address = address
        self.mapsize = mapsize
        self.name = name
        self.count = count
        self.info = info

    def __str__(self):
        return "Region({}, {}, {}, {}, {})".format(
            self.address.value,
            self.mapsize.value,
            self.name.value,
            self.count.value,
            self.info
        )
