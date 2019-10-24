import ctypes
import ctypes.util
import re
import struct
from caw_memory_editors import MacOSX, CannotReadException

BASE_WORLD_NAME = "Von Haunt Estate".encode('utf-8')
REPLACE_WORLD_NAME = "Apple Fritters are tasty".encode('utf-8')

class ChangeWorldNames:
    def __init__(self, process):
        self.process = process

    def run(self):
        # self.find_lots()

        a = self.process.allocate_bytes(len(BASE_WORLD_NAME)+1)
        b = self.process.allocate_bytes(len(REPLACE_WORLD_NAME)+1)
        self.process.write_bytes(a.value, ctypes.create_string_buffer(BASE_WORLD_NAME + b'\x00'), len(BASE_WORLD_NAME)+1)
        self.process.write_bytes(b.value, ctypes.create_string_buffer(REPLACE_WORLD_NAME + b'\x00'), len(REPLACE_WORLD_NAME)+1)

        print(a, a.value, self.process.read_bytes(a.value, bytes=8))
        print(b, b.value, self.process.read_bytes(b.value, bytes=8))

        b.value = a.value

        print(a, a.value, self.process.read_bytes(a.value, bytes=8))
        print(b, b.value, self.process.read_bytes(b.value, bytes=8))

    def find_lots(self):
        potential_lot_addrs = self.process.find_in_memory(BASE_WORLD_NAME)
        return self.filter_to_relevant_lots(potential_lot_addrs)

    def filter_to_relevant_lots(self, lot_addrs):
        mem_regions = self.process.all_regions()

        replace_addr = self.process.allocate_bytes(len(REPLACE_WORLD_NAME)+1)
        self.process.write_bytes(replace_addr.value, ctypes.create_string_buffer(REPLACE_WORLD_NAME + b'\x00'), len(REPLACE_WORLD_NAME)+1)
        replace_addr_bytes = struct.pack('L', replace_addr.value)

        refs_to_name = []
        for addr in lot_addrs:
            print(addr)
            addr_bytes = struct.pack('L', addr)
            refs_to_name += self.process.find_in_memory(addr_bytes, mem_regions=mem_regions)
            print("HMMM: " + str(struct.pack('L', addr)) + " - " + str(len(struct.pack('L', addr))) + " - " + str(refs_to_name))

        print(refs_to_name)
        print(replace_addr_bytes)
        print(len(replace_addr_bytes))

        for ref_addr in refs_to_name:
            print("\n--1-----\n{}\n---1-----\n".format(self.process.read_bytes(ref_addr, bytes=len(replace_addr_bytes))))
            self.process.write_bytes(ref_addr, ctypes.create_string_buffer(replace_addr_bytes), len(replace_addr_bytes))
            print("\n---2----\n{}\n---2-----\n".format(self.process.read_bytes(ref_addr, bytes=len(replace_addr_bytes))))


sims_process = MacOSX("The Sims 4")
change_names = ChangeWorldNames(sims_process)
change_names.run()
