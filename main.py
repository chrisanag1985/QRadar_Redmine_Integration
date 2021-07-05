import requests
import json
import configparser
from requests.utils import requote_uri
import sys
import os

requests.packages.urllib3.disable_warnings()

config_filename = 'config.ini'
qradar_domain_id = {}
open_ticketid_dict = {}
# {offense_id:ticket_id}
maxt = 0
maxq= 0


if os.path.isfile(config_filename):
	config = configparser.ConfigParser()
	config.sections()
	config.read(config_filename) 


	filestore = config['FILESTORE']
	qradar = config['QRADAR']
	qradar_domains = config['QRADAR_DOMAINS']
	redmine = config['REDMINE']

	filename_to_store_vars = filestore['filename_to_store_vars']

	qradar_api_key = qradar['qradar_api_key']
	if qradar_api_key == "":
		print("[+] Check your settings... QRadar API key is missing...")
		sys.exit()
	qradar_protocol = qradar['qradar_protocol']
	qradar_host = qradar['qradar_host']
	if qradar_host == "":
		print("[+] Check your settings... QRadar Host value is missing...")
	reason_id = int(qradar['reason_id'])

	for key in qradar_domains:
		keyint = int(key)
		qradar_domain_id[keyint] = qradar_domains[key]


	redmine_api_key = redmine['redmine_api_key']
	if redmine_api_key == "":
		print("[+] Check your settings... Script is terminating...")
		sys.exit()
	redmine_protocol = redmine['redmine_protocol']
	redmine_host = redmine['redmine_host']
	if redmine_host == "":
		print("[+] Check your settings... Redmine Host value is missing...")
	project_id = int(redmine['project_id'])
	offense_custom_field = redmine['offense_custom_field']
	offense_custom_field_id = int(redmine['offense_custom_field_id'])
	domain_custom_field = redmine['domain_custom_field']
	domain_custom_field_id = int(redmine['domain_custom_field_id'])

else:

	print("[+] The configuration file DOES NOT Exists!!!")
	sys.exit()





# Get  max offense_id:ticket_id 

def initialize():

	global open_ticketid_dict
	global maxt
	global maxq

	open_ticketid_dict = {}
	maxt = 0
	maxq= 0
	
	try:
		with open(filename_to_store_vars,'r') as f:

			line = f.readline()
			line = line.replace('\n','')
			maxq,maxt = line.split(':')
			maxq=int(maxq)
			maxt=int(maxt)
			#print("Maxq:%d ,Maxt:%d"%(maxq,maxt))	
		f.close()

	except FileNotFoundError:

		print("[+] File Not Found. Creating...")
		file = open(filename_to_store_vars,'w+')
		file.write('0:0')
		file.close()

"""
Redmine API Requests
"""


def get_redmine_ticket_offense_ids(project_id):

	total_tickets_count = 0

	headers = {'X-Redmine-API-Key':redmine_api_key,'Accept':'application/json'}
	
	try:
		r = requests.get(redmine_protocol+'://'+redmine_host+'/issues.json?project_id='+str(project_id),headers=headers)
		response = json.loads(r.text)
		total_tickets_count = response['total_count']
	except Exception as e:
		# print("[+] No Tickets Found")
		print("Error Found: "+e)
		
	
	print("[+] Total Tickets Count:%s"%total_tickets_count)

	if total_tickets_count > 0:
		for issue in response['issues']:
			ticket_id = issue['id']

			
			for custom_field in issue['custom_fields']:
				
				if custom_field['name'] == offense_custom_field:
					if custom_field['value'] != "":
							val = int(custom_field['value'])
							offense_id = custom_field['value']
							#print(ticket_id,offense_id)
							open_ticketid_dict[int(offense_id)] = int(ticket_id)
					else:
							print("[+] Ticket %d : Not a QRadar related issue."%ticket_id)
				


	return(open_ticketid_dict)


