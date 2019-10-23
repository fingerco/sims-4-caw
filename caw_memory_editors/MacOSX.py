import os
import ctypes
import ctypes.util
import subprocess
from .errors import CannotAttachException, CannotReadException, InvalidAddressException
from .Region import Region

libc = ctypes.CDLL(ctypes.util.find_library('c'))

# Based on https://github.com/n1nj4sec/memorpy/blob/master/memorpy/OSXProcess.py
class vm_region_basic_info_64(ctypes.Structure):
    _fields_ = [
        ('protection',      ctypes.c_uint32),
        ('max_protection',  ctypes.c_uint32),
        ('inheritance',     ctypes.c_uint32),
        ('shared',          ctypes.c_uint32),
        ('reserved',        ctypes.c_uint32),
        ('offset',          ctypes.c_ulonglong),
        ('behavior',        ctypes.c_uint32),
        ('user_wired_count',ctypes.c_ushort),
]

VM_REGION_BASIC_INFO_64    = 9
VM_REGION_BASIC_INFO_COUNT_64 = ctypes.sizeof(vm_region_basic_info_64) / 4

VM_PROT_READ    = 1
VM_PROT_WRITE    = 2
VM_PROT_EXECUTE    = 4

class MacOSX:
    def __init__(self, pid_or_name):
        try:
            self.pid = int(pid_or_name)
        except ValueError:
            pid_list = os.popen("ps -A | grep \"%s\" | awk '{print $1}'" % pid_or_name).read()
            lines = pid_list.split("\n")

            if len(lines) <= 1:
                # It is just our own grep command
                raise ProcessNotFound("Process '{}' not found".format(pid_or_name))

            self.pid = int(lines[0])

        self.my_task = libc.mach_task_self()
        self.task = ctypes.c_uint32()

        ret = libc.task_for_pid(self.my_task, ctypes.c_int(self.pid), ctypes.pointer(self.task))
        if ret != 0:
            raise CannotAttachException("task_for_pid failed with error code: {}".format(ret))

    def all_regions(self):
        regions = []
        curr_region = 0

        while True:
            try:
                regions.append(self.get_region(curr_region))
                curr_region += 1

            except InvalidAddressException:
                break

        return regions


    def get_region(self, region_num=0):
        address = ctypes.c_ulong(0)
        mapsize = ctypes.c_ulong(0)
        name    = ctypes.c_uint32(0)
        count   = ctypes.c_uint32(VM_REGION_BASIC_INFO_COUNT_64)
        info    = vm_region_basic_info_64()

        for curr_region in range(0, region_num):
            ret = libc.mach_vm_region(self.task, ctypes.pointer(address),
                                       ctypes.pointer(mapsize), VM_REGION_BASIC_INFO_64,
                                       ctypes.pointer(info), ctypes.pointer(count),
                                       ctypes.pointer(name))

            if ret == 1:
                raise InvalidAddressException("mach_vm_region (region {}) returned: {}".format(curr_region, ret))
            elif ret != 0:
                raise CannotReadException("mach_vm_region (region {}) returned: {}".format(curr_region, ret))

            if curr_region < region_num:
                address.value += mapsize.value


        return Region(
            address=address,
            mapsize=mapsize,
            name=name,
            count=count,
            info=info
        )


    def read_bytes(self, address, bytes = 4):
        pdata = ctypes.c_void_p(0)
        data_cnt = ctypes.c_uint32(0)

        ret = libc.mach_vm_read(self.task, ctypes.c_ulonglong(address), ctypes.c_longlong(bytes), ctypes.pointer(pdata), ctypes.pointer(data_cnt));

        if ret != 0:
            raise CannotReadException("mach_vm_read returned: {}".format(ret))

        buf=ctypes.string_at(pdata.value, data_cnt.value)
        libc.vm_deallocate(self.my_task, pdata, data_cnt)
        return buf
