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



You have to create at least two Custom Fields on Redmin Ticket of 'Ticketing System Project', which the script uses to correlate the QRadar Offense ID and Redmine Ticket ID.
In this script i set them as `Offense ID` (Format: Text) and `Domain` (Format: List) .

At the custom field `Domain` (List) you have to add the Domain Names as you put it to the `config.ini`.

----------------------------------------------------------------------------------------------------------

Example For Custom Field `Domain`:

Custom fields- > Issues -> Domain

Format: List

Name: Domain

Possible values: 
	
	Default Network

	Domain1


----------------------------------------------------------------------------------------------------------


TIP: Go to the custom field `Offense ID` and add to the `Link Values to URL`  https://qradar-host/console/qradar/jsp/QRadar.jsp?appName=Sem&pageId=OffenseSummary&summaryId=%value% so when you click on the `Offense ID` to open the specific Offense in the QRadar


  

You have to use the API of both QRadar and Redmine, to get some values that must be set before you begin, like the Redmine Project ID, the QRadar closing reason ID e.t.c.

To get the id and other info that will help you to edit the `config.ini` run the `helper.py`

(Check the `config.ini` to see these variables)


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

0 = Default Domain

1 = Domain1


Explanation:

The sections `QRADAR_REDMINE_MAPPING`, `REDMINE_CUSTOM_FIELDS`, `CUSTOM_FIELDS_IS_LIST` are mandatory in the `config.ini`. 

Moving on section `QRADAR_REDMINE_MAPPING`
This helps the Redmine to map the QRADAR field with the Redmine field. In this example we map the `id` (QRadar) with the `Offense ID` (Redmine Custom Field)
To get the QRadar fields see in the `Interactive API Documentation for Developers`, at the `/siem/offenses`. The Redmine Fields you can get it with `/issues.json`
For more check: https://www.redmine.org/projects/redmine/wiki/Rest_Issues

At the section `REDMINE_CUSTOM_FIELDS` you map the redmine `custom field id`  with the redmine `custom field name`. You can get this info by running the `helper.py`

At the section `CUSTOM_FIELDS_IS_LIST` is for all the redmine custom fields that are format `List`. Now you have to map the redmine `custom field id` with the section that contains the possible values of the list. Maybe that sounds complicated so lets see this with an example.



----------------------------------------------------------------------------------------------------------
Example:

In this example we will map the `QRadar Domains` with the Redmine Custom Field `Domain` and we will use the above `config.ini` .

Disclaimer: the QRadar returns in the offense the `{ domain_id : interger }`

As we see before in the above `config.ini` the custom field `Domain` has ID: 4 
Now we add below the `CUSTOM_FIELDS_IS_LIST` the value ` 4 = QRADAR_DOMAINS` which map the custom id 4
with a section in the `config.ini` with the name `QRADAR_DOMAINS`.

Now we add a section `QRADAR_DOMAINS` in the `config.ini` and we add below this the values with the setup

QRadar domain_id = Redmine Custom Field List Value

0  = Default Network

For QRadar i got these values by running at the API:

https://qradar_host/api/config/domain_management/domains?fields=id%2Cname


----------------------------------------------------------------------------------------------------------





It also creates a file (`open_offenses.txt`) that stores the last QRadar Offense ID and the last Redmine Ticket ID. (you can change the filename and filepath as you please.)

After you setup all these variables, add it  on a `crontab` or on `systemd` with timer and run it every `60s` or so. 




