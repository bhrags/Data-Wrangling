
# coding: utf-8

# # Data Wrangling- Open Street Map Project

# I have chosen Hyderabad as my osm file.
# sample osm file - 54mb(umcompressed)
# link - https://mapzen.com/data/metro-extracts/metro/hyderabad_india/
# 
# The city of smiles, of lights, of a thousand faces, endearingly called the Pearl City, Hyderabad offers a variety of tourist attractions ranging from Heritage monuments, Lakes and Parks, Gardens and Resorts, Museums to delectable cuisine and a delightful shopping experience. To the traveller, Hyderabad offers a fascinating panorama of the past, with a richly mixed cultural and historical tradition spanning 400 colourful years.

#     Questions explored 
#     1.Overabbreviated street names.
#     2.Finding inconcistent pincodes to differentiate hyderabad city from hyderabad district.Codes ranging from 500010 and 
#     500070 fall in the city and remainging fall outside.

# 1.Auditing the Street names

# In[2]:

import re
import pprint
from collections import defaultdict
import xml.etree.cElementTree as ET

osm_file="sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types=defaultdict(set)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons" , "Nagar" , "Road" , "Tank" , "Lake" , "Valley" , "Enclave" ,
            "Apartment" , "Colony" , "Sector" , "Park" , "Nivas" , "Mall" , "Centre" , "Plaza","Phase","Junction","Campus"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
street_types = defaultdict(set)
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if is_street_name(tag): 
                audit_street_type(street_types, tag.attrib['v'])



# In[3]:

#Listing the types of streets in our osm data
for i in street_types:
    print i


# In[4]:

#Cleaning the street names that are abbreviated by using Regular expression and updating them with a corrected street name.
from collections import defaultdict
import re
import pprint
import xml.etree.cElementTree as ET

mapping = { "St": "Street",
            "udyog":"Udyog",
            "chaulk":"Chowk",
            "St.": "Street",
            "Ave":"Avenue",
            "chowk":"Chowk",
            "EFLU" :"",
            "Rd":"Road",
            "cross":"Cross",
            "Rd.":"Road",
            "nagar":"Nagar",
            "road":"Road",
            "raod":"Road",
            "apartment":"Apartment",
            "no.":"",
            "ROADS" : "Roads",
            "colony" : "Colony",
            "NH7" :"Highway",
            "NAGAR":"Nagar",
            "RD":"Road",
           
            }

keys= mapping.keys() 

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
PROBLEMCHARS = re.compile(r'[=\+/&-<>;\'"\?%#$@\,\. \t\r\n]') 
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+') 

def update_street_name(name, mapping):

        m = street_type_re.search(name)
        if m:
            street_type=m.group()
    
            if street_type in keys:
                value=mapping[street_type]
                y=name.find(street_type)
                z=name[:y]+value
                return z

            else:
                try: 
            
                    type(int(street_type))
                    position=name.find(street_type)
                    remove_numbers=name[:position]
                    return remove_numbers
          
                except ValueError:
                    x = name.replace(", "," ").replace(" ,"," ").replace(" No.","").replace(" no.","").replace(",","")
                    return x


# In[5]:

for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way": 
        for tag in elem.iter("tag"):
            if is_street_name(tag):
                print "Before:",tag.attrib['v']
                print "After:",update_street_name(tag.attrib['v'], mapping)


# 2.Postal code Auditing

# In this step, the pincodes with white space characters are updated and the pincodes range is determined, whether they lie inside the city or not.

# In[6]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

pin_outside = []
pin_inside = []
i = 0
white_space=re.compile(r'\S+\s+\S+')
for event , elem in ET.iterparse(osm_file):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if tag.attrib['k'] == "postal_code" or tag.attrib['k'] == "addr:postcode":
                if white_space.search(tag.attrib['v']):
                    i=i+1
                    continue
                elif int(tag.attrib['v'].strip())<500010 or int(tag.attrib['v'].strip())>500070:
                     pin_outside.append(tag.attrib['v'])
                        
                elif int(tag.attrib['v'].strip())>500010 or int(tag.attrib['v'].strip())<500070:
                     pin_inside.append(tag.attrib['v'])
                        
print "Number of postal codes wrongly entered :",i                    
print "Number of Postal codes which line outside the city : ",len(pin_outside)
print "Number of Postal codes which belong to city limits 500010-500070 :",len(pin_inside)


