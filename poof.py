#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Poof: List and uninstall/remove macOS packages
# Copyright (c) 2011-2017 Rudá Moura <ruda.moura@gmail.com>
#

"""Poof is a command line utility to list and uninstall/remove macOS packages.

*NO WARRANTY* DON'T BLAME ME if you destroy your installation!
NEVER REMOVE com.apple.* packages unless you know what you are doing.

How it works:

It first removes all files and directories declared by the package and
then forget the metadata (the receipt data).

Usage:

List packages (but ignore all from Apple).

    $ ./poof.py | grep -v com.apple.pkg
    com.accessagility.wifiscanner
    com.adobe.pkg.FlashPlayer
    com.amazon.Kindle
    com.christiankienle.CoreDataEditor
    com.ea.realracing2.mac.bv
    com.google.pkg.GoogleVoiceAndVideo
    com.google.pkg.Keystone
    com.Growl.GrowlHelperApp
    com.lightheadsw.caffeine
    com.Logitech.Control Center.pkg
    ...

Remove FlashPlayer (com.adobe.pkg.FlashPlayer).

    $ sudo ./poof.py com.adobe.pkg.FlashPlayer
    ...
    Forgot package 'com.adobe.pkg.FlashPlayer' on '/'.
"""

from __future__ import print_function
from subprocess import Popen, PIPE
import sys
import os


class Shell(object):
    def __getattribute__(self, attr):
        return Command(attr)


class Command(object):
    def __init__(self, command):
        self.command = command

    def __call__(self, params=None):
        args = [self.command]
        if params:
            args += params.split()
        return self.run(args)

    def run(self, args):
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        out, err = out.strip(), err.strip()
        if sys.version_info >= (3, 0):
            out, err = str(out, 'utf-8'), str(err, 'utf-8')
        if p.returncode == 0:
            return True, out.split('\n')
        else:
            return False, err.split('\n')


def package_list():
    sh = Shell()
    sts, out = sh.pkgutil('--pkgs')
    return out


def package_info(package_id):
    sh = Shell()
    ok, info = sh.pkgutil('--pkg-info ' + package_id)
    if ok == False:
        raise IOError('Unknown package or name mispelled')
    info = [x.split(': ') for x in info]
    return dict(info)


def package_files(package_id):
    sh = Shell()
    ok, files = sh.pkgutil('--only-files --files ' + package_id)
    ok, dirs = sh.pkgutil('--only-dirs --files ' + package_id)
    # Guess AppStore receipt
    for dir in dirs:
        if dir.endswith('.app'):
            dirs.append(dir + '/Contents/_MASReceipt')
            files.append(dir + '/Contents/_MASReceipt/receipt')
            break
    return files, dirs


def package_forget(package_id):
    sh = Shell()
    ok, msg = sh.pkgutil('--verbose --forget ' + package_id)
    return msg


def package_remove(package_id, force=True, verbose=False):
    try:
        info = package_info(package_id)
    except IOError as e:
        print("%s: '%s'" % (e, package_id))
        return False
    prefix = info['volume']
    if info['location']:
        prefix += info['location'] + os.sep
    files, dirs = package_files(package_id)
    files = [prefix + x for x in files]
    clean = True
    for path in files:
        try:
            os.remove(path)
        except OSError as e:
            clean = False
            print(e)
    dirs = [prefix + x for x in dirs]
    if sys.version_info >= (3, 0):
        dirs_depth = sorted({(x.count('/'), x) for x in dirs}, key=lambda x: x[0], reverse=True)
        dirs = [x[1] for x in dirs_depth]
    else:
        dirs.sort(lambda p1, p2: p1.count('/') - p2.count('/'), reverse=True)
    for dir in dirs:
        try:
            os.rmdir(dir)
            if verbose:
                print('Removing', dir)
        except OSError as e:
            clean = False
            print(e)
    if force or clean:
        msg = package_forget(package_id)
        print(msg[0])
    return clean


def main(argv=None):
    if argv == None:
        argv = sys.argv
    if len(argv) == 1:
        for pkg in package_list():
            print(pkg)
    for arg in argv[1:]:
        package_remove(arg)
    return 0


if __name__ == '__main__':
    sys.exit(main())
