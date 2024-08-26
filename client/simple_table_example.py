# A Simple Python program with the functionality of the `simple_table_example` Jupyter Notebook
# (c) 2024 Regents of the University of California
import requests
server_url = 'http://localhost:5001'
response = requests.get(server_url)
print('Server Routes')
print(response.json())
table_names = f'{server_url}/get_table_names'
response = requests.get(table_names)
print('Names of the hosted tables')
print(response.json())
print('Get the range of the Year Column of Nationwide Vote')
response = requests.get(f'{server_url}/get_range_spec?table_name=nationwide_vote&column_name=Year')
response.json()
print('Get the values of all of the parties that have ever run in the US')
response = requests.get(f'{server_url}/get_all_values?table_name=nationwide_vote&column_name=Party')
response.json()
print('Get the schema of the Presidential Vote Table')
response = requests.get(f'{server_url}/get_table_schema?table_name=presidential_vote')
response.json()
print('Show the years when a candidate named Roosevelt ran for the Presidency')
filter_name = {"operator": "REGEX_MATCH", "column": "Name", "expression": ".*Roosevelt.*"}
filter_state = {"operator": "IN_LIST", "column": "State", "values": ["Nationwide"]}
all_filter = {"operator": "ALL", "arguments": [filter_name, filter_state]}
query = {"table": "presidential_vote",  "filter": all_filter, "columns": ['Year', 'Name', 'Percentage']}
response = requests.post(f'{server_url}/get_filtered_rows', json = query)
response.status_code