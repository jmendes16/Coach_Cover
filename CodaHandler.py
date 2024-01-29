import requests
import pandas as pd

API_key = 'your_api_key'
doc_ID = 'your_document_ID'
table_ID = 'your_table_ID'

headers = {'Authorization' : f'Bearer {API_key}'}
url = f'https://coda.io/apis/v1/docs/{doc_ID}/tables/{table_ID}/rows'

response = requests.get(url, headers=headers).json()

table_data = [row['values'] for row in response.get('items')]

table = pd.DataFrame(table_data)
column_map = dict(zip(table.columns,['name','no_slots','notes','coach_booked']))
table.rename(columns=column_map,inplace=True)
table.drop('notes', axis=1 ,inplace=True)

print(table.head())

