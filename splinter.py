import archinstall
import time
import logging


# Log various information about hardware before starting the installation. This might assist in troubleshooting
archinstall.log(f"Hardware model detected: {archinstall.sys_vendor()} {archinstall.product_name()}; UEFI mode: {archinstall.has_uefi()}", level=logging.DEBUG)
archinstall.log(f"Processor model detected: {archinstall.cpu_model()}", level=logging.DEBUG)
archinstall.log(f"Memory statistics: {archinstall.mem_available()} available out of {archinstall.mem_total()} total installed", level=logging.DEBUG)
archinstall.log(f"Virtualization detected: {archinstall.virtualization()}; is VM: {archinstall.is_vm()}", level=logging.DEBUG)
archinstall.log(f"Graphics devices detected: {archinstall.graphics_devices().keys()}", level=logging.DEBUG)

# For support reasons, we'll log the disk layout pre installation to match against post-installation layout
archinstall.log(f"Disk states before installing: {archinstall.disk_layouts()}", level=logging.DEBUG)

# TODO prompt user for disk or autodetect

# TODO load splinter config defaults

mountpoint = "/mnt/archinstall"

def perform_filesystem_operations():
    if archinstall.arguments.get('harddrives', None):
        print(f" ! Formatting {archinstall.arguments['harddrives']} in ", end='')
        

def execute_installation(mountpoint):

    with archinstall.Installer(mountpoint, kernels=["linux"]) as installation:
        for partition in installation.partitions:
            if partition.size < 0.19:
                raise archinstall.DiskError(f"The selected /boot partition is not large enough to properly install the bootloader. Please resize it to at least 200MiB")
            
        installation.log('Waiting for automatic mirror selection (reflector) to complete', level=logging.INFO)
        while archinstall.service_state('reflector') not in ('dead', 'failed'):
            time.sleep(1)
            
        archinstall.SysCommand('timedatectl set-ntp true')
        
        logged = False
        while archinstall.service_state('dbus-org.freedesktop.timesync1.service') not in ('running'):
            if not logged:
                installation.log(f"Waiting for dbus-org.freedesktop.timesync1.service to enter running state", level=logging.INFO)
                logged = True
                
            time.sleep(1)
        
        logged = False
        while 'Server: n/a' in archinstall.SysCommand('timedatectl timesync-status --no-pager --property=Server --value'):
            if not logged:
                installation.log(f"Waiting for timedatectl timesync-status to report a timesync against a server", level=logging.INFO)
                logged = True
                
            time.sleep(1)
            
    archinstall.use_mirrors(archinstall.arguments['mirror-region']) 

    enable_testing = True
    enable_multilib = True
    
    if installation.minimal_installation(testing=True, multilib=True, hostname="splinter", locales=[f"{archinstall.arguments['sys-language']} {archinstall.arguments['sys-encoding'].upper()}"]):
        installation.set_mirrors(archinstall.arguments['mirror-region'])
        installation.setup_swap('zram')
        installation.add_additional_packages("grub")
        
        