
import ctypes
from ctypes import c_int, c_ulong
import sys
import psutil
import os

def check_dllpath(dllpath):
    return os.path.exists(dllpath) 
    """ RETURNS A BOOL """

def getpid(pname):
    pid = None 
    for p in psutil.process_iter(attrs=['pid', 'name']):
        if p.info['name'] == pname:
            pid = p.info['pid']
            break 
    return pid

def mbox(title, msg):
    sys.stdout.write(" [*] Creating Message Box!")
    ctypes.windll.user32.MessageBoxW(0, msg, title, 0)

def inject(pid, dllpath):
    
    PAGE_READWRITE = 0x04
    PROCESS_ALL_ACCESS = ( 0x00F0000 | 0x00100000 | 0xFFF )
    VIRTUAL_MEM = ( 0x1000 | 0x2000 )

    kernel32 = ctypes.windll.kernel32
    dll_len = len(dllpath)

    hproc = kernel32.OpenProcess( PROCESS_ALL_ACCESS, False, int(pid) )

    if not hproc:
        mbox("Error :(", "Process Id is not valid, You sure this process exists? :(")
        sys.exit(0)

    """ Allocate space for the dll path """
    dll_addy = kernel32.VirtualAllocEx(hproc, 0, dll_len, 0, VIRTUAL_MEM, PAGE_READWRITE)
    sys.stdout.write("[*] Space has been allocated for the DLL")

    """ WRITE DLL TO ALLOCATED SPACE """
    written = c_int(0)
    kernel32.WriteProcessMemory(hproc, dll_addy, dllpath, dll_len, ctypes.byref(written))
    sys.stdout.write("[*] The DLL has been written to the allocated space.")

    """ RESOLVE LLA ADDRESS """
    h_kernel32 = kernel32.GetModuleHandleA("kernel32.dll")
    h_loadlib = kernel32.GetProcAddress(h_kernel32, "LoadLibraryA")
    sys.stdout.write("[*] Space has been allocated for the LLA.")

    thread_id = c_ulong

    if not kernel32.CreateRemoteThread(hproc, 0, h_loadlib, dll_addy, 0, ctypes.byref(thread_id)):
        mbox("Error", "Failed to Inject DLL. Exit :(")
        sys.stdout.write("*** ERROR CHECK MBOX ***")
        sys.exit(0)

    mbox("Success!", "DLL Was successfully injected.")

if __name__ == "__main__":

    procid = getpid("javaw.exe")
    dllpath = "C:/klumzi.dll"

    if check_dllpath(dllpath):
        pass 
    else:
        mbox("Error", "DLL Path does not exist :(")

    inject(procid, dllpath)