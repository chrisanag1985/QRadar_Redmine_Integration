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
redmine_custom_fields_dict = {}
qradar_redmine_mapping_dict = {}
custom_fields_is_list_dict = {}
# {offense_id:ticket_id}
maxt = 0
maxq= 0


if os.path.isfile(config_filename):
	config = configparser.ConfigParser()
	config.sections()
	config.read(config_filename) 


	filestore = config['FILESTORE']
	qradar = config['QRADAR']
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



	redmine_api_key = redmine['redmine_api_key']
	if redmine_api_key == "":
		print("[+] Check your settings... Script is terminating...")
		sys.exit()
	redmine_protocol = redmine['redmine_protocol']
	redmine_host = redmine['redmine_host']
	if redmine_host == "":
		print("[+] Check your settings... Redmine Host value is missing...")
	project_id = int(redmine['project_id'])

	
	redmine_custom_fields = config['REDMINE_CUSTOM_FIELDS']
	qradar_redmine_mapping = config['QRADAR_REDMINE_MAPPING']
	custom_fields_is_list = config['CUSTOM_FIELDS_IS_LIST']
	map_qradar_domain_id_to_tracker = config['MAP_DOMAIN_TO_TRACKER']

	# one_dict must all be strings
	one_dict_to_rule_them_all = {}
	for key in qradar_redmine_mapping:
		qradar_field = key
		redmine_field = qradar_redmine_mapping[key]
		one_dict_to_rule_them_all[qradar_field] = {'map': redmine_field, 'attributes':{'isCustom':'False','isList':'False'}}
		for custom_id,custom_name in redmine_custom_fields.items():
			#is custom field?
			if custom_name == redmine_field:
				one_dict_to_rule_them_all[qradar_field]['attributes']['isCustom'] = 'True'
				one_dict_to_rule_them_all[qradar_field]['attributes']['custom_id'] = custom_id
				if custom_id in custom_fields_is_list.keys():
					one_dict_to_rule_them_all[qradar_field]['attributes']['isList'] = 'True'
					section_name = custom_fields_is_list[custom_id]
					custom_field_list_dict = config[section_name]
					tmp = {}
					for k,v in custom_field_list_dict.items():
						tmp[k] = v
					one_dict_to_rule_them_all[qradar_field]['attributes']['listValues'] = tmp
					tmp = {}
					if qradar_field == 'domain_id':
						for k,v in map_qradar_domain_id_to_tracker.items():
							tmp[k] = v
						one_dict_to_rule_them_all[qradar_field]['attributes']['map_qdomain_tracker'] =  tmp

	custom_field_offense = one_dict_to_rule_them_all['id']['map']
	#print(one_dict_to_rule_them_all)




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


def printer(x):
	print(x)
	print(x.status_code)
	print(x.headers)
	print(x.request)
	print(x.request.body)
	print(x.text)
	



def get_redmine_ticket_offense_ids(project_id):

	total_tickets_count = 0

	headers = {'X-Redmine-API-Key':redmine_api_key,'Accept':'application/json'}
	
	try:
		r = requests.get(redmine_protocol+'://'+redmine_host+'/issues.json?project_id='+str(project_id),headers=headers)
		response = json.loads(r.text)
		total_tickets_count = response['total_count']
	except Exception as e:
		# print("[+] No Tickets Found")
		print("Error Found: %s "%e)
		
	
	print("[+] Total Tickets Count:%s"%total_tickets_count)

	if total_tickets_count > 0:
		for issue in response['issues']:

			ticket_id = issue['id']
			

			
			for custom_field in issue['custom_fields']:

			
				if custom_field['name'] == custom_field_offense:
					
					if custom_field['value'] != "":
							val = int(custom_field['value'])
							offense_id = custom_field['value']
							# print(ticket_id,offense_id)
							open_ticketid_dict[int(offense_id)] = int(ticket_id)
					else:
							print("[+] Ticket %d : Not a QRadar related issue."%ticket_id)
				

	# print(open_ticketid_dict)
	return(open_ticketid_dict)




