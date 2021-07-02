# QRadar_Redmine_Integration

The idea behind this project is to use the Redmine as a Ticketing System, by taking advantage of Issues Tracking feature.


                                BE AWARE, this is an EARLY DEV VERSION  

# About this document

**Draft (To Be Updated...)**


# How it works
  
  It works with `API CALLS` on both QRadar and Redmine Apps so it can run on a different server. 
  It checks for new QRadar Offenses and sync to Redmine.
  It checks if an Offense has been deleted from Qradar and removes it from Redmine.
  It checks if a Ticket is Closed (Redmine Issue Status that is marked as Closed Issue) and close it on QRadar.
  
  


# Give it a try

You have to update the variables at the start of the `main.py`, to get this Python script to work. The API-KEYS must have sufficient rights to add,edit,update 
or remove Qradar Offenses and Redmine Tickets.

You have to create at least to Custom Fields on Redmin Ticket, which the script uses to correlate the QRadar Offense ID and Redmine Ticket ID.
In this script i set them as `Offense ID` and `Domain`.

You have to use the API of both QRadar and Redmine to get some values that must set, like the Redmine Project ID, the QRadar closing reason ID e.t.c.

(Check the `main.py` to see the requirements)

It also creates a file (`open_offenses.txt`) that stores the last QRadar Offense ID and the last Redmine Ticket ID. (you can change it as you please.)

After you setup also these changes add it on a `crontab` or on `systemd` with timer and run it every `60s` or so. 


