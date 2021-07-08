import requests
import json
import configparser
import os
import sys

requests.packages.urllib3.disable_warnings()

config_filename = 'config.ini'



if os.path.isfile(config_filename):
	config = configparser.ConfigParser()
	config.sections()
	config.read(config_filename) 



	qradar = config['QRADAR']
	redmine = config['REDMINE']


	qradar_api_key = qradar['qradar_api_key']
	if qradar_api_key == "":
		print("[+] Check your settings... QRadar API key is missing...")
		sys.exit()
	qradar_protocol = qradar['qradar_protocol']
	qradar_host = qradar['qradar_host']
	if qradar_host == "":
		print("[+] Check your settings... QRadar Host value is missing...")


	redmine_api_key = redmine['redmine_api_key']
	if redmine_api_key == "":
		print("[+] Check your settings... Script is terminating...")
		sys.exit()
	redmine_protocol = redmine['redmine_protocol']
	redmine_host = redmine['redmine_host']
	if redmine_host == "":
		print("[+] Check your settings... Redmine Host value is missing...")
	

else:

	print("[+] The configuration file DOES NOT Exists!!!")
	sys.exit()

#GET /projects.json
def get_redmine_projects():


	headers = {'X-Redmine-API-Key':redmine_api_key,'Accept':'application/json'}
	
	
	r = requests.get(redmine_protocol+'://'+redmine_host+'/projects.json',headers=headers)
	response = json.loads(r.text)
	print("\nProjects:")
	for project in response['projects']:
		print("ID: %s  Name: %s "%(project['id'],project['name']))



#GET /issue_statuses.json
def get_redmine_issue_statuses():


	headers = {'X-Redmine-API-Key':redmine_api_key,'Accept':'application/json'}
	
	
	r = requests.get(redmine_protocol+'://'+redmine_host+'/issue_statuses.json',headers=headers)
	response = json.loads(r.text)
	print("\nIssue Statuses:")
	for issue_status in response['issue_statuses']:
		print("ID: %s  Name: %s   Close Issue: %s "%(issue_status['id'],issue_status['name'],issue_status['is_closed']))


#GET /issue_statuses.json
def get_redmine_trackers():


	headers = {'X-Redmine-API-Key':redmine_api_key,'Accept':'application/json'}
	
	
	r = requests.get(redmine_protocol+'://'+redmine_host+'/trackers.json',headers=headers)
	response = json.loads(r.text)
	print("\nTrackers:")
	for tracker in response['trackers']:
		print("ID: %s Name: %s"%(tracker['id'],tracker['name']))

#GET /custom_fields.json
def get_redmine_custom_fields():


	headers = {'X-Redmine-API-Key':redmine_api_key,'Accept':'application/json'}
	
	
	r = requests.get(redmine_protocol+'://'+redmine_host+'/custom_fields.json',headers=headers)
	response = json.loads(r.text)
	print("\nCustom Fields:")
	for custom_field in response['custom_fields']:
		print("ID: %s Name: %s Field Format: %s "%(custom_field['id'],custom_field['name'],custom_field['field_format']))
		if custom_field['field_format'] == 'list':
			for value in custom_field['possible_values']:
				print(value)


#https://qradar_host/api/config/domain_management/domains?fields=id%2Cdescription
def get_qradar_domains():

	headers= {'SEC':qradar_api_key,'Accept': 'application/json'}
	r = requests.get(qradar_protocol+'://'+qradar_host+'/api/config/domain_management/domains?fields=id%2Cname',headers=headers,verify=False)
	response = json.loads(r.text)
	print("\nQRadar Domains:")
	for domain in response:
		if domain['name'] == "":
			d = "Default Network"
		else:
			d = domain['name']
		print("ID: %d  Name: %s"%(domain['id'],d))

#GET - /siem/offense_closing_reasons
def get_qradar_closind_issues():

	headers= {'SEC':qradar_api_key,'Accept': 'application/json'}
	r = requests.get(qradar_protocol+'://'+qradar_host+'/api/siem/offense_closing_reasons?fields=id%2Ctext',headers=headers,verify=False)
	response = json.loads(r.text)
	print("\nQRadar Closing Issues:")
	for closing_issue in response:
		print("ID: %d Name: %s"%(closing_issue['id'],closing_issue['text']))



get_redmine_projects()
get_redmine_trackers()
get_redmine_issue_statuses()
get_redmine_custom_fields()
get_qradar_domains()
get_qradar_closind_issues()
