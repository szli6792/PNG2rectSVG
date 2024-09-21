from PIL import Image
from xml.etree import ElementTree as ET
import re
import os

# THE OPTIMIZING FUNCTION:
def consolidate_rects(svg_string):
    # Register SVG namespace without a prefix
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    # Parse SVG
    root = ET.fromstring(svg_string)

    # Group rectangles by row and merge horizontally adjacent ones
    rows = {}
    for elem in root.iter():
        if elem.tag.endswith('rect'):
            x = int(elem.attrib['x'])
            y = int(elem.attrib['y'])
            width = int(elem.attrib['width'])
            height = int(elem.attrib['height'])
            fill = elem.attrib['style'].split(':')[1].strip(';')

            # Find or create row entry
            if y in rows:
                row = rows[y]
            else:
                row = {'min_x': float('inf'), 'max_x': float('-inf'), 'rects': []}
                rows[y] = row

            # Update min and max x for the row
            row['min_x'] = min(row['min_x'], x)
            row['max_x'] = max(row['max_x'], x + width)

            # Add rect to the row
            row['rects'].append({'x': x, 'y': y, 'width': width, 'height': height, 'fill': fill})

    # Merge horizontally adjacent rectangles in each row
    for row in rows.values():
        rects = row['rects']
        merged_rects = []

        # Merge horizontally adjacent rectangles
        current_x = row['min_x']
        current_width = 0
        current_fill = None
        for rect_idx, rect in enumerate(rects):
            if rect['x'] == current_x + current_width and rect['fill'] == current_fill:
                current_width += rect['width']
            else:
                if current_width > 0:
                    merged_rects.append({'x': current_x, 'y': rect['y'], 'width': current_width, 'height': rect['height'], 'fill': current_fill})
                current_x = rect['x']
                current_width = rect['width']
                current_fill = rect['fill']

        # Add the last merged rectangle
        if current_width > 0:
            merged_rects.append({'x': current_x, 'y': rect['y'], 'width': current_width, 'height': rect['height'], 'fill': current_fill})
        elif current_width == 0 and len(rects) == 1:  # If only one rectangle in the row, add it even if no merging
            merged_rects.append(rects[0])

        row['rects'] = merged_rects




    # Create new SVG structure with consolidated rectangles
    new_root = ET.Element('{http://www.w3.org/2000/svg}svg')
    #new_root.attrib['width'] = root.attrib.get('width', '100')  # Use a default width if not found
    #new_root.attrib['height'] = root.attrib['height']
    new_root.attrib['viewBox'] = root.attrib['viewBox']

    # Add consolidated rectangles to the new SVG
    for row in rows.values():
        for rect in row['rects']:
            rect_elem = ET.SubElement(new_root, '{http://www.w3.org/2000/svg}rect')
            rect_elem.attrib['x'] = str(rect['x'])
            rect_elem.attrib['y'] = str(rect['y'])
            rect_elem.attrib['width'] = str(rect['width'])
            rect_elem.attrib['height'] = str(rect['height'])
            rect_elem.attrib['style'] = 'fill:' + rect['fill'] + ';'

    # Serialize modified SVG back to string
    modified_svg = ET.tostring(new_root, encoding='unicode')

    # Use regular expressions to find and remove the black pixels
    modified_svg = re.sub(r'style="fill:#000000;?".*?/>', '/>', modified_svg)

    return modified_svg

# THE SVG_RECT MAKING FUNCTION:
def pixel_to_svg_rect(x, y, color):
    return f'<rect x="{x}" y="{y}" width="1" height="1" style="fill:{color};"></rect>'

# THE MAIN FUNCTION:
def png_to_svg(input_path, output_path, a, b):
    img = Image.open(input_path)
    width, height = img.size
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
    
    # Convert each png pixel to rect object
    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            if len(pixel) == 4 and pixel[3] == 0:
                continue  # Ignore completely transparent pixels
            color = '#{:02x}{:02x}{:02x}'.format(*pixel[:3])
            svg_content += pixel_to_svg_rect(x, y, color)
    
    svg_content += '</svg>'

    consolidated_svg = consolidate_rects(svg_content) #Optimize the SVG with horizontal and vertical merging of rect objects
    translated_svg = translate_svg(consolidated_svg,a,b) # Translate the SVG to taste for different levels
    
    with open(output_path, 'w') as f:
        f.write(translated_svg) 
  
def translate_svg(input_path,a,b):
    # Parse the SVG file
    root = ET.fromstring(input_path)

    # Iterate through each <rect> element
    for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
        # Get the current x value and translate it down by 2 units
        x = int(rect.attrib['x'])
        new_x = x + a
        y = int(rect.attrib['y'])
        new_y = y + b
        
        # Update the x attribute with the translated value
        rect.set('x', str(new_x))
        rect.set('y', str(new_y))

    # Write the modified SVG to a new file
    #tree.write(output_path)
    translated_svg = ET.tostring(root, encoding='unicode')

    return translated_svg              

def rename_png_and_save_svg(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
      
    i = 1
    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):

        if filename.endswith(".png"):
            # Extract the file name and extension
            #file_name, file_ext = os.path.splitext(filename)
        
            new_filename = f"yoyo {i}.svg"
            new_file_path = os.path.join(output_folder, new_filename)

            extendedFilename = input_folder + '/' + filename
                
                # Read the content of the PNG file/Write new file
            png_to_svg(extendedFilename, new_file_path, 0, 0)

        i += 1


# Example usage:
input_folder = 'png' ######################################### MODIFY NAME HERE
output_folder = 'svg' ######################################### MODIFY NAME HERE
rename_png_and_save_svg(input_folder, output_folder)



# USE HERE:
#input_path = 'sc2k nuclear plant correct colors.png'
#output_path = 'output.svg'
#png_to_svg(input_path, output_path)
