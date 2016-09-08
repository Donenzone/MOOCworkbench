from Crypto.PublicKey import RSA
import os
from git import Repo

def generate_ssh_private_public_key_pair():
    key = RSA.generate(2048)
    encrypted_key = key.exportKey('PEM')

    file_out = open(os.path.expanduser("~/.ssh/mooc_workbench_rsa"), "wb")
    file_out.write(encrypted_key)

    file_out = open(os.path.expanduser("~/.ssh/mooc_workbench_rsa.pub"), "wb")
    file_out.write(key.publickey().exportKey('OpenSSH'))

    return key.publickey().exportKey('OpenSSH').decode('utf-8')

def add_public_key_to_auth_keys(ssh_pub_key):
    with open(os.path.expanduser("~/.ssh/authorized_keys"), "a") as auth_key_file:
        auth_key_file.write(ssh_pub_key + '\n')

def clone_repo_via_ssh(git_path, repo_name):
    Repo.clone_from('jochem@192.168.29.128:' + git_path, repo_name)
