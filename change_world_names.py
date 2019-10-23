import ctypes
import ctypes.util
import re
from caw_memory_editors import MacOSX, errors

BASE_WORLD_NAME = "Newcrest".encode('utf-16be')
REPLACE_WORLD_NAME = "Piecrust".encode('utf-16be')

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
                region_bytes = self.process.read_bytes(region.address.value, bytes=region.mapsize.value)
            except errors.CannotReadException:
                continue

            found = None
            last_found = -1
            while found != -1:
                found = region_bytes.find(BASE_WORLD_NAME, last_found+1)
                if found != -1:
                    world_name_addrs.append(region.address.value + found)
                    last_found = found

        return self.filter_to_relevant_worlds(world_name_addrs)

    def filter_to_relevant_worlds(self, world_name_addrs):
        for addr in world_name_addrs:
            print("\n--1-----\n{}\n---1-----\n".format(self.process.read_bytes(addr, bytes=len(BASE_WORLD_NAME)).decode('utf-16be')))
            self.process.write_bytes(addr, ctypes.create_string_buffer(REPLACE_WORLD_NAME), len(REPLACE_WORLD_NAME))
            print("\n---2----\n{}\n---2-----\n".format(self.process.read_bytes(addr, bytes=len(BASE_WORLD_NAME)).decode('utf-16be')))


sims_process = MacOSX("The Sims 4")
change_names = ChangeWorldNames(sims_process)
change_names.run()
