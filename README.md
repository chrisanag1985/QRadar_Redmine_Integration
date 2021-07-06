# QRadar_Redmine_Integration

The idea behind this project is to use the Redmine as a Ticketing System, by taking advantage of Issues Tracking feature.


                                BE AWARE, this is an EARLY DEV VERSION  

# About this document

**Draft (To Be Updated...)**


# How it works
  
  - It works with `API CALLS` on both QRadar and Redmine Apps, so this script can run on a different server. 
  - It checks for new created QRadar Offenses and sync them to Redmine.
  - It checks if an Offense has been deleted from Qradar and removes it from Redmine.
  - It checks if a Ticket is Closed (Redmine Issue Status that is marked as closed Issue) and close it on QRadar.

# Give it a try

You have to update the variables at the `config.ini` file, to get this Python script to work. The `API-KEYS` must have sufficient rights to add,edit,update or remove Qradar Offenses and Redmine Tickets. (FYI: do not enter quotes in `config.ini`)

Variables in `config.ini`

	API-KEY = askdflkal-adfsfsdf-sdffafasdf

Get the project id from the `helper.py`

	project_id = 1 

This is the ID that the script will use to close the offenses at the QRadar. To get the `ID` go to QRADAR API : `/siem/offense_closing_reasons`

	reason_id = 2



You have to create at least two Custom Fields for Issues, The first is used by the script to correlate the QRadar Offense ID and Redmine Ticket ID.
In this script i set it by the name  `Offense ID` (Format: Text) and the second by the name  `Domain` (Format: List) which is used for mapping the QRadar Domain Management.

TIP: Go to the custom field `Offense ID` and add to the `Link Values to URL`  https://qradar-host/console/qradar/jsp/QRadar.jsp?appName=Sem&pageId=OffenseSummary&summaryId=%value% so when you click on the `Offense ID` to open the specific Offense in the QRadar

More specific about the Redmine custom field `Domain` (List).

Navigate to: `Custom fields` -> `Issues` -> `Domain`

Format: `List`

Name: `Domain`

Possible values: 
	
	Default Network
	Domain1


----------------------------------------------------------------------------------------------------------

## Mapping QRadar Offenses with Redmine Ticketing System

Example for `config.ini`


	[QRADAR_REDMINE_MAPPING]
	id = Offense ID
	domain_id = Domain
	description = subject


	[REDMINE_CUSTOM_FIELDS]
	3 = Offense ID
	4 = Domain


	[CUSTOM_FIELDS_IS_LIST]
	4 = QRADAR_DOMAINS


	[QRADAR_DOMAINS]
	0 = Default Network
	1 = Domain1


Explanation:

The sections `QRADAR_REDMINE_MAPPING`, `REDMINE_CUSTOM_FIELDS`, `CUSTOM_FIELDS_IS_LIST` are mandatory for the `config.ini`. 



- Section `QRADAR_REDMINE_MAPPING`

This helps you to map the QRADAR fields with the Redmine fields. In this example we map the `id` (QRadar Offense ID) with the `Offense ID` (Redmine Custom Field)
To see the QRadar possible fields that you can use, go to the  `Interactive API Documentation for Developers`, at the `/siem/offenses`. The Redmine's possible Fields you can get them from `/issues.json` or check: https://www.redmine.org/projects/redmine/wiki/Rest_Issues

- Section `REDMINE_CUSTOM_FIELDS` ,

For mapping the redmine `custom field id`  with the redmine `custom field name`. You can get more information by running the `helper.py`

- Section `CUSTOM_FIELDS_IS_LIST` 

For declaring the redmine custom fields that are `List` format and map them with a section in the `config.ini` which contains the possible values of the list.


----------------------------------------------------------------------------------------------------------
Example:

In this example we will map the `QRadar Domains` with the Redmine Custom Field `Domain` and in our example we will use the above `config.ini` .

FYI: When you request from the QRadar API to get the offenses, the QRadar returns in the offense payload among the other the  `{ domain_id : integer }`



Now at the Redmine API, if we run the `helper.py` (for our example) we get:


	Custom Fields:
	ID: 3 Name: Offense ID Field Format: string 
	ID: 4 Name: Domain Field Format: list 
	{'value': 'Domain1', 'label': 'Domain1'}
	{'value': 'Default Network', 'label': 'Default Network'}



As we see before in the above `config.ini` the custom field `Domain` has ID: 4 
Now  at the `config.ini` we add below the `CUSTOM_FIELDS_IS_LIST` the value ` 4 = QRADAR_DOMAINS` which map the custom id 4
with a section in the `config.ini` with the name `QRADAR_DOMAINS` (this name is dynamic and you can put the name you wish as long as it is the same name with the section).

Now we add a section `QRADAR_DOMAINS` in the `config.ini` and we add below this section the values with the format

	QRadar domain_id = Redmine Custom Field List Value

e.g

	0  = Default Network

For QRadar you can get these values from the API:

https://qradar_host/api/config/domain_management/domains?fields=id%2Cname


----------------------------------------------------------------------------------------------------------



It also creates a file (`open_offenses.txt`) that stores the last QRadar Offense ID and the last Redmine Ticket ID. (you can change the filename and filepath as you please.)

After you setup all these variables, add it  on a `crontab` or on `systemd` with timer and run it every `60s` or so. 




