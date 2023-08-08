"""Reads a yaml file and creates a Navisworks XML search set file.

:param ENV SOURCE: filename of the yaml file to be read
:returns: a Navisworks XML search set
"""
import logging
import os
from pathlib import Path
from xml.etree import ElementTree

import yaml
from dotenv import load_dotenv

FILENAME = "SOURCE"
load_dotenv()


def _load_yaml_file(filename: str) -> str:
    # loads and returns the .yaml file
    file_content = None
    file = Path(filename) if filename else None
    if file and file.exists:
        logger.debug(f"Loading content from {filename}")
        with file.open() as stream:
            file_content = yaml.load(stream, Loader=yaml.SafeLoader)
    else:
        logger.error(f"Cannot load content from {filename} - file does not exist")
    return file_content


def _add_selectionset(key: str, val: str) -> ElementTree.Element:
    selectionset = None
    if key and val:
        selectionset = ElementTree.Element("selectionset")
        selectionset.set("name", key)
        findspec = ElementTree.SubElement(selectionset, "findspec")
        findspec.set("mode", "all")
        findspec.set("disjoint", "0")
        conditions = ElementTree.SubElement(findspec, "conditions")

        # add conditions
        for idx in range(len(val)):
            flags = "26" if idx ==0 else "90" # or

            test = "wildcard" if "*" in val[idx] else "contains"

            condition = ElementTree.SubElement(conditions, "condition")
            condition.set("test", test)
            condition.set("flags", flags)
            prop = ElementTree.SubElement(condition, "property")
            name = ElementTree.SubElement(prop, "name")
            name.set("internal", "LcOaSceneBaseUserName")
            name.text = "Name"
            value = ElementTree.SubElement(condition, "value")
            data = ElementTree.SubElement(value, "data")
            data.set("type", "wstring")
            data.text = val[idx]

    return selectionset


def _build_xml_file(set_dict: dict) -> ElementTree.Element:
    # preliminaries
    exchange = ElementTree.Element("exchange")
    exchange.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    exchange.set("xsi:noNamespaceSchemaLocation", "http://download.autodesk.com/us/navisworks/schemas/nw-exchange-12.0.xsd")
    exchange.set("units", "m")
    exchange.set("filename", "")
    exchange.set("filepath", "")

    selectionsets = ElementTree.SubElement(exchange, "selectionsets")
    viewfolder = ElementTree.SubElement(selectionsets, "viewfolder")
    viewfolder.set("name", "T&I")

    if set_dict:
        for key, val in set_dict.items():
            selectionset = _add_selectionset(key, val)
            if selectionset:
                viewfolder.append(selectionset)

    return exchange


logger = logging.getLogger(__name__)

yamlfile = _load_yaml_file(os.getenv(FILENAME))
xmlfile = _build_xml_file(yamlfile)

# create and write xml file
tree = ElementTree.ElementTree(xmlfile)
ElementTree.indent(tree, space="\t", level=0)

source = Path(os.getenv(FILENAME))
destination = source.parent / (source.stem + ".xml" )
tree.write(destination, xml_declaration=True, encoding="utf-8")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
