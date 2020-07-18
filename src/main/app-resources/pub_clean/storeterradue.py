'''
Created on 15 July 2020

@author: alex
'''
import os
import requests
import json
import hashlib

def getAPIrepo():
    APIkey = 'AKCp5fU4YVRZ4UHZ39dectSqxk5wrnGMB5aVrAz4MR3EMG9nExkPt6zSGBqtehuYZNmUTiXqN'
    repo ='aapostolakis'
    uname ='aapostolakis'
    store = 'https://store.terradue.com'
    return APIkey, repo, uname, store


def retrieve_file(url, local_file):
    res = requests.get(url, allow_redirects=True)
    open(local_file, 'wb').write(res.content)
    
    
def delete_file(filename, store_url, username, api_key):
    res = requests.delete(url="{0}/{1}".format(store_url, filename), auth=(username, api_key))
    print("Response status code: {0}".format(res.status_code))
    print('File {0} deleted'.format(filename))


def send_file(local_file, content_type, store_url, username, api_key):

    # Open file to send
    content = open(local_file, 'rb').read()

    # Send file (using the HTTP PUT method)
    res = requests.put(url="{0}/{1}".format(store_url, os.path.basename(local_file)),
                       headers={"Content-Type": content_type},
                       auth=(username, api_key),
                       data=content
    )

    print("Response status code: {0}".format(res.status_code))

    assert res.status_code == 201

    print('File {0} uploaded'.format(local_file))

    # Verify the content (hash check)

    local_checksum = hashlib.sha256(content).hexdigest()
    remote_checksum = res.json()['checksums']['sha256']

    print("- Local checksum:  {0}".format(local_checksum))
    print("- Remote checksum: {0}".format(remote_checksum))

    assert local_checksum == remote_checksum

def sendfiles(fileslist, localfolder, remotefolder):
    # Set the credentials (Ellip username and API key)
    api_key, repo_name, username, store = getAPIrepo()
    
    # Set the destination URL on store (directory)
    store_url = "{2}/{0}/{1}/".format(repo_name, remotefolder, store)
    
    # Set dictionary with file information
        
    for f in fileslist:
        fullpath=os.path.join(localfolder,f['name'])
        try:
            send_file(fullpath, f['content_type'], store_url, username, api_key)
        except Exception as e:
            print('ERROR: File {0} NOT uploaded: {1}'.format(f['name'], e))


def deletefiles(fileslist, remotefolder):
    # Set the credentials (Ellip username and API key)
    api_key, repo_name, username, basic_url = getAPIrepo()
    
    # Set the destination URL on store (directory)
    store_url = "{2}/{0}/{1}/".format(repo_name, remotefolder, basic_url)
    
    # Set dictionary with file information
        
    for f in fileslist:
        try:
            delete_file(f['name'], store_url, username, api_key)
        except Exception as e:
            print('ERROR: File {0} NOT uploaded: {1}'.format(f['name'], e))