# In the second iteration, the pincodes in string format and having ":" are identified. Both are updated as None.

# In[7]:

white_space=re.compile(r'\S+\s+\S+')
COLON= re.compile(r'^([a-z]|_)+:')
O="outside_city"
def update_pincode(pincode):
    if white_space.search(pincode):
        x=pincode.replace(" ","") 
        return x 
    elif tag.attrib['v']=='Vikrampuri':
         return None
    elif COLON.search(pincode):
         return None
    elif int(pincode)<500010 or int(pincode)>500070:
         return O
    else:
        return pincode


# In[8]:

for event, elem in ET.iterparse(osm_file):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if tag.attrib['k'] == "postal_code" or tag.attrib['k'] == "addr:postcode":
                print "Before :",tag.attrib['v']
                print "After :",update_pincode(tag.attrib['v'])


# After auditing is complete the next step is to prepare the data to be inserted into a SQL database. To do so we will parse the elements in the OSM XML file, transforming them from document format to tabular format, thus making it possible to write to .csv files. These csv files can then easily be imported to a SQL database as tables.

# In[9]:

import csv
import codecs
import pprint
import re 
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
   
    # YOUR CODE HERE
    if element.tag == 'node': 
        for k in element.attrib: 
            if k in NODE_FIELDS: 
                node_attribs[k]=element.attrib[k] 
        for y in element: 
            if y.tag=='tag': 
                node_tags = {}
                # tag k = 'addr:street' v = ' kormangala'
                # tag k = 'hourse ' v = 'asome'
                node_tags['id']=element.attrib['id'] 
                if LOWER_COLON.match(y.attrib['k']): 
                    
                    node_tags['key']=y.attrib['k'].split(":",1)[1] 
                    node_tags['type']=y.attrib['k'].split(":",1)[0] 
                else: 
                    node_tags['key'] = y.attrib['k']
                    node_tags['type'] = 'regular'
                    
                if y.attrib["k"] == 'addr:street':
                    if update_street_name(y.attrib["v"] , mapping):
                        node_tags["value"] = update_street_name(y.attrib["v"] , mapping)
                    else:
                        continue
                
                elif y.attrib["k"] == "addr:postcode":
                    if update_pincode(y.attrib["v"]):
                        node_tags["value"] = update_pincode(y.attrib["v"])
                    else:
                        continue
                else:
                    node_tags["value"] = y.attrib["v"]

                tags.append(node_tags)
                      
        return {'node': node_attribs, 'node_tags': tags} 
                
             

        
    elif element.tag == 'way': 
            for x in element.attrib: 
                if x in WAY_FIELDS: 
                    way_attribs[x]=element.attrib[x] 
            i=0 
            for q in element.iter("nd"): 
               
                way_nodes.append({'id':element.attrib['id'],'node_id':q.attrib['ref'],'position':i}) 
                i+=1 
            for y in element: 
                if y.tag=='tag': 
                    node_tags = {}
                    node_tags['id']=element.attrib['id']
                    if LOWER_COLON.match(y.attrib['k']): 
                         
                        node_tags['key']=y.attrib['k'].split(":",1)[1] 
                        node_tags['type']=y.attrib['k'].split(":",1)[0] 
                    else: 
                        node_tags['key'] = y.attrib['k']
                        node_tags['type'] = 'regular'
                    
                    if y.attrib["k"] == 'addr:street':
                        if update_street_name(y.attrib["v"] , mapping):
                            node_tags["value"] = update_street_name(y.attrib["v"] , mapping)
                        else:
                            continue
                    
                    elif y.attrib["k"] == "addr:postcode":
                        if update_pincode(y.attrib["v"]):
                            node_tags["value"] = update_pincode(y.attrib["v"])
                        else:
                            continue

                       
                    else:
                         node_tags["value"] = y.attrib["v"]
                        
                    tags.append(node_tags)
                   
            return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}       
    

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                    if element.tag == 'node':
                        nodes_writer.writerow(el['node'])
                        node_tags_writer.writerows(el['node_tags'])
                    elif element.tag == 'way':
                        ways_writer.writerow(el['way'])
                        way_nodes_writer.writerows(el['way_nodes'])
                        way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)

