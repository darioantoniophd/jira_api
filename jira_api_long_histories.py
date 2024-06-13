import requests
import base64
import csv
from datetime import datetime


# Jira credentials
username = "dantonio@mzptec.com"

import os
from dotenv import load_dotenv

load_dotenv("/home/dario/Dropbox/ai/key.env",override=True)
api_token = os.environ['JIRA_API_KEY']

project_key = "V02"

# Construct the authorization header
credentials = f"{username}:{api_token}"
base64_credentials = base64.b64encode(credentials.encode()).decode()

# API endpoint URL
base_url = "https://mzptec.atlassian.net/rest/api/latest"

# Request headers
headers = {
    "Authorization": f"Basic {base64_credentials}",
    "Content-Type": "application/json"
}

# Initialize variables for pagination
start_at = 0
max_results = 50
total_issues = 0

all_issues = []

while True:
    params = {
        "jql": f"project={project_key}",
        "startAt": start_at,
        "maxResults": max_results,
    }

    response = requests.get(f"{base_url}/search", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)
        
        total_issues = data.get("total", 0)
        start_at += max_results
        
        if start_at >= total_issues:
            break
    else:
        print("Request failed:", response.content)
        break

print("Total issues retrieved:", len(all_issues))
	
csv_filename = "change_history.csv"

with open(csv_filename, "w", newline="") as csv_file:
	csv_writer = csv.writer(csv_file)
	input_format_duedate = "%Y-%m-%d %H:%M:%S.%f"  # Format of the input date string
	input_format_fromdate = "%d/%b/%y"  # Format of the input date string
	row = [
					'Key',
					'Summary',
					'Labels',
					'Change in From date',
					'Change in Due date',
					'Initial duration',
					'Change in Duration'
					]
	csv_writer.writerow(row)				

	for issue in all_issues:
				
		initial_start_date = None
		initial_due_date = None
		change_in_due_date = 0
		change_in_start_date = 0
		relevant_changes = None
				
		all_changelog_entries = []
		key = issue["key"]
		start_at = 0
		max_results = 100
		count = 0
					
		initial_start_date = None
		initial_due_date = None
		change_in_due_date = 0
		change_in_start_date = 0
		relevant_changes = None
		
		print(issue['key'],issue['fields']['summary'])
		
		while True:
			changelog_params = {
				"startAt": start_at,
				"maxResults": max_results
			}
			changelog_response = requests.get(f"{base_url}/issue/{key}/changelog", headers=headers, params=changelog_params)
			#print("Status code: ",changelog_response.status_code)
			#print(json.dumps(json.loads(changelog_response.text), sort_keys=True, indent=4, separators=(",", ": ")))
			
			changelog_data = changelog_response.json()
			
			histories = changelog_data.get("values", [])
	
			if not histories:
				break
	        
			all_changelog_entries.extend(histories)
	        
			start_at += max_results
	
			if start_at >= changelog_data["total"]:
				break

	
	
		
		
		
		for history in all_changelog_entries:
            # Filter history items related to start date or due date
			relevant_changes = [item for item in history['items'] if item['field'] in ['duedate', 'Start date']]
			if relevant_changes:
				for change in relevant_changes:
					try:
						if change['field'] == 'duedate':
							input_format = input_format_duedate
							if not change['fromString'] and change['toString']: 
								initial_due_date = datetime.strptime(change['toString'], input_format)
							if change['fromString'] and change['toString']:
								change_in_due_date = change_in_due_date + (datetime.strptime(change['toString'], input_format) - datetime.strptime(change['fromString'], input_format)).days
								
						elif change['field'] == 'Start date':
							input_format = input_format_fromdate
							if change['toString']:
								# Split the input date into day, month, and year components
								day, month_abbrev, year = change['toString'].split("/")
								# Capitalize the month abbreviation
								capitalized_month_abbrev = month_abbrev.capitalize()
								if capitalized_month_abbrev == 'Abr': capitalized_month_abbrev = 'Apr'
								if capitalized_month_abbrev == 'Ene': capitalized_month_abbrev = 'Jan'
								if capitalized_month_abbrev == 'Dic': capitalized_month_abbrev = 'Dec'
								if capitalized_month_abbrev == 'Ago': capitalized_month_abbrev = 'Aug'
								# Construct the formatted date
								change['toString'] = f"{day}/{capitalized_month_abbrev}/{year}"
								if not change['fromString']:
									initial_start_date = datetime.strptime(change['toString'], input_format)
									
							
							# Split the input date into day, month, and year components
								if change['fromString']:
									day, month_abbrev, year = change['fromString'].split("/")
									# Capitalize the month abbreviation
									capitalized_month_abbrev = month_abbrev.capitalize()
									if capitalized_month_abbrev == 'Abr': capitalized_month_abbrev = 'Apr'
									if capitalized_month_abbrev == 'Ene': capitalized_month_abbrev = 'Jan'
									if capitalized_month_abbrev == 'Dic': capitalized_month_abbrev = 'Dec'
									if capitalized_month_abbrev == 'Ago': capitalized_month_abbrev = 'Aug'
									# Construct the formatted date
									change['fromString'] = f"{day}/{capitalized_month_abbrev}/{year}"
									change_in_start_date = change_in_start_date + (datetime.strptime(change['toString'], input_format) - datetime.strptime(change['fromString'], input_format)).days
							
					except Exception as e:
					    # Print the standard error output
					    print("An exception occurred:", e)
		
				
		if initial_start_date and initial_due_date:
			initial_duration = (initial_due_date - initial_start_date).days
			row = [
			issue['key'],
			issue['fields']['summary'],
			issue['fields']['labels'],
			change_in_start_date,
			change_in_due_date,
			initial_duration,
			change_in_due_date-change_in_start_date
			]
			csv_writer.writerow(row)	
		elif relevant_changes:
			print('No pudo calcularse initial_duration')
			
	
	
				
