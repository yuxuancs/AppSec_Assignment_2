import pytest
from django.test import TestCase,Client
import json,os,django
from shlex import quote
#from LegacySite.models import User,Product,Card
from . import extras,models

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GiftcardSite.settings')
os.environ['DJANGO_SETTINGS_MODULE'] = 'GiftcardSite.settings'
django.setup()
CARD_PARSER = 'giftcardreader'


class MyTest(TestCase):

    def __init__(self):
        super(MyTest,self).__init__()
        
    def test_1(self):
        client = Client()
        resp = client.get('/gift/',{'director': "<script>alert('XSS attack!')</script>"})
#        string = bytes.decode(resp.content)
#        if string.__contains__("&lt;script&gt"): # check whether "<" and ">" <=> "&lt" and "&gt"
        if resp.status_code == 200:
            return "XSS attack successfully!"
        else:
            return None

    def test_2(self):
        client = Client(enforce_csrf_checks=True)
        resp = client.post('/gift/1',{'amount':'1','username':'yuxuan_2'})
        if resp.status_code == 200:
            return "CRSF attack successfully!"
        else:
            return None

    def test_3(self):
        cf_data = open('part1/SQL_Injection_steal_password.gftcrd').read()
        cf_path = f'./tmp/SQLi_test_parser.gftcrd'
        card_data = extras.parse_card_data(cf_data, cf_path)
        signature = json.loads(card_data)['records'][0]['signature']
        card_query = models.Card.objects.raw('select id from LegacySite_card where data = %s',params=[signature])
        if len(card_query) == 0:
            return "SQL Injection attack successfully!"
        else:
            return None

    def test_4(self):
        card_path_name = open('part1/Injection.txt').read()
        # KG: Are you sure you want the user to control that input?
        ret_val = os.system(f"./giftcardreader 2 {card_path_name} > tmp_file")
        print("+"*80)
        print(ret_val)
        print("+"*80)
        if ret_val == 0:
            return "Command Injection attack successfully!"
        else:
            return None

@pytest.mark.django_db
def run_test():
    test = MyTest()
    print('Runing test_1:')
    test1 = test.test_1()
    assert test1 != None, "XSS Error"
    print(test1)
    print('Runing test_2:')
    test2 = test.test_2()
    assert test2 != None, "CRSF Error"
    print(test2)
    print('Runing test_3:')
    test3 = test.test_3()
    assert test3 != None, "SQL Injection Error"
    print(test3)
    print('Runing test_4:')
    test4 = test.test_4()
    assert test4 != None, "Command Injection Error"
    print(test4)

run_test()

