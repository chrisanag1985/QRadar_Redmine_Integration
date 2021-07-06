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

TIP: Go to the custom field `Offense ID` and add to the `Link Values to URL`  https://qradar-host/console/qradar/jsp/QRadar.jsp?appName=Sem&pageId=OffenseSummary&summaryId=%value% so when you click on the `Offense ID` to open the specific Offense in the QRadar


  

You have to use the API of both QRadar and Redmine, to get some values that must be set before you begin, like the Redmine Project ID, the QRadar closing reason ID e.t.c.

To get the id and other info that will help you to edit the `config.ini` run the `helper.py`

(Check the `config.ini` to see these variables)


[QRADAR_DOMAINS]
0 = Default Domain
1 = Domain1


[REDMINE_CUSTOM_FIELDS]
3 = Offense ID
4 = Domain

[QRADAR_REDMINE_MAPPING]
id = Offense ID
domain_id = Domain
description = subject

[CUSTOM_FIELDS_IS_LIST]
4 = QRADAR_DOMAINS

Explanation:

The section `QRADAR_REDMINE_MAPPING` is mandatory in the `config.ini`. 

Moving on section `QRADAR_REDMINE_MAPPING`
This helps the Redmine to map the QRADAR field with the Redmine field. In this example we map the `id` (QRadar) with the `Offense ID` (Redmine Custom Field)
To get the QRadar fields see in the `Interactive API Documentation for Developers`, at the `/siem/offenses`. The Redmine Fields you can get it with `/issues.json`
For more check: https://www.redmine.org/projects/redmine/wiki/Rest_Issues


It also creates a file (`open_offenses.txt`) that stores the last QRadar Offense ID and the last Redmine Ticket ID. (you can change the filename and filepath as you please.)

After you setup all these variables, add it  on a `crontab` or on `systemd` with timer and run it every `60s` or so. 




