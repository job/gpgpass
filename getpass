#!/usr/bin/python

# Required: sudo apt-get install python-git python-gnupg

import os
import argparse
import sys
import signal
from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser
import stat

try:
    import gnupg
except ImportError:
    print "ERROR Missing python-gnupg"
    print "Run: easy_install gnupg"
    exit(1)

try:
    import git
except ImportError:
    print "ERROR Missing python-git"
    print "Run: easy_install GitPython"
    exit(1)

def init():
    global cfg
    cfg = SafeConfigParser()
    cfgdir = os.path.join(os.path.expanduser("~"), '.getpass')

    if not os.path.isdir(cfgdir):
        print "Creating %s" % cfgdir
        os.mkdir(cfgdir, 0700)
    else:
        # Ensure proper permissions
        os.chmod(cfgdir, 0700)
          
    if os.path.isfile(os.path.join(cfgdir, 'config.ini')):
        cfg.read(os.path.join(cfgdir, 'config.ini'))

    else:
        # Create a default config.ini
        cfg.add_section('Passwords')
        cfg.set('Passwords', 'passwordsRepository', os.path.join(os.path.expanduser("~"), '.getpass', 'gpg-passwords'))
        cfg.set('Passwords', 'passwordsRepositoryRemote', "")
        cfg.set('Passwords', 'passwordsSyncInterval', '30')

        cfg.add_section('AutomaticUpdate')
        cfg.set('AutomaticUpdate', 'automaticUpdate', 'True')
        cfg.set('AutomaticUpdate', 'automaticUpdateInterval', '1440')

        with open(os.path.join(cfgdir, 'config.ini'), 'wb') as fh:
            cfg.write(fh)

    passwordsRepository = cfg.get('Passwords', 'passwordsRepository')
    passwordsRepositoryRemote = cfg.get('Passwords', 'passwordsRepositoryRemote')
    passwordsSyncInterval = int(cfg.get('Passwords', 'passwordsSyncInterval'))
    automaticUpdate = cfg.get('AutomaticUpdate', 'automaticUpdate')
    automaticUpdateInterval = int(cfg.get('AutomaticUpdate', 'automaticUpdateInterval'))
    
    if automaticUpdate:
        updateRepository(os.path.dirname(os.path.realpath(__file__)), automaticUpdateInterval)

    # Create directory to hold passwords and this script
    if not os.path.isdir(passwordsRepository):
        try:
            os.makedirs(passwordsRepository, 0700)
        except StandardError, e:
            print "Unable to create the path '%s': %s.\nCreate the path manually (remember permissions) or change the passwordsRepository setting." % (passwordsRepository, e)
            sys.exit(1)

    # Ensure correct permissions
    os.chmod(passwordsRepository, 0700)

    # Pull the latest version of password files
    if passwordsRepositoryRemote != "":
        updateRepository(passwordsRepository, passwordsSyncInterval, True)
    else:
        print "WARNING: A remote password repository has not been defined. Edit %s and set passwordsrepositoryremote." % (os.path.join(cfgdir, 'config.ini'))

def updateRepository(repositoryDirectory, interval, repositoryRemote = None):

    if os.path.isdir(os.path.join(repositoryDirectory, ".git")):
        # Repo has been cloned before, pull latest changes, but only if more then passwordsSyncInterval minutes ago
        doSync = False
        if os.path.isfile(os.path.join(repositoryDirectory, ".git", "FETCH_HEAD")): # File doesn't exist when a fetch hasn't happened yet
            mtime = os.stat(os.path.join(repositoryDirectory, ".git", "FETCH_HEAD"))[stat.ST_MTIME]
            lastdt = datetime.fromtimestamp(mtime)
            if datetime.now() - lastdt > timedelta(minutes=interval):
                doSync = True
        else:
            doSync = True

        if doSync:
            pwrepo = git.Repo(repositoryDirectory)
            print "Fetching latest changes from GIT remote '%s'." % (pwrepo.remotes.origin.url)
            pwrepo.remotes.origin.pull()

    elif repositoryRemote != None:
        print "GIT Repository not initialised, cloning from '%s'." % (repositoryRemote)
        git.Repo.clone_from(repositoryRemote, repositoryDirectory)
    else:
        print "Unable to automatically update '%s', it is not a GIT repository." % repositoryDirectory

def seachThruFiles(searchText, showFullFile):
    global cfg
    gpg = gnupg.GPG(use_agent=True)

    # Iterate over all files in directories in passwordsRepository
    for root, dirs, files in os.walk(cfg.get('Passwords', 'passwordsRepository')):
        if not root.endswith(".git"):
            for name in files:
                # Try to decode the file with gpg
                quitAfterDisplay = False
                if name.lower() == searchText.lower():
                    searchText = ""
                    quitAfterDisplay = True

                try:
                    with open(os.path.join(root, name)) as fh:
                        decrypted_data = gpg.decrypt_file(fh)
                    
                        if not quitAfterDisplay:
                            namePrinted = False
                            for line in str(decrypted_data).splitlines():
                                if searchText.lower() in line.lower():
                                    if not namePrinted:
                                        print "---------- %s ----------" % name
                                        namePrinted = True
                                    if showFullFile:
                                        print str(decrypted_data)
                                    else:
                                        print line

                            if namePrinted:
                                print "\n"
                        else:
                            content = str(decrypted_data)
                            print "---------- %s ----------" % name
                            print content
                            print "\n"
                except StandardError, e:
                    print "Error decrypting %s: %s" % (os.path.join(root, name), e)

                if quitAfterDisplay:
                    sys.exit(0)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search thru GPG encrypted password files.')
    parser.add_argument("searchText", help='Scan decrypted GPG files for this text.')
    parser.add_argument("-f", help='Show the entire file when a match is found.', dest='showFullFile', action='store_true')
    args = parser.parse_args()

    init()
    seachThruFiles(args.searchText, args.showFullFile)
