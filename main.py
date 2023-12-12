from lxml import etree
import glob
import os

kml_files = glob.glob('Input/*.kml')
if not kml_files:
    raise ValueError("No KML files found in 'Input/' directory")

def format_line(input_string):
    split_string = input_string.split(',')
    if len(split_string) < 3:
        return None
    formatted_string = '+{0:09.6f}+{1:010.6f}'.format(float(split_string[1]), float(split_string[0]))
    return formatted_string

def process_section(f, section_name, map_type, map_name, priority, infill_name, write_opening_map_tag, write_closing_map_tag):
    coordinates = []
    latitudes = []
    longitudes = []
    for name in temp_root.findall(".//kml:name[.='{}']".format(section_name), namespaces):
        print(f"Found section: {section_name}")  # Debug print
        polygon = name.getnext()
        if polygon is not None and polygon.tag == "{http://www.opengis.net/kml/2.2}Polygon":
            coordinates_element = polygon.find(".//kml:coordinates", namespaces)
            if coordinates_element is not None:
                for coordinate in coordinates_element.text.split():
                    formatted_coordinate = format_line(coordinate)
                    if formatted_coordinate is not None:
                        coordinates.append(formatted_coordinate)
                        lat, lon = map(float, coordinate.split(',')[:2])
                        latitudes.append(lat)
                        longitudes.append(lon)
            else:
                print(f"No coordinates found for section: {section_name}")  # Debug print
                return
        else:
            print(f"No Polygon found for section: {section_name}")  # Debug print
            return
        
    if not coordinates:
        print(f"No coordinates found for section: {section_name}")  # Debug print
        return

    if coordinates[0] == coordinates[-1]:
        coordinates.pop(0)
        latitudes.pop(0)
        longitudes.pop(0)

    min_lat, max_lat = min(latitudes), max(latitudes)
    min_lon, max_lon = min(longitudes), max(longitudes)
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    center_coordinate = '+{0:03.6f}+{1:02.6f}'.format(center_lon, center_lat) 

    parts = center_coordinate.split("+")
    lat = parts[1]
    lon = parts[2]
    if '.' in lat and len(lat.split('.')[0]) < 2:
        lat = '0' + lat
    center_coordinate = '+' + lat + '+' + lon

    airport_ICAO = os.path.splitext(os.path.basename(kml_file))[0]
    custom_color = ' CustomColourName="DeepLush"' if airport_ICAO.startswith('WI') and map_type == 'Ground_BAK' else ''

    if write_opening_map_tag:
        f.write(f'    <Map Type="{map_type}" Name="SMR_{airport_ICAO}_{map_name}" Priority="{priority}" Center="{center_coordinate}"{custom_color}>\n')
    f.write(f'        <Infill Name="{infill_name}">\n')
    f.write('            ' + '/\n            '.join(coordinates) + '\n')
    f.write('        </Infill>\n')
    if write_closing_map_tag:
        f.write('    </Map>\n')


for kml_file in kml_files:
    tree = etree.parse(kml_file)
    root = tree.getroot()

    namespaces = {'kml': 'http://www.opengis.net/kml/2.2', 'gx': 'http://www.google.com/kml/ext/2.2'}

    for element_name in ['Style', 'StyleMap', 'LookAt']:
        for element in root.findall('.//kml:' + element_name, namespaces):
            element.getparent().remove(element)

    for element_name in ['drawOrder']:
        for element in root.findall('.//gx:' + element_name, namespaces):
            element.getparent().remove(element)

    for element_name in ['styleUrl', 'Placemark', 'tessellate', 'outerBoundaryIs', 'open', 'Folder']:
        for element in root.findall('.//kml:' + element_name, namespaces):
            element.getparent().extend(element)
            element.getparent().remove(element)

    output_file_path = os.path.join('Output', f'SMR_{os.path.splitext(os.path.basename(kml_file))[0]}.xml')
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    temp_file_path = os.path.join('Temp', 'temp.kml')
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

    os.makedirs('Temp', exist_ok=True)

    with open(os.path.join('Temp', 'temp.kml'), 'wb') as f:
        f.write(etree.tostring(tree, xml_declaration=True, encoding='UTF-8', pretty_print=True))

    os.makedirs('Output', exist_ok=True)

    temp_tree = etree.parse(os.path.join('Temp', 'temp.kml'))
    temp_root = temp_tree.getroot()

    with open(os.path.join('Output', f'SMR_{os.path.splitext(os.path.basename(kml_file))[0]}.xml'), 'a') as f:  # Change 'w' to 'a'
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<Maps>\n')

        process_section(f, 'GrassBG', 'Ground_BAK', 'BAK','6', 'GrassBG', True, True)

        hole_number = 1
        while True:
            section_name = 'GrassHole{}'.format(hole_number)
            next_section_name = 'GrassHole{}'.format(hole_number + 1)
            write_opening_map_tag = hole_number == 1
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_section(f, section_name, 'Ground_BAK', 'HOLES', '4', section_name, write_opening_map_tag, write_closing_map_tag)
                hole_number += 1
            else:
                break

        process_section(f, 'Move', 'Ground_APR', 'MOVE', '5', 'Movement_Areas', True, True)

        building_number = 1
        while True:
            section_name = 'Bldg{}'.format(building_number)
            next_section_name = 'Bldg{}'.format(building_number + 1)
            write_opening_map_tag = building_number == 1
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_section(f, section_name, 'Ground_BLD', 'BLD', '4', section_name, write_opening_map_tag, write_closing_map_tag)
                building_number += 1
            else:
                break

        runway_number = 1
        while True:
            section_name = 'Rwy{}'.format(runway_number)
            next_section_name = 'Rwy{}'.format(runway_number + 1)
            write_opening_map_tag = runway_number == 1
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_section(f, section_name, 'Ground_RWY', 'RWY', '4', section_name, write_opening_map_tag, write_closing_map_tag)
                runway_number += 1
            else:
                break

        f.write('</Maps>\n')