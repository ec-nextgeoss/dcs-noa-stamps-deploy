'''
Created on 2 July 2020

@author: alex
'''

import os, sys
import traceback
import subprocess
import shutil
import smtplib
import datetime
import xml.etree.ElementTree as ET
from io import StringIO
import time

def set_datetime(xml_template, nst):
    dt_temp = xml_template.find(".//gco:DateTime",nst)
    now = datetime.datetime.now()
    nowst = now.strftime('%Y-%m-%dT%H:%M:%S')
    dt_temp.text=nowst
    
def set_date(xml_template, nst):
    dt_temp = xml_template.find(".//gco:Date",nst)
    now = datetime.datetime.now()
    datenowst = now.strftime('%Y-%m-%d')
    dt_temp.text=datenowst    

def set_tag(xml_batch, nsd, xml_template, nst, tag):
    dt_temp_parent = xml_template.find(".//%s/.."%tag,nst)
    for dt_temp in xml_template.findall(".//%s"%tag,nst):
        dt_temp_parent.remove(dt_temp)
    for dt_dyn in xml_batch.findall(".//%s"%tag,nsd):
        dt_temp_parent.append(dt_dyn)


def registerNameSpaces():    
    ET.register_namespace('gmd',"http://www.isotc211.org/2005/gmd")
    ET.register_namespace('gml',"http://www.opengis.net/gml")           
    ET.register_namespace('xsi',"http://www.w3.org/2001/XMLSchema-instance")
    ET.register_namespace('gts',"http://www.isotc211.org/2005/gts")
    ET.register_namespace('gco',"http://www.isotc211.org/2005/gco")
    ET.register_namespace('schemaLocation',"http://www.isotc211.org/2005/gmd http://www.isotc211.org/2005/gmd/gmd.xsd http://www.isotc211.org/2005/srv http://schemas.opengis.net/iso/19139/20060504/srv/srv.xsd")

def readxml(xmlfile):
    root = None
    nslist = None
    try: 
        with open(xmlfile,'r') as xml:
            xmlcontent = xml.read()
            root = ET.fromstring(xmlcontent)
            nslist = dict([ node for _, node in ET.iterparse( StringIO(unicode(xmlcontent, "utf-8")), events=['start-ns'] ) ])     
    except:
        traceback.print_exc()
    return root, nslist

def updatexml(inputfolder, templatefolder, outputfolder):
    registerNameSpaces()
    
    xml_template, nst = readxml(os.path.join(templatefolder,'CKAN_template.xml'))
    xml_batch, nsd  = readxml(os.path.join(inputfolder,'batch_info.xml'))
   
    set_datetime(xml_template, nst)
    set_date(xml_template, nst)
    set_tag(xml_batch, nsd, xml_template, nst, "gmd:descriptiveKeywords")
    set_tag(xml_batch, nsd, xml_template, nst, "gmd:geographicElement")
    set_tag(xml_batch, nsd, xml_template, nst, "gmd:temporalElement")
    set_tag(xml_batch, nsd, xml_template, nst, "gmd:supplementalInformation")
    set_tag(xml_batch, nsd, xml_template, nst, "gmd:distributionInfo")
    set_tag(xml_batch, nsd, xml_template, nst, "gmd:citation/gmd:CI_Citation/gmd:title")
    
    xmlst = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(xml_template)
    with open(os.path.join(outputfolder,'dynamic_info.xml'), "w") as xmlf: 
        xmlf.write(xmlst)


