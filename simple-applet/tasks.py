import configparser
import xml.etree.ElementTree as ET

from invoke import task
from jcvmutils.functions import valid_aid

BUILD_FILE = 'build.xml'
CONFIG_FILE = 'config.ini'

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

class AID(object):
    def __init__(self, aid):
        # TODO add validation
        self.AID = aid
        self.RID = self.AID[:10]
        self.PIX = self.AID[10:]

# tasks
@task
def aid(c):
    print(config['DEFAULT']['AID'])

@task
def update_aid(c, aid_value):
    if not valid_aid(aid_value):
        print('\'{}\' is an invalid AID'.format(aid_value))
        return

    aid = AID(aid_value)
    update_config(aid)
    update_build_aid(aid)


# helper functions
def update_config(aid):
    config['DEFAULT']['RID'] = aid.RID
    config['DEFAULT']['PIX'] = aid.PIX

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def update_build_aid(aid):
    tree = ET.parse(BUILD_FILE)

    properties = tree.findall('property')
    for prop in properties:
        if prop.attrib['name'] == 'RID':
            prop.attrib['value'] = aid.RID

        if prop.attrib['name'] == 'PIX':
            prop.attrib['value'] = aid.PIX

    tree.write(open(BUILD_FILE, 'wb'), encoding="utf-8", xml_declaration=True)
