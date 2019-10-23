import ctypes
import ctypes.util
import re
from caw_memory_editors import MacOSX, errors

BASE_WORLD_NAME = "Newcrest"

class ChangeWorldNames:
    def __init__(self, process):
        self.process = process
        self.mem_regions = process.all_regions()

    def run(self):
        base_world = self.find_a_world()
        print(base_world)

    def find_a_world(self):
        world_name_addrs = []
        for region in self.mem_regions:
            try:
                region_str = process.read_bytes(region.address.value, bytes=region.mapsize.value)
            except errors.CannotReadException:
                continue

            if BASE_WORLD_NAME in region_str:
                name_ocurrences = [m.start() for m in re.finditer(BASE_WORLD_NAME, region_str)]
                for name_loc in name_ocurrences:
                    world_name_addrs.append(region.address.value + name_loc)

        return self.filter_to_relevant_worlds(world_name_addrs)

    def filter_to_relevant_worlds(self, world_name_addrs):
        for addr in world_name_addrs:
            print(process.read_bytes(addr, bytes=len(BASE_WORLD_NAME) + 10))
        print(world_name_addrs)


process = MacOSX("The Sims 4")
change_names = ChangeWorldNames(process)
change_names.run()
