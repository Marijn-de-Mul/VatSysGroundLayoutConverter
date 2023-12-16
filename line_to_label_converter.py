import os
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def create_kml_structure(bay_lines):
    kml = Element('kml', {'xmlns:gx': 'http://www.google.com/kml/ext/2.2'})
    document = SubElement(kml, 'Document')
    folder = SubElement(document, 'Folder')
    name = SubElement(folder, 'name')
    name.text = 'Lab'
    subfolder = SubElement(folder, 'Folder')
    subfolder_name = SubElement(subfolder, 'name')
    subfolder_name.text = 'Bay'
    open_tag = SubElement(subfolder, 'open')
    open_tag.text = '1'

    for line in bay_lines:
        placemark = SubElement(subfolder, 'Placemark')
        placemark_name = SubElement(placemark, 'name')
        placemark_name.text = line[0]  # line name
        lookat = SubElement(placemark, 'LookAt')
        longitude = SubElement(lookat, 'longitude')
        longitude.text = str(line[1][0])  # first coordinate
        latitude = SubElement(lookat, 'latitude')
        latitude.text = str(line[1][1])  # second coordinate
        altitude = SubElement(lookat, 'altitude')
        altitude.text = '0'
        heading = SubElement(lookat, 'heading')
        heading.text = '-48.71114456521964'
        tilt = SubElement(lookat, 'tilt')
        tilt.text = '5.542398972479446'
        range_tag = SubElement(lookat, 'range')
        range_tag.text = '1991.93130203422'
        altitude_mode = SubElement(lookat, 'gx:altitudeMode')
        altitude_mode.text = 'relativeToSeaFloor'

        style_url = SubElement(placemark, 'styleUrl')
        style_url.text = '#m_ylw-pushpin0'

        point = SubElement(placemark, 'Point')
        draw_order = SubElement(point, 'gx:drawOrder')
        draw_order.text = '1'
        coordinates = SubElement(point, 'coordinates')
        coordinates.text = f"{line[1][0]},{line[1][1]},0"  # coordinates

    return prettify(kml)

def parse_kml_file(file_path):
    tree = ElementTree()
    tree.parse(file_path)
    root = tree.getroot()

    bay_lines = []
    for placemark in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
        name = placemark.find('{http://www.opengis.net/kml/2.2}name').text
        line_string = placemark.find('{http://www.opengis.net/kml/2.2}LineString')
        if line_string is not None:
            coordinates_text = line_string.find('{http://www.opengis.net/kml/2.2}coordinates').text.strip()
            coordinates_pairs = coordinates_text.split(' ')
            if coordinates_pairs:
                pair = coordinates_pairs[0]
                coordinates = pair.split(',')
                if len(coordinates) >= 2 and coordinates[0] and coordinates[1]:
                    bay_lines.append((name, (float(coordinates[0]), float(coordinates[1]))))

    return bay_lines

def write_to_file(output, filename):
    if not os.path.exists('Output'):
        os.makedirs('Output')
    with open(f'Output/converted_{filename}', 'w') as f:
        f.write(output)

filename = 'WIII.kml'
bay_lines = parse_kml_file(f'Input/{filename}')
output = create_kml_structure(bay_lines)
write_to_file(output, filename)