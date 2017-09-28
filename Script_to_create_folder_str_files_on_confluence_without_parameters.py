# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 10:46:37 2017
Script below replicates the provided folder, including subfolders and
files on Confluence.

Folder location, User ID and Password will need to be updated before running the script

@author: pratik.sule
"""
#Needed libraries

import xmlrpc.client,os,shutil,csv,glob, mimetypes

#Path for Folder to be copied 

folder_path = '' #Edit folder path here, replace \ with \\


#Confluence site details
site_URL = "https://confluence.cms.gov"
username = "" #Edit username here
pwd = "" #Edit password here
spacekey = "CCOSOA" #Specific to the Opera CMS Confluence Space

#Logging into Confluence
server = xmlrpc.client.ServerProxy(site_URL + "/rpc/xmlrpc")
token = server.confluence2.login(username, pwd)

#Set the parent page name under which you want the new pages to be
#created

root_parent_name = "CSR Recon"

root_parent_page = server.confluence2.getPage(token, spacekey, root_parent_name) 

print(root_parent_page)

blank_page = {'space': spacekey,'title': '','content':"",'parentId': ''}

child_list_content = """<p><ac:structured-macro ac:macro-id="985848d0-e19e-4d85-bec4-1189aa5f45a2" ac:name="children" ac:schema-version="2"/></p>
                     """

file_list_content = """<p><ac:structured-macro ac:macro-id="c91f310e-22ce-4dbe-a46f-66a5241f1720" ac:name="attachments" ac:schema-version="1"/></p>
                    """

both_list_content = """<p>
  <ac:structured-macro ac:macro-id="985848d0-e19e-4d85-bec4-1189aa5f45a2" ac:name="children" ac:schema-version="2"/>
</p>
<p> </p>
<p>
  <ac:structured-macro ac:macro-id="c91f310e-22ce-4dbe-a46f-66a5241f1720" ac:name="attachments" ac:schema-version="1"/>
</p>
"""

                    
#Parse the given folder structure to create pages and upload files

curr_parent_id = root_parent_page["id"]

print(curr_parent_id)

first_pass = True

content_text = ""

rootDir = folder_path
for dirName, subdirList, fileList in os.walk(rootDir):
    
    #get current directory name
    dir_tree = dirName.split("\\")
    dir_actual_name = dir_tree[-1]
    
    #Create page for current directory
    if subdirList:
        
        if fileList:
            
            content_text = both_list_content
        
        else:
            content_text = content_text + child_list_content
    else:
        
        content_text = file_list_content
    
    
    if first_pass:
        
        temp_page = {'space': spacekey,'title': dir_actual_name ,'content': content_text,'parentId': curr_parent_id}
    
        current_page = server.confluence2.storePage(token, temp_page)
        
        curr_parent_id = current_page["id"]
        
        first_pass = False
    else:
        
        current_parent_page = server.confluence2.getPage(token, spacekey, dir_tree[-2]) 
        
        curr_parent_id = current_parent_page["id"]
        
        temp_page = {'space': spacekey,'title': dir_actual_name ,'content': content_text,'parentId': curr_parent_id}
    
        current_page = server.confluence2.storePage(token, temp_page)

    
    #Upload files from current directory
    
    
    
    print('Found directory: %s' % dir_actual_name)
    
    if fileList:
        
        for fname in fileList:
            file = os.path.join(dirName, fname)
            with open(file, 'rb') as f:
                filedata = f.read()
                
            attachment = {};
            attachment['fileName'] = file;
            attachment['contentType'] = mimetypes.guess_type(file)[0] ;
            
            server.confluence2.addAttachment(token, current_page['id'], attachment, filedata)
         
            print('\t%s' % fname)   
            