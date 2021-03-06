# Gpgpass
[![Build Status](https://travis-ci.org/rvdh/gpgpass.svg?branch=master)](https://travis-ci.org/rvdh/gpgpass)
[![Coverage Status](https://coveralls.io/repos/rvdh/gpgpass/badge.png)](https://coveralls.io/r/rvdh/gpgpass)
[ ![Codeship Status for rvdh/gpgpass](https://www.codeship.io/projects/e56e6b80-2c5a-0132-64c8-1a021f7da059/status)](https://www.codeship.io/projects/38817)

The goal of this tool is to provide an easy but safe way to share passwords amongst (groups of) co-workers.
It does this by keeping a local GIT repository in sync with a remote. Changes to password files are automatically pulled to the local repository.
**The repository should only contain GPG-encrypted password files!**

The tool will try to use a gpg-agent if it's running. If it's not, you will have to enter the password for your key every time a file is decrypted.

The tool will decrypt a file into memory. If you are worried your computer's memory is not safe, don't use this tool.

By default, the tool will check for an update for itself if the last time since it checked was more then a day ago. It does a simple git pull from remote, if the installation directory is a GIT repository.
To turn this off, change the automaticupdate settings in ~/.gpgpass/config.ini.

## Prerequisites
* GnuPG
* GIT
* python-gnupg (https://pythonhosted.org/python-gnupg/)
* GitPython (https://pythonhosted.org/GitPython/0.3.1/)

## Installation
1. pip install gpgpass
2. Change the config.ini setting "passwordsRepositoryRemote" to point to your remote password repository.

## Supported platforms
The code should work on Linux, MacOS X and Windows, provided git and gnupg are configured correctly. 
For Windows, ensure git is in $PATH.

## Usage
*Note: all examples here assume the GPG-encoded files can be decoded with your GPG key.*

```
gpgpass username
```
This will search all GPG encrypted files for the string 'username' and display matching lines.

```
gpgpass -f username
```
This will search all GPG encrypted files for the string 'username' and display the whole files in which a match was found.

```
gpgpass filename.gpg
```
This will search for and display the entire file.

## Updating password files
To change a GPG-encrypted file, I suggest using vim. With the vim addon 'gnupg', you can simply 'vim file.gpg'. It will decrypt the file into memory, you can make your changes and upon quitting the file is encrypted and saved. Next, push your change to the remote.

## Setting up the password repository
The tool assumes a GIT repository has been setup, containing GPG-encrypted password files. 
### Layout
An example setup looks like this:
```
./repository/Department1/PasswordFile1.gpg
./repository/Department1/PasswordFile2.gpg
./repository/Department1/PasswordFile3.gpg
./repository/Department2/PasswordFile1.gpg
./repository/Department2/PasswordFile2.gpg
```
There's no limit in the amount of subdirectories you create. In our case, the repository looks like this:
```
./Passwords/Engineering/Networking/Switches.gpg
./Passwords/Engineering/Networking/Routing.gpg
./Passwords/Engineering/Virtualization/Chassis.gpg
./Passwords/Engineering/Virtualization/Nodes.gpg
./Passwords/Support/Domainregistries/SIDN.gpg
./Passwords/Support/Domainregistries/EURid.gpg
./Passwords/Support/Servers/Linux.gpg
./Passwords/Support/Servers/Windows.gpg
```
### Creating the encrypted files
To create new GPG encrypted password files, put plaintext password files besides the GPG encrypted files or start out with only plaintext password files.
Next, you define groups in your ~/.gnupg/gpg.conf:
```
group department1   = 0x5A66E935 0x12345678 0xABCDEF12
group department2   = 0x5A66E935 0x12345678 0xABCDEF12 0x87654321 0x21FEDBCA
group department3   = 0x5A66E935 0x12345678 0xABCDEF12 0x87654321 0x21FEDBCA 0x11223344 0xAABBCCDD
```
In this setup, I (0x5A66E935) belong to all groups so I can decrypt/encrypt all files in the password repository. User 0x87654321 will only be able to read the password files in ./repository/Department2.
You can use the following script to encrypt the plaintext password files:
```
#!/bin/bash
for GROUP in Department1 Department2 Department3; do
    for FILE in $(find ./repository/$GROUP -type f | grep -v '\.gpg'); do
        print $FILE
        gpg --yes --use-agent -r ${GROUP} -e -s $FILE
        if [ $? -eq 0 ]; then
            # Remove the plain-text file
            rm $FILE
        fi
    done
done
```
