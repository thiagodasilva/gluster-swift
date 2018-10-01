# Simple program to save all package information
# into a file which can be sourced by a bash script

from nas_connector import _pkginfo as pkginfo

PKGCONFIG = 'pkgconfig.in'

pkginfo.save_config(PKGCONFIG)
