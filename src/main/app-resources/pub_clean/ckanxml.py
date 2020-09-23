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
import re
import storeterradue

# Sentinel Monitor modules
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

def copy_tag(xml_batch, nsd, xml_template, nst, tag):
    dt_temp_parent = xml_template.find(".//%s/.."%tag,nst)
    for dt_temp in xml_template.findall(".//%s"%tag,nst):
        dt_temp_parent.remove(dt_temp)
    for dt_dyn in xml_batch.findall(".//%s"%tag,nsd):
        dt_temp_parent.append(dt_dyn)
        
def delete_tag(xmlelem, ns, tag):
    elem_parent = xmlelem.find(".//%s/.."%tag,ns)
    for elem in xmlelem.findall(".//%s"%tag,ns):
        elem_parent.remove(elem)
        
def set_tag(xml_template, nst, tag, value):
    tagel = xml_template.find(".//%s"%tag,nst)
    tagel.text = value
    
def append_tag(xml_batch, nsd, xml_template, nst, tag):
    sourcetag = xml_batch.find(".//%s"%tag,nsd)
    targettag, targetparent = get_tag_and_parent(xml_template, nst, tag)
    apptext = sourcetag.text if sourcetag.text is not None else ""
    sourcetag.text = targettag.text + apptext
    source_elem_st = ET.tostring(sourcetag)
    new_target_elem = ET.fromstring(source_elem_st)
    targetparent.remove(targettag)
    targetparent.append(new_target_elem)
    
def get_tag_value(xmlelem, ns, tag):
    tagel = xmlelem.find(".//%s"%tag,ns)
    return tagel.text

def get_tag_and_parent(xml_template, nst, tag):
    elem_parent = xml_template.find(".//%s/.."%tag, nst)
    elem = xml_template.find(".//%s"%tag, nst)
    return elem, elem_parent

def append_element(elem, elem_parent):
    elem_st = ET.tostring(elem)
    newelem = ET.fromstring(elem_st)
    elem_parent.append(newelem)
    
def set_distributioninfo(distinfo, ns, text, link):
    description = distinfo.find(".//gmd:description/gco:CharacterString", ns)
    description.text = text
    url = distinfo.find(".//gmd:linkage/gmd:URL", ns)
    url.text = link
    
def get_harvestname(xml_batch, nsd):
    titletag=xml_batch.find(".//gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString",nsd)
    harvestnamesafe="".join([c for c in titletag.text if re.match(r'\w', c)])
    harvestnamesafe = harvestnamesafe if len(harvestnamesafe)<15 else harvestnamesafe[0:14]
    return harvestnamesafe

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
        if not os.path.isfile(xmlfile):
            raise Exception('File %s does not exist'%xmlfile)
        with open(xmlfile,'r') as xml:
            xmlcontent = xml.read()
            root = ET.fromstring(xmlcontent)
            nslist = dict([ node for _, node in ET.iterparse( StringIO(unicode(xmlcontent, "utf-8")), events=['start-ns'] ) ])     
    except:
        traceback.print_exc()
    return root, nslist

def initialize(inputfolder, templatefolder, outputfolder):
    registerNameSpaces()
    
    templatefile = 'CKAN_template.xml'
    batchinfofile ='batch_info.xml'

    xml_template, nst = readxml(os.path.join(templatefolder,templatefile))
    if xml_template is  None:
        raise Exception("Unable to read template "+os.path.join(templatefolder,templatefile))
    xml_batch, nsd  = readxml(os.path.join(inputfolder,batchinfofile))
    if xml_batch is None:
        raise Exception("Unable to read batch info "+os.path.join(inputfolder,batchinfofile))
    
    return xml_batch, nsd, xml_template, nst

def updatexml(inputfolder, templatefolder, outputfolder):
    
    outputfile = 'ckaninfo.xml'
    
    xml_batch, nsd, xml_template, nst = initialize(inputfolder, templatefolder, outputfolder)
    
    set_datetime(xml_template, nst)
    set_date(xml_template, nst)
    #copy_tag(xml_batch, nsd, xml_template, nst, "gmd:descriptiveKeywords")
    copy_tag(xml_batch, nsd, xml_template, nst, "gmd:geographicElement")
    copy_tag(xml_batch, nsd, xml_template, nst, "gmd:temporalElement")
    copy_tag(xml_batch, nsd, xml_template, nst, "gmd:supplementalInformation")
    copy_tag(xml_batch, nsd, xml_template, nst, "gmd:citation/gmd:CI_Citation/gmd:title")
    append_tag(xml_batch, nsd, xml_template, nst, "gmd:abstract/gco:CharacterString")

    APIkey, repo, uname, store = storeterradue.getAPIrepo()
    harvestdir = get_harvestname(xml_batch, nsd)
    kmlfile = 'gevelo.kml'
    jpgfile = 'plotvdo.jpg'

    dinfoel, dinfo_parent = get_tag_and_parent(xml_template, nst, 'gmd:distributionInfo')
    delete_tag(xml_template, nst, 'gmd:distributionInfo')
    #append 2 new distributioninfo tags
    append_element(dinfoel, dinfo_parent)
    append_element(dinfoel, dinfo_parent)

    distinfolist = [['Velocities in JPG format', "{0}/{1}/{2}/{3}".format(store,repo,harvestdir, jpgfile)], \
                    ['Velocities in KML format', "{0}/{1}/{2}/{3}".format(store,repo,harvestdir, kmlfile)]]
    
    i=0
    for distinfo in xml_template.findall(".//gmd:distributionInfo",nst):
        set_distributioninfo(distinfo, nst, distinfolist[i][0], distinfolist[i][1])
        i+=1

    xmlst = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(xml_template)
    with open(os.path.join(outputfolder,outputfile), "w") as xmlf:
        xmlf.write(xmlst)
        
    return harvestdir

#folder=r'C:\Users\alex\Documents\Projects\NOA 1 interferogram\STAMPS\sandbox'
#updatexml(folder, folder, folder)
