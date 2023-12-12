from lxml import etree
import glob
import os

kml_files = glob.glob('Input/*.kml')
if not kml_files:
    raise ValueError("No KML files found in 'Input/' directory")

tree = etree.parse(kml_files[0])
root = tree.getroot()

namespaces = {'kml': 'http://www.opengis.net/kml/2.2', 'gx': 'http://www.google.com/kml/ext/2.2'}

for element_name in ['Style', 'StyleMap', 'LookAt']:
    for element in root.findall('.//kml:' + element_name, namespaces):
        element.getparent().remove(element)

for element_name in ['drawOrder']:
    for element in root.findall('.//gx:' + element_name, namespaces):
        element.getparent().remove(element)

for element_name in ['styleUrl', 'Placemark', 'tessellate', 'outerBoundaryIs', 'open']:
    for element in root.findall('.//kml:' + element_name, namespaces):
        element.getparent().extend(element)
        element.getparent().remove(element)

os.makedirs('Temp', exist_ok=True)

with open('Temp/modified_file.kml', 'wb') as f:
    f.write(etree.tostring(tree, xml_declaration=True, encoding='UTF-8', pretty_print=True))