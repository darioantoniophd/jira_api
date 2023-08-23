import requests
import base64
import csv
from datetime import datetime


# Jira credentials
username = "dantonio@mzptec.com"
api_token = "ATATT3xFfGF0LLrcTvcNFN28uLylQ74MIgyLOgt6kYRqP79-WxdDy_UFFu2wHTTZsSf2rV7OF3yMQtMArG4EwTQdSioQPLlusMP2OZpOS15a4-_uK9eJrkweZ8YwTADMBPi4OaLg2BcGpl34IBIUxW4mxQshLTpFZzi_hHYC8m8ek2gxPgNOe6Y=AAC48005"
project_key = "V02"

# Construct the authorization header
credentials = f"{username}:{api_token}"
base64_credentials = base64.b64encode(credentials.encode()).decode()

# API endpoint URL
url = "https://mzptec.atlassian.net/rest/api/2/search"

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
        "expand": "changelog",
        "startAt": start_at,
        "maxResults": max_results,
    }

    response = requests.get(url, headers=headers, params=params)

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
					'Change in From date',
					'Change in Due date',
					'Change in Duration'
					]
	csv_writer.writerow(row)				

	for issue in all_issues:
		changelog = issue.get("changelog", {})
		histories = changelog.get("histories", [])
		change_in_due_date = 0
		change_in_from_date = 0
		for history in histories:
            # Filter history items related to start date or due date
			relevant_changes = [item for item in history['items'] if item['field'] in ['duedate', 'Start date'] and item['fromString']]
            
			if relevant_changes:
				for change in relevant_changes:
					try:
						
						if change['field'] == 'duedate':
							input_format = input_format_duedate
							change_in_due_date = change_in_due_date + (datetime.strptime(change['toString'], input_format) - datetime.strptime(change['fromString'], input_format)).days
								
						else:
							input_format = input_format_fromdate
						
							# Split the input date into day, month, and year components
							print(change['toString'])
							day, month_abbrev, year = change['toString'].split("/")
							# Capitalize the month abbreviation
							capitalized_month_abbrev = month_abbrev.capitalize()
							if capitalized_month_abbrev == 'Abr': capitalized_month_abbrev = 'Apr'
							if capitalized_month_abbrev == 'Ene': capitalized_month_abbrev = 'Jan'
							if capitalized_month_abbrev == 'Dic': capitalized_month_abbrev = 'Dec'
							if capitalized_month_abbrev == 'Ago': capitalized_month_abbrev = 'Aug'
							# Construct the formatted date
							change['toString'] = f"{day}/{capitalized_month_abbrev}/{year}"
							
							# Split the input date into day, month, and year components
							print(change['fromString'])
							day, month_abbrev, year = change['fromString'].split("/")
							# Capitalize the month abbreviation
							capitalized_month_abbrev = month_abbrev.capitalize()
							if capitalized_month_abbrev == 'Abr': capitalized_month_abbrev = 'Apr'
							if capitalized_month_abbrev == 'Ene': capitalized_month_abbrev = 'Jan'
							if capitalized_month_abbrev == 'Dic': capitalized_month_abbrev = 'Dec'
							if capitalized_month_abbrev == 'Ago': capitalized_month_abbrev = 'Aug'
							# Construct the formatted date
							change['fromString'] = f"{day}/{capitalized_month_abbrev}/{year}"
							change_in_from_date = change_in_from_date + (datetime.strptime(change['toString'], input_format) - datetime.strptime(change['fromString'], input_format)).days
							
					except Exception as e:
					    # Print the standard error output
					    print("An exception occurred:", e)
					
					
		row = [
			issue['key'],
			issue['fields']['summary'],
			change_in_from_date,
			change_in_due_date,
			change_in_due_date-change_in_from_date
			]
	   
		csv_writer.writerow(row)				
