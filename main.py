from lxml import etree
import glob
import shutil
import os

kml_files = glob.glob('Input/*.kml')
if not kml_files:
    raise ValueError("No KML files found in 'Input/' directory")

def format_line(input_string):
    split_string = input_string.split(',')
    if len(split_string) < 3:
        return None
    lat = float(split_string[1])
    lon = float(split_string[0])
    formatted_lat = '{0:+.6f}'.format(lat).zfill(10)
    formatted_lon = '{0:+.6f}'.format(lon).zfill(11)
    formatted_string = formatted_lat + formatted_lon
    return formatted_string

def process_polygon(f, section_name, map_type, map_name, priority, infill_name, write_opening_map_tag, write_closing_map_tag):
    coordinates = []
    latitudes = []
    longitudes = []
    for name in temp_root.findall(".//kml:name[.='{}']".format(section_name), namespaces):
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

    if coordinates[0] == coordinates[-1]:
        coordinates.pop(0)
        latitudes.pop(0)
        longitudes.pop(0)

    def format_coordinate(lat, lon):
        return '{0:+010.6f}{1:+09.6f}'.format(lon, lat)

    min_lat, max_lat = min(latitudes), max(latitudes)
    min_lon, max_lon = min(longitudes), max(longitudes)
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    center_coordinate = format_coordinate(center_lat, center_lon)
    
    airport_ICAO = os.path.splitext(os.path.basename(kml_file))[0]
    custom_color = ' CustomColourName="DeepLush"' if airport_ICAO.startswith('WI') and map_type == 'Ground_BAK' else ''

    if write_opening_map_tag:
        f.write(f'    <Map Type="{map_type}" Name="SMR_{airport_ICAO}_{map_name}" Priority="{priority}" Center="{center_coordinate}"{custom_color}>\n')
    f.write(f'        <Infill Name="{infill_name}">\n')
    f.write('            ' + '/\n            '.join(coordinates) + '\n')
    f.write('        </Infill>\n')
    if write_closing_map_tag:
        f.write('    </Map>\n')

def process_line(f, section_name, map_type, map_name, priority, infill_name, write_opening_map_tag, write_closing_map_tag):
    coordinates = []
    latitudes = []
    longitudes = []
    for name in temp_root.findall(".//kml:name[.='{}']".format(section_name), namespaces):
        polygon = name.getnext()
        if polygon is not None and polygon.tag == "{http://www.opengis.net/kml/2.2}LineString":
            coordinates_element = polygon.find(".//kml:coordinates", namespaces)
            if coordinates_element is not None:
                for coordinate in coordinates_element.text.split():
                    formatted_coordinate = format_line(coordinate)
                    if formatted_coordinate is not None:
                        coordinates.append(formatted_coordinate)
                        lat, lon = map(float, coordinate.split(',')[:2])
                        latitudes.append(lat)
                        longitudes.append(lon)

    if coordinates[0] == coordinates[-1]:
        coordinates.pop(0)
        latitudes.pop(0)
        longitudes.pop(0)

    def format_coordinate(lat, lon):
        return '{0:+010.6f}{1:+09.6f}'.format(lon, lat)

    min_lat, max_lat = min(latitudes), max(latitudes)
    min_lon, max_lon = min(longitudes), max(longitudes)
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    center_coordinate = format_coordinate(center_lat, center_lon)

    airport_ICAO = os.path.splitext(os.path.basename(kml_file))[0]
    custom_color = ''
    width = ''
    if airport_ICAO.startswith('WI'):
        if map_name in [f'SB']:
            custom_color = ' CustomColourName="RosenbauerRed"'
            width = ' Width="2"'
        elif map_name in [f'BAY_CL']: 
            custom_color = ' CustomColourName="SuperDuperLightGrey"'
        elif map_name in [f'TWY_CL']:
            custom_color = ' CustomColourName="SuperDuperLightGrey"'

    if write_opening_map_tag:
        f.write(f'    <Map Type="{map_type}" Name="SMR_{airport_ICAO}_{map_name}" Priority="{priority}" Center="{center_coordinate}"{custom_color}{width}>\n')
    f.write(f'        <Line Name="{infill_name}">\n')
    f.write(f'        <Point>\n')
    f.write('            ' + '/\n            '.join(coordinates) + '\n')
    f.write(f'        </Point>\n')
    f.write('        </Line>\n')
    if write_closing_map_tag:
        f.write('    </Map>\n')

