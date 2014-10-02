#!/usr/bin/env python
import os
import argparse
import sys
from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser
import stat


try:
    import gnupg
except ImportError:
    print "ERROR Missing python-gnupg"
    print "Run: easy_install gnupg"
    sys.exit(2)

try:
    import git
except ImportError:
    print "ERROR Missing python-git"
    print "Run: easy_install git"
    sys.exit(2)


def init(configDir, passwordsRepository):
    global cfg
    cfg = SafeConfigParser()

    if not os.path.isdir(configDir):
        print "Creating %s" % configDir
        os.mkdir(configDir, 0700)
    else:
        # Ensure proper permissions
        os.chmod(configDir, 0700)

    if os.path.isfile(os.path.join(configDir, 'config.ini')):
        cfg.read(os.path.join(configDir, 'config.ini'))

    else:
        # Create a default config.ini
        cfg.add_section('Passwords')
        cfg.set('Passwords', 'passwordsRepository', passwordsRepository)
        cfg.set('Passwords', 'passwordsRepositoryRemote', "")
        cfg.set('Passwords', 'passwordsSyncInterval', '30')

        with open(os.path.join(configDir, 'config.ini'), 'wb') as fh:
            cfg.write(fh)

    passwordsRepository = cfg.get('Passwords', 'passwordsRepository')
    passwordsRepositoryRemote = cfg.get('Passwords',
                                        'passwordsRepositoryRemote')
    passwordsSyncInterval = int(cfg.get('Passwords',
                                        'passwordsSyncInterval'))

    # Create directory to hold passwords and this script
    if not os.path.isdir(passwordsRepository):
        try:
            os.makedirs(passwordsRepository, 0700)
        except:
            print "Unable to create the path '%s': %s.\nCreate the path \
manually (remember permissions) or change the passwordsRepository \
setting." % (passwordsRepository, 'fo')
            sys.exit(1)

    # Ensure correct permissions
    os.chmod(passwordsRepository, 0700)

    # Pull the latest version of password files
    if passwordsRepositoryRemote != "":
        updateRepository(passwordsRepository, passwordsSyncInterval,
                         passwordsRepositoryRemote)
    else:
        print "WARNING: A remote password repository has not been defined. \
Edit %s and set passwordsrepositoryremote." \
            % (os.path.join(configDir, 'config.ini'))

    return True


def updateRepository(repositoryDirectory, interval, repositoryRemote=None):

    if os.path.isdir(os.path.join(repositoryDirectory, ".git")):
        # Repo has been cloned before, pull latest changes, but only if
        # more then passwordsSyncInterval minutes ago
        doSync = False
        # File doesn't exist when a fetch hasn't happened yet
        if os.path.isfile(os.path.join(repositoryDirectory, ".git", "FETCH_HEAD")):
            mtime = os.stat(os.path.join(repositoryDirectory, ".git", "FETCH_HEAD"))[stat.ST_MTIME]
            lastdt = datetime.fromtimestamp(mtime)
            if datetime.now() - lastdt > timedelta(minutes=interval):
                doSync = True
        else:
            doSync = True

        if doSync:
            pwrepo = git.Repo(repositoryDirectory)
            print "Fetching latest changes from GIT remote '%s'." \
                % (pwrepo.remotes.origin.url)
            pwrepo.remotes.origin.pull()

        return 1

    elif repositoryRemote is not None:
        print "GIT Repository not initialised, cloning from '%s'." \
            % (repositoryRemote)
        git.Repo.clone_from(repositoryRemote, repositoryDirectory)
        return 2
    else:
        raise StandardError("Unable to automatically update '%s', \
it is not a GIT repository." % repositoryDirectory)


def searchThruFiles(searchText, showFullFile, GnuPGHome=None):
    global cfg
    gpg = gnupg.GPG(use_agent=True, gnupghome=GnuPGHome)

    # Iterate over all files in directories in passwordsRepository
    for root, dirs, files in os.walk(cfg.get('Passwords', 'passwordsRepository')):
        if root.endswith(".git"):
            continue
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

    return True


def parse_args(arguments=None):

    parser = argparse.ArgumentParser(description='Search thru GPG encrypted password files.')
    parser.add_argument("searchText",
                        help='Scan decrypted GPG files for this text.')
    parser.add_argument("-f",
                        help='Show the entire file when a match is found.',
                        dest='showFullFile', action='store_true')
    args = parser.parse_args(arguments)

    return args


def main():
    args = parse_args()
    init(os.path.join(os.path.expanduser("~"), '.gpgpass'),
         os.path.join(os.path.expanduser("~"), '.gpgpass', 'gpg-passwords'))
    searchThruFiles(args.searchText, args.showFullFile)

if __name__ == "__main__":
    main()
