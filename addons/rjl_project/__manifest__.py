# -*- coding: utf-8 -*-

##############################################################################
#
#    HZ
#    Copyright (C) 2017.
#
##############################################################################

{
    "name":"Rajalistrik Project",
    "version":"1.0",
    "category":"RJL",
    'sequence': 1,
    "depends":['base', 'project', 'purchase', 'sale', 'account', 'hr', 'hr_expense', 'web_gantt_view'],
    "data":[
        'wizard/update_progression_status_views.xml',
        'views/project_views.xml',
    	'security/rjl_project_security.xml',
        ],
    "active":True,
    "installable":True
}
