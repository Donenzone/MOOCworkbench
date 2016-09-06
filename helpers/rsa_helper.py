from Crypto.PublicKey import RSA
import os

def generate_ssh_private_public_key_pair():
    key = RSA.generate(2048)
    encrypted_key = key.exportKey('PEM')

    file_out = open(os.path.expanduser("~/.ssh/mooc_workbench_rsa"), "wb")
    file_out.write(encrypted_key)

    file_out = open(os.path.expanduser("~/.ssh/mooc_workbench_rsa.pub"), "wb")
    file_out.write(key.publickey().exportKey('OpenSSH'))

def add_key_to_ssh_agent():
    os.system("some_command with args")
generate_ssh_private_public_key_pair()
