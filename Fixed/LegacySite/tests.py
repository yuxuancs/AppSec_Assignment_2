
from django.test import TestCase,Client
import json,os,django
from shlex import quote
from LegacySite.models import User,Product,Card
from . import extras


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GiftcardSite.settings')
django.setup()
CARD_PARSER = 'giftcardreader'


class MyTest(TestCase):

    def __init__(self):
        super(MyTest,self).__init__()
        
    def test_1(self):
        resp = Client.get('/gift/',{'director': "<script>alert('XSS attack!')</script>"})
        string = bytes.decode(resp.content)
        if string.__contains__("&lt;script&gt"): # check whether "<" and ">" <=> "&lt" and "&gt"
            return "XSS Test passed!"
        else:
            return None

    def test_2(self):
        self.client = Client(enforce_csrf_checks=True)
        resp = self.client.post('/gift/1',{'amount':'1','username':'yuxuan_2'})
        if resp.status_code == 403:
            return "CRSF test passed!"
        else:
            return None

    def test_3(self):
        cf_data = open('part1/SQL_Injection_steal_password.gftcrd')
        cf_path = f'./tmp/SQLi_test_parser.gftcrd'
        card_data = extras.parse_card_data(cf_data.read(), cf_path)
        cf_data.close()
        signature = json.loads(card_data)['records'][0]['signature']
        card_query = Card.objects.raw('select id from LegacySite_card where data = %s', params=[signature])
        if len(card_query) == 0:
            return "SQL injection test passed!"
        else:
            return None

    def test_4(self):
        card_path_name = open('part1/Injection.txt')
        # KG: Are you sure you want the user to control that input?
        ret_val = os.system(quote(f"./{CARD_PARSER} 2 {card_path_name} > tmp_file"))
        if ret_val != 0:
            return "command injection passed!"
        else:
            return None
