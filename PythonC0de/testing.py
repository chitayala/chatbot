import os

import requests
question = "How will the OTP be sent to the customers?"

cloudSearchUrl = """
{}/2013-01-01/search?q={}&q.parser=simple&q.options={"defaultOperator":"or"}&return=_all_fields,_score&sort=_score+desc
"""
cloudSearchApi = "http://search-bank-bot-k4byqmxrpqcw2q4yevtz6aenoy.us-east-1.cloudsearch.amazonaws.com"

response = requests.get(url=cloudSearchUrl % (cloudSearchApi, question)).json()
print(response)
content = []
for item in response['hits']['hit'][:10]:
    content.append(item['fields']['answer'])

print(content)