def process_label(f, section_name, map_type, map_name, priority, write_opening_map_tag, write_closing_map_tag):
    labels = []
    latitudes = []
    longitudes = []
    for name in temp_root.findall(".//kml:name[.='{}']".format(section_name), namespaces):
        sibling = name.getnext()
        while sibling is not None:
            if sibling.tag == "{http://www.opengis.net/kml/2.2}name":
                label_name = sibling.text
                point = sibling.getnext()
                if point is not None and point.tag == "{http://www.opengis.net/kml/2.2}Point":
                    coordinates_element = point.find(".//kml:coordinates", namespaces)
                    if coordinates_element is not None:
                        coordinate = coordinates_element.text.strip()
                        formatted_coordinate = format_line(coordinate)
                        if formatted_coordinate is not None:
                            labels.append((label_name, formatted_coordinate))
                            lat, lon = map(float, coordinate.split(',')[:2])
                            latitudes.append(lat)
                            longitudes.append(lon)
                sibling = point.getnext()
            else:
                sibling = sibling.getnext()

    def format_coordinate(lat, lon):
        return '{0:+010.6f}{1:+09.6f}'.format(lon, lat)

    min_lat, max_lat = min(latitudes), max(latitudes)
    min_lon, max_lon = min(longitudes), max(longitudes)
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    center_coordinate = format_coordinate(center_lat, center_lon)

    if write_opening_map_tag:
        f.write(f'    <Map Type="{map_type}" Name="SMR_{os.path.splitext(os.path.basename(kml_file))[0]}_{map_name}" Priority="{priority}" Center="{center_coordinate}" CustomColourName="TremendouslyLightGrey">\n')
    f.write(f'        <Label HasLeader="False" Alignment="Center" VerticalAlignment="Middle">\n')
    for label_name, label_coordinate in labels:
        f.write(f'            <Point Name="{label_name}">{label_coordinate}</Point>\n')
    f.write('        </Label>\n')
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

    for element_name in ['styleUrl', 'Placemark', 'tessellate', 'outerBoundaryIs', 'open']:
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

    print(os.path.splitext(os.path.basename(kml_file))[0])

    with open(os.path.join('Output', f'SMR_{os.path.splitext(os.path.basename(kml_file))[0]}.xml'), 'a') as f:  
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<Maps>\n')

        process_polygon(f, 'GrassBG', 'Ground_BAK', 'BAK','6', 'GrassBG', True, True)

        hole_number = 1
        while True:
            section_name = 'GrassHole{}'.format(hole_number)
            next_section_name = 'GrassHole{}'.format(hole_number + 1)
            write_opening_map_tag = hole_number == 1
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_polygon(f, section_name, 'Ground_BAK', 'HOLES', '4', section_name, write_opening_map_tag, write_closing_map_tag)
                hole_number += 1
            else:
                break

        move_number = 0
        while True:
            if move_number == 0:
                section_name = 'Move'
            else:
                section_name = 'Move{}'.format(move_number)
            next_section_name = 'Move{}'.format(move_number + 1)
            write_opening_map_tag = move_number == 0
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_polygon(f, section_name, 'Ground_APR', 'MOVE', '5', section_name, write_opening_map_tag, write_closing_map_tag)
                move_number += 1
            else:
                break

        building_number = 1
        while True:
            section_name = 'Bldg{}'.format(building_number)
            next_section_name = 'Bldg{}'.format(building_number + 1)
            write_opening_map_tag = building_number == 1
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_polygon(f, section_name, 'Ground_BLD', 'BLD', '4', section_name, write_opening_map_tag, write_closing_map_tag)
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
                process_polygon(f, section_name, 'Ground_RWY', 'RWY', '4', section_name, write_opening_map_tag, write_closing_map_tag)
                runway_number += 1
            else:
                break

        taxiway_CL_number = 1
        while True:
            section_name = 'Twy{}'.format(taxiway_CL_number)
            next_section_name = 'Twy{}'.format(taxiway_CL_number + 1)
            write_opening_map_tag = taxiway_CL_number == 1
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_line(f, section_name, 'Ground_INF', 'TWY_CL', '3', section_name, write_opening_map_tag, write_closing_map_tag)
                taxiway_CL_number += 1
            else:
                break

        taxiway_BAY_CL_number = 1
        while True:
            section_name = 'Bay{}'.format(taxiway_BAY_CL_number)
            next_section_name = 'Bay{}'.format(taxiway_BAY_CL_number + 1)
            write_opening_map_tag = taxiway_BAY_CL_number == 1
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_line(f, section_name, 'Ground_INF', 'BAY_CL', '3', section_name, write_opening_map_tag, write_closing_map_tag)
                taxiway_BAY_CL_number += 1
            else:
                break

        stopbar_number = 1
        while True:
            section_name = 'SB{}'.format(stopbar_number)
            next_section_name = 'SB{}'.format(stopbar_number + 1)
            write_opening_map_tag = stopbar_number == 1
            write_closing_map_tag = temp_root.find(".//kml:name[.='{}']".format(next_section_name), namespaces) is None
            if temp_root.find(".//kml:name[.='{}']".format(section_name), namespaces) is not None:
                process_line(f, section_name, 'Ground_INF', 'SB', '3', section_name, write_opening_map_tag, write_closing_map_tag)
                stopbar_number += 1
            else:
                break
        
        process_label(f, 'Bay', 'Ground_INF', 'BAY', '1', True, True)
        process_label(f, 'Twy', 'Ground_INF', 'TWY', '1', True, True)

        f.write('</Maps>\n')
    
    shutil.rmtree('Temp/')