import os
import requests
import json
import re

def get_account_list_from_reference_doc():
	directory_path = os.environ['PWD']
        reference_doc_path = os.path.join(directory_path, "Reference_standard.txt")

	file = open(reference_doc_path)
	lists = eval(file.read())

	stage_account_list = []
	
	for dict in lists:
		stage_account = dict['Username']
		if stage_account not in stage_account_list:
			stage_account_list.append(stage_account)

	print stage_account_list
	print len(stage_account_list)
	return stage_account_list	
		
def active_stage_account(url, login_list, password):
	for list in login_list:
    		s = requests.session()
    		s.verify = False

    		req1 = s.post(url, data={'_flowId': 'legacy-login-flow', 'failureRedirect': url,'username': list, 'password': password}, headers={'Accept-Language': 'en-US'})
    		print req1.url
    		assert req1.status_code == 200

    		req2 = s.post(req1.url, params={'_flowId': 'legacy-login-flow', '_flowExecutionKey': 'e1s1'}, data={'accepted': 'true', '_accepted': 'on', 'optionalTerms_28': 'accept', '_eventId_submit': 'Continue', '_flowExecutionKey': 'e1s1', 'redirect': ''})
    		#print req2.content
    		print req2.url
    		assert req2.status_code == 200

if __name__ == '__main__':
	url="https://www.stage.redhat.com/wapps/sso/login.html"
	account_list = get_account_list_from_reference_doc()
	password = "redhat"
	active_stage_account(url, account_list, password)

