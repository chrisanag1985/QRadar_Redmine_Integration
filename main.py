import requests
import json
from requests.utils import requote_uri

requests.packages.urllib3.disable_warnings()


"""
VARIABLES

"""
filename_to_store_vars = 'open_offenses.txt'

"""

 QRADAR

"""
# Get the reason ID from qradar API you want to close the offense in QRadar
# fqdn or IP
qradar_api_key ='<QRADAR-API-KEY>'
qradar_protocol = 'https'
qradar_host = '<FQDN OR IP>'
# Insert the reason ID you want to close the offense. You can get the ID from QRADAR API
reason_id = 2

#curl -S -X GET -u admin  -H 'Version: 15.0' -H 'Accept: application/json' 'https://qradar_host/api/config/domain_management/domains'

qradar_domain_id = {
	
	0 : 'Domain1',
	1:  'Domain2'

}

"""

REDMINE

"""
redmine_api_key = '<REDMINE-API-KEY>'
redmine_protocol = 'http'
redmine_host = '<FQDN OR IP>'
# Redmine Project ID you want to sync
project_id = 1
offense_custom_field = "Offense ID"
domain_custom_field = "Domain"




"""
DO NOT EDIT BELOW THIS LINE

"""
#####################################################################################################################################


open_ticketid_dict = {}
# {offense_id:ticket_id}
maxt = 0
maxq= 0


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




def get_redmine_ticket_offense_ids(project_id):

	total_tickets_count = 0
	

	#curl -X GET -H "X-Redmine-API-Key':'<api-key>"  http://redmine/issue_statuses.json

	headers = {'X-Redmine-API-Key':redmine_api_key,'Accept':'application/json'}
	
	r = requests.get(redmine_protocol+'://'+redmine_host+'/issues.json?project_id='+str(project_id),headers=headers)


	try:
		response = json.loads(r.text)
		total_tickets_count = response['total_count']
	except:
		print("[+] No Tickets Found")

	
	print("[+] Total Tickets Count:%s"%total_tickets_count)

	if total_tickets_count > 0:
		for issue in response['issues']:
			ticket_id = issue['id']

			#print(issue['custom_fields'])

			for custom_field in issue['custom_fields']:
				if custom_field['name'] == offense_custom_field:
					try:
						val = int(custom_field['value'])
						offense_id = custom_field['value']
						#print(ticket_id,offense_id)
						open_ticketid_dict[int(offense_id)] = int(ticket_id)
					except:
						
						print("[+] Ticket %d : Not a QRadar related issue."%ticket_id)
				


	return(open_ticketid_dict)

"""
QRadar Offense
--------------

curl -S -X GET -u admin -H 'Range: items=0-49' -H 'Version: 15.0' -H 'Accept: application/json' 'https://qradar_host/api/siem/offenses?filter=id%3E2'


{'last_persisted_time': 1624958408000, 'username_count': 1, 'description': 'Access Permitted\n', 
'rules': [{'id': 100439, 'type': 'CRE_RULE'}], 'event_count': 88, 'flow_count': 0, 'assigned_to': None, 'security_category_count': 1, 
'follow_up': False, 'source_address_ids': [1], 'source_count': 1, 'inactive': True, 'protected': False, 'closing_user': None, 
'destination_networks': ['Net-10-172-192.Net_192_168_0_0'], 'source_network': 'Net-10-172-192.Net_192_168_0_0', 'category_count': 1, 'close_time': None, 'remote_destination_count': 0, 
'start_time': 1623392293060, 'magnitude': 4, 'last_updated_time': 1624956511662, 'credibility': 3, 'id': 1, 'categories': ['Access Permitted'], 'severity': 5, 'policy_category_count': 0, 
'log_sources': [{'type_name': 'EventCRE', 'type_id': 18, 'name': 'Custom Rule Engine-8 :: qradar', 'id': 63}], 'closing_reason_id': None, 'device_count': 1, 
'first_persisted_time': 1623392295000, 'offense_type': 0, 'relevance': 3, 'domain_id': 0, 'offense_source': '192.168.168.166', 'local_destination_address_ids': [1], 
'local_destination_count': 1, 'status': 'OPEN'}
"""


def post_redmine_new_issue(description,domain,offense_id):
	#returning ticket_id
	
	headers = {'X-Redmine-API-Key':redmine_api_key,'Content-Type':'application/json','Accept':'application/json'}
	payload = {'issue':{'project_id':project_id,'subject':description,'custom_fields':[{'id':3,'name':offense_custom_field,'value':offense_id},{'id':4,'name':domain_custom_field,'value': domain}]}}
	r = requests.post(redmine_protocol+'://'+redmine_host+'/issues.json',headers=headers,json=payload)
	response = json.loads(r.text)

	return(response['issue']['id'])


def get_qradar_offenses():

	headers= {'SEC':qradar_api_key,'Accept': 'application/json'}
	r = requests.get(qradar_protocol+'://'+qradar_host+'/api/siem/offenses',headers=headers,verify=False)
	return(r.text)


def get_offenses_in_open_offense_list(filter):

	headers =  {'SEC':qradar_api_key,'Accept': 'application/json'}
	url = qradar_protocol+'://'+qradar_host+'/api/siem/offenses?fields=id%2Cdomain_id%2Cdescription&filter=status%3D%22OPEN%22'
	r = requests.get(url,headers=headers,verify=False)
	return(r.text)

def close_ticket(ticket_id):

	#curl -X GET -H "X-Redmine-API-Key':'api-key"  http://redmine/issue_statuses.json
	print("Closing %d Ticket"%ticket_id)
	headers = {'X-Redmine-API-Key':redmine_api_key,'Content-Type':'application/json','Accept':'application/json'}
	payload = {'issue':{'status_id':4}}
	r = requests.put(redmine_protocol+'://'+redmine_host+'/issues/'+str(ticket_id)+'.json',headers=headers,json=payload)


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

	# this dict takes offense_id:ticket_id from redmine
	open_ticketid_dict = get_redmine_ticket_offense_ids(project_id)
	# print(open_ticketid_dict,type(open_ticketid_dict))

	
	#Get Qradar ID in Open status
	x = get_offenses_in_open_offense_list(open_ticketid_dict.keys())
	qradar_offenses_dict = json.loads(x)
	# print(qradar_offenses_dict)


	
	for x in qradar_offenses_dict:
		qradar_offenses_list.append(x['id'])
		qradar_open[x['id']] = {'description':x['description'].replace('\n',''),'domain_id':x['domain_id']}


	t = open_ticketid_dict.keys()
	q = qradar_offenses_list

	#exists in redmine
	d = t - q
	#must me in order
	
	for i in d:
		print("[+] Ticket %d exists in Redmine. Closing Ticket to Redmine"%i)
		#close ticket offense
		close_ticket(open_ticketid_dict[i])

	#exists in qradar
	e = q - t

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





