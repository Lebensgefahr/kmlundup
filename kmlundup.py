#!/usr/bin/env python

import os, sys
import re
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom


# Extract date and time only from description field placed by Locus Pro.
def cleanDescription(text):

  if text:
    m = re.search('time: ([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2})', text)
    if m:
      date = m.group(3)+'.'+m.group(2)+'.'+m.group(1)
      time = m.group(4)
      return date + ' ' + time
  return text

# Round coordinates without error in positioning. For some reasons coordiantes from different programs
# may differ in fractional part. It makes two different points from one point.

def roundCoordinates(coordinates):

  longtitude, latitude, altitude = coordinates.split(',')
  return str(round(float(longtitude), 6))+','+str(round(float(latitude), 6))+','+altitude

# Insert point or track into hash array
def addTo(rec):
  if not coordinates in rec:
    rec[coordinates] = { 'name' : name, 'description' : description }
  else:
    # If current entity is already in the hash array check its description lenght and keep longer 
    if rec[coordinates]['description']:
      if description:
        if len(rec[coordinates]['description']) < len(description):
          rec[coordinates] = { 'name' : name, 'description' : description }

# Add main tag. Keep in mind that this tag should be removed before parsing (it make some problems)
def addRoot():
  root = Element('kml', {'xmlns':'http://earth.google.com/kml/2.2'})
  return root

# Add document tag
def addDoc(name):
  document = Element(name)
  return document

# Add folder tag
def addFolder(name):
  folder = Element('Folder')
  folderName = SubElement(folder, 'name')
  folderName.text = name
  state = SubElement(folder, 'open')
  state.text = '1'
  style = Element('Style')
  folder.append(style)
  listStyle = Element('ListStyle')
  style.append(listStyle)
  listItemType = SubElement(listStyle, 'listItemType')
  listItemType.text = 'check'
  bgColor = SubElement(listStyle, 'bgColor')
  bgColor.text = '00ffffff'
  return folder

# Add point with all necessary tags
def addPoint(name, description, coordinates):

  placemark = Element('Placemark')
  placemarkName = SubElement(placemark, 'name')
  placemarkName.text = name
  placemarkDesc = SubElement(placemark, 'description')
  placemarkDesc.text = description
  placemarkStyle = Element('Style')
  placemark.append(placemarkStyle)
  placemarkLabelStyle = Element('LabelStyle')
  placemarkStyle.append(placemarkLabelStyle)
  placemarkLabelColor = SubElement(placemarkLabelStyle, 'color')
  placemarkLabelColor.text = 'A600FFFF'
  placemarkLabelScale = SubElement(placemarkLabelStyle, 'scale')
  placemarkLabelScale.text = '0.785714285714286'
  placemarkIconStyle = Element('IconStyle')
  placemarkStyle.append(placemarkIconStyle)
  placemarkIconScale = SubElement(placemarkIconStyle, 'scale')
  placemarkIconScale.text = '0.5'
  placemarkIcon = Element('Icon')
  placemarkIconStyle.append(placemarkIcon)
  placemarkIconHref = SubElement(placemarkIcon, 'href')
  placemarkIconHref.text = 'files\\1.png'
  placemarkHotSpot = SubElement(placemarkIconStyle, 'hotSpot', { 'x':'0.5', 'y':'0', 'xunits':'fraction', 'yunits':'fraction'})
  placemarkPoint = Element('Point')
  placemark.append(placemarkPoint)
  placemarkPointExtrude = SubElement(placemarkPoint, 'extrude')
  placemarkPointExtrude.text = '1'
  placemarkPointCoordinates = SubElement(placemarkPoint, 'coordinates')
  placemarkPointCoordinates.text = coordinates
  return placemark

# Add track with all necessary tag
def addTrack(name, description, coordinates):

  placemark = Element('Placemark')
  placemarkName = SubElement(placemark, 'name')
  placemarkName.text = name
  placemarkDesc = SubElement(placemark, 'description')
  placemarkDesc.text = description
  placemarkStyle = Element('Style')
  placemark.append(placemarkStyle)
  placemarkLineStyle = Element('LineStyle')
  placemarkStyle.append(placemarkLineStyle)
  placemarkLineColor = SubElement(placemarkLineStyle, 'color')
  placemarkLineColor.text = 'A60000FF'
  placemarkLineWidth = SubElement(placemarkLineStyle, 'width')
  placemarkLineWidth.text = '2'
  placemarkLineString = Element('LineString')
  placemark.append(placemarkLineString)
  placemarkLineStringExtrude = SubElement(placemarkLineString, 'extrude')
  placemarkLineStringExtrude.text = '1'
  placemarkLineStringCoordinates = SubElement(placemarkLineString, 'coordinates')
  placemarkLineStringCoordinates.text = coordinates
  return placemark

# Walk through document looking for placemark tags.
def findPlacemark(root):

  global coordinates, name, description

  for placemark in root:
    if placemark.tag == "Placemark":
      for item in placemark:
        if item.tag == "name":
          name = item.text
        if item.tag == "description":
          description = cleanDescription(item.text)
        if item.tag == "Point":
          for obj in item:
            if obj.tag == "coordinates":
#             style = 'point'
              coordinates = roundCoordinates(obj.text)
              addTo(points)
        elif item.tag == "LineString":
          for obj in item:
            if obj.tag == "coordinates":
#             style = 'way'
              coordinates = obj.text
              addTo(tracks)
      continue
    findPlacemark(placemark)

# Print human friendly formated XML
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, encoding='utf8', method="html")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

#print(ElementTree.tostring(kml, encoding="UTF-8", method="html"))



if __name__ == "__main__":
  try:
    reload(sys)
    sys.setdefaultencoding('utf8')
    len(sys.argv) == 2
    option = sys.argv[1]
    filename = sys.argv[2]
    tree = ElementTree.parse(filename)
    root = tree.getroot() 
    points = {}
    tracks = {}
    findPlacemark(root)
    kml = addRoot()
    document = addDoc('Document')
    kml.append(document)
    
    # Print points only
    if sys.argv[1] == "--points":
      folder = addFolder('Points')
      document.append(folder)
      for key in points.keys():
        folder.append(addPoint(points[key]['name'], points[key]['description'], key))
    # Print tracks only
    if sys.argv[1] == "--tracks":
      folder = addFolder('Tracks')
      document.append(folder)
      for key in tracks.keys():
        folder.append(addTrack(tracks[key]['name'], tracks[key]['description'], key))
    print(prettify(kml))

  except:
    print "Usage: " + os.path.basename(__file__) + "[ --points | --tracks] FILE"
    sys.exit(1)