def do_payload(offense_reply_dict):


	payload_dict = {}

	payload_dict['issue'] = {'project_id':project_id}
	payload_dict['issue']['custom_fields'] = []

	for key in one_dict_to_rule_them_all.keys():
		
		if one_dict_to_rule_them_all[key]['attributes']['isCustom'] == 'True':
			#custom field
			#print(key,one_dict_to_rule_them_all[key]['map'],offense_reply_dict[key])
			tmp_val = offense_reply_dict[key]
			#check if is list and get the value
			if one_dict_to_rule_them_all[key]['attributes']['isList'] == 'True':
				tmp_val = one_dict_to_rule_them_all[key]['attributes']['listValues'][str(offense_reply_dict[key])]

			payload_dict['issue']['custom_fields'].append({'id': one_dict_to_rule_them_all[key]['attributes']['custom_id'] ,'name': one_dict_to_rule_them_all[key]['map'] ,'value': tmp_val  })
		else:
			#not custom field
			payload_dict['issue'][one_dict_to_rule_them_all[key]['map']] = offense_reply_dict[key].replace('\n','') 

	

	#print(payload_dict)
	
	
	return(payload_dict)



def post_redmine_new_issue(offense_dict):
	#returning ticket_id
	
	
	headers = {'X-Redmine-API-Key':redmine_api_key,'Content-Type':'application/json','Accept':'application/json'}
	payload = do_payload(offense_dict)

	r = requests.post(redmine_protocol+'://'+redmine_host+'/issues.json',headers=headers,json=payload)
	response = json.loads(r.text)
	# printer(r)

	return(response['issue']['id'])

def close_ticket(ticket_id):

	headers = {'X-Redmine-API-Key':redmine_api_key,'Content-Type':'application/json','Accept':'application/json'}
	payload = {'issue':{'status_id':4}}
	r = requests.put(redmine_protocol+'://'+redmine_host+'/issues/'+str(ticket_id)+'.json',headers=headers,json=payload)


"""
QRadar API Requests
"""


def get_offenses_in_open_offense_list(filter):

	headers =  {'SEC':qradar_api_key,'Accept': 'application/json'}
	url = qradar_protocol+'://'+qradar_host+'/api/siem/offenses?filter=status%3D%22OPEN%22'
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

		#Get Qradar IDs in Open status
		x = get_offenses_in_open_offense_list(open_ticketid_dict.keys())
		qradar_offenses_dict = json.loads(x)
	except Exception as e:
		print("Exception: %s . Terminating..."%e)
			


	
	for x in qradar_offenses_dict:
		qradar_offenses_list.append(x['id'])
		qradar_open[x['id']] = x


	tickets = open_ticketid_dict.keys()
	qids = qradar_offenses_list

	#exists in redmine
	d = tickets - qids

	#must me in order
	
	for i in d:
		print("[+] Offense %d exists in Redmine and not in QRadar. Closing Ticket %d to Redmine"%(i,open_ticketid_dict[i]))
		#close ticket offense
		close_ticket(open_ticketid_dict[i])

	#exists in qradar
	e = qids - tickets


	#must be in order

	for offense_id in e:
		print("[+] Offense %d exists in Qradar"%offense_id)
		#is new?
		if offense_id > maxq:
			print("[+] New Offense. Sending to Redmine...")
			ticket_id =  post_redmine_new_issue(qradar_open[offense_id])	
			maxt = ticket_id
			maxq = offense_id
		else:
			print("[+] Old Offense. Closing it...")
			#delete qradar offense
			close_offense(offense_id=offense_id,reason_id=reason_id)

	with open(filename_to_store_vars,"w") as f:

		f.write(str(maxq)+":"+str(maxt))
		f.close()

	

#####################################################################################################################################


	
print("[+] Start Syncing...")
initialize()
check_for_new_offenses()
print("[+] Synced...")