def post_redmine_new_issue(description,domain,offense_id):
	#returning ticket_id
	
	headers = {'X-Redmine-API-Key':redmine_api_key,'Content-Type':'application/json','Accept':'application/json'}
	payload = {'issue':{'project_id':project_id,'subject':description,'custom_fields':[{'id':offense_custom_field_id,'name':offense_custom_field,'value':offense_id},{'id':domain_custom_field_id,'name':domain_custom_field,'value': domain}]}}
	r = requests.post(redmine_protocol+'://'+redmine_host+'/issues.json',headers=headers,json=payload)
	response = json.loads(r.text)

	return(response['issue']['id'])

def close_ticket(ticket_id):

	print("Closing %d Ticket"%ticket_id)
	headers = {'X-Redmine-API-Key':redmine_api_key,'Content-Type':'application/json','Accept':'application/json'}
	payload = {'issue':{'status_id':4}}
	r = requests.put(redmine_protocol+'://'+redmine_host+'/issues/'+str(ticket_id)+'.json',headers=headers,json=payload)


"""
QRadar API Requests
"""

def get_qradar_offenses():

	headers= {'SEC':qradar_api_key,'Accept': 'application/json'}
	r = requests.get(qradar_protocol+'://'+qradar_host+'/api/siem/offenses',headers=headers,verify=False)
	return(r.text)


def get_offenses_in_open_offense_list(filter):

	headers =  {'SEC':qradar_api_key,'Accept': 'application/json'}
	url = qradar_protocol+'://'+qradar_host+'/api/siem/offenses?fields=id%2Cdomain_id%2Cdescription&filter=status%3D%22OPEN%22'
	r = requests.get(url,headers=headers,verify=False)
	return(r.text)




def close_offense(offense_id,reason_id):


	headers =  {'SEC':qradar_api_key,'Accept': 'application/json'}
	url = qradar_protocol+'://'+qradar_host+'/api/siem/offenses/'+str(offense_id)+'?closing_reason_id='+str(reason_id)+'&status=CLOSED'
	r = requests.post(url,headers=headers,verify=False)



#####################################################################################################################################

def check_for_new_offenses():

	global maxq
	global maxt

	qradar_open = {}
	qradar_offenses_list = []
	open_ticketid_dict = {}

	try:
		# this dict takes offense_id:ticket_id from redmine
		open_ticketid_dict = get_redmine_ticket_offense_ids(project_id)
		# print(open_ticketid_dict,type(open_ticketid_dict))

		
		#Get Qradar IDs in Open status
		x = get_offenses_in_open_offense_list(open_ticketid_dict.keys())
		qradar_offenses_dict = json.loads(x)
	except Exception as e:
		print(e)
		sys.exit()		


	
	for x in qradar_offenses_dict:
		qradar_offenses_list.append(x['id'])
		qradar_open[x['id']] = {'description':x['description'].replace('\n',''),'domain_id':x['domain_id']}


	tickets = open_ticketid_dict.keys()
	qids = qradar_offenses_list

	#exists in redmine
	d = tickets - qids
	#must me in order
	
	for i in d:
		print("[+] Ticket %d exists in Redmine. Closing Ticket to Redmine"%i)
		#close ticket offense
		close_ticket(open_ticketid_dict[i])

	#exists in qradar
	e = qids - tickets

	#must be in order

	for i in e:
		print("[+] Offense %d exists in Qradar"%i)
		#is new?
		if i > maxq:
			print("[+] New Offense. Sending to Redmine...")
			offense_id = i
			description = qradar_open[i]['description']
			domain = qradar_domain_id[qradar_open[i]['domain_id']]
			ticket_id =  post_redmine_new_issue(description,domain,offense_id)	
			maxt = ticket_id
			maxq = offense_id
		else:
			print("[+] Old Offense. Closing it...")
			#delete qradar offense
			close_offense(offense_id=i,reason_id=reason_id)

	with open(filename_to_store_vars,"w") as f:

		f.write(str(maxq)+":"+str(maxt))
		f.close()

	

#####################################################################################################################################


	
print("[+] Start Syncing...")
initialize()
check_for_new_offenses()
print("[+] Synced...")





