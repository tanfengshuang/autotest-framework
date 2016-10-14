import requests

url = "http://mail.163.com/"
s = requests.session()
s.verify = False
#req1 = s.post(url, data={"idInput": "tanfengshuang@163.com", 'pwdInput': "**7260593shuang"})
#req1 = requests.post(url, data={"idInput": "tanfengshuang@163.com", 'pwdInput': "**7260593shuang"}, headers={'content-type': 'text/css'})
req1 = requests.get(url,auth=("tanfengshuang@163.com", "**7260593shuang"))
print req1.content

#s = requests.session()
#s.verify = False
#url = "https://mojo.redhat.com/docs/DOC-26756"
#login_name = "ftan"
#login_passwd = "rui<TAN2"
#req = s.get(url, auth=(login_name, login_passwd))#, headers={'Accept-Language': 'en-US'})
#print req.content

