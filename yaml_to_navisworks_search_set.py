import logging
import os
import xml.etree.ElementTree as ET

import yaml
from dotenv import load_dotenv


FILENAME = "SOURCE"
load_dotenv()


def _load_yaml_file(filename):
    # loads and returns the .yaml file
    if filename and os.path.exists(filename):
        logger.debug(f'Loading content from {filename}')
        with open(filename) as stream:
            try:
                return yaml.load(stream, Loader=yaml.SafeLoader)
            except Exception as e:
                raise e
    else:
        logger.error(f'Cannot load content from {filename} - file does not exist')


def _add_selectionset(key, val):
    selectionset = None
    if key and val:
        selectionset = ET.Element('selectionset')
        selectionset.set('name', key)
        findspec = ET.SubElement(selectionset, 'findspec')
        findspec.set('mode', 'all')
        findspec.set('disjoint', '0')
        conditions = ET.SubElement(findspec, 'conditions')

        # add conditions
        for idx in range(len(val)):
            if idx == 0:
                flags = '26'
            else:
                flags = '90'  # or

            if val[idx].find('*'):
                test = 'wildcard'
            else:
                test = 'contains'

            condition = ET.SubElement(conditions, 'condition')
            condition.set('test', test)
            condition.set('flags', flags)
            property = ET.SubElement(condition, 'property')
            name = ET.SubElement(property, 'name')
            name.set('internal', 'LcOaSceneBaseUserName')
            name.text = 'Name'
            value = ET.SubElement(condition, 'value')
            data = ET.SubElement(value, 'data')
            data.set('type', 'wstring')
            data.text = val[idx]

    return selectionset


def _build_xml_file(dict):
    # preliminaries
    exchange = ET.Element('exchange')
    exchange.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    exchange.set('xsi:noNamespaceSchemaLocation', 'http://download.autodesk.com/us/navisworks/schemas/nw-exchange-12.0.xsd')
    exchange.set('units', 'm')
    exchange.set('filename', '')
    exchange.set('filepath', '')

    selectionsets = ET.SubElement(exchange, 'selectionsets')
    viewfolder = ET.SubElement(selectionsets, 'viewfolder')
    viewfolder.set('name', 'T&I')

    for key, val in dict.items():
        selectionset = _add_selectionset(key, val)
        if selectionset:
            viewfolder.append(selectionset)
    return exchange


logger = logging.getLogger(__name__)

yamlfile = _load_yaml_file(os.getenv(FILENAME))
xmlfile = _build_xml_file(yamlfile)

# create and write xml file
tree = ET.ElementTree(xmlfile)
ET.indent(tree, space='\t', level=0)
file_name, file_extension = os.path.splitext(os.getenv(FILENAME))
destination_file = file_name + '.xml'
tree.write(destination_file, xml_declaration=True, encoding='utf-8')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
