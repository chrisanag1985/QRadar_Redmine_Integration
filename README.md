# QRadar_Redmine_Integration

The idea behind this project is to use the Redmine as a Ticketing System, by taking advantage of Issues Tracking feature.


                                BE AWARE, this is an EARLY DEV VERSION  

# About this document

**Draft (To Be Updated...)**


# How it works
  
  It works with `API CALLS` on both QRadar and Redmine Apps, so this script can run on a different server. 
  It checks for new created QRadar Offenses and sync them to Redmine.
  It checks if an Offense has been deleted from Qradar and removes it from Redmine.
  It checks if a Ticket is Closed (Redmine Issue Status that is marked as closed Issue) and close it on QRadar.
  
  


# Give it a try

You have to update the variables at the beginning of the `main.py` file, to get this Python script to work. The `API-KEYS` must have sufficient rights to add,edit,update or remove Qradar Offenses and Redmine Tickets.

You have to create at least two Custom Fields on Redmin Ticket of the specific Project, which the script uses to correlate the QRadar Offense ID and Redmine Ticket ID.
In this script i set them as `Offense ID` and `Domain`.

You have to use the API of both QRadar and Redmine, to get some values that must set at start, like the Redmine Project ID, the QRadar closing reason ID e.t.c.

(Check the `main.py` to see the requirements)

It also creates a file (`open_offenses.txt`) that stores the last QRadar Offense ID and the last Redmine Ticket ID. (you can change the filename and filepath as you please.)

After you setup all these variables, add it  on a `crontab` or on `systemd` with timer and run it every `60s` or so. 


