# coding:utf-8
from os import listdir
from os.path import dirname, join, splitext, exists
import configparser

PACKAGE_DIR = "package"
UPLOAD_DIR = "upload"
EXE_DIR = join(dirname(__file__), "exe")

PROFILES_DIR = join(EXE_DIR, "profiles")
CERTS = {}

for f in listdir(PROFILES_DIR):
    bn, ext = splitext(f)
    if ext != '.cfg':
        continue
    nn = bn + '.keystore'
    if not exists(join(PROFILES_DIR, nn)):
        continue

    cf = configparser.SafeConfigParser()
    cf.read(join(PROFILES_DIR, f))
    if 'build' in cf.sections():
        CERTS[nn] = dict(cf.items('build'))

print('certifications')
print(CERTS)
