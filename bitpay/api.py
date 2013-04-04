import urllib2
import sys
import platform
import simplejson as json
from base64 import b64encode
from crypt import crypt
from bitpay import __version__


class BitPayValidationError(Exception):
    pass


class BitPayApi(object):
    _api_key = None
    _standard_headers = {'Content-Type': 'application/json',
                         'User-Agent': '%%s python-bitpay/%s Python/%s %s' % (__version__,
                                          sys.version.split()[0],
                                          platform.platform(True)),
                        }
    _api_base = 'https://bitpay.com/'
    _validate_pos_data = True
    
    def __init__(self, api_key=None, validate_pos_data=True):
        self._api_key = api_key
        self._validate_pos_data = validate_pos_data
        
    @property
    def api_key(self):
        return self._api_key
        
    def set_api_key(self, api_key):
        self._api_key = api_key
        
    def set_validate_pos_data(self, validate):
        self._validate_pos_data = bool(validate)
        
    @property
    def _authorization_header(self):
        if self._api_key is None:
            raise ValueError("Unable to build authorization headers without an API key")
        return {'Authorization': 'Basic %s' % b64encode(self._api_key),}
        
    def _send(self, url, data=None, post=False):
        headers = dict(self._standard_headers.items() + self._authorization_header.items())
        
        if post is True:
            headers['Content-Length'] = data.__len__()
        
        if data is not None and type(data) is dict:
            data = json.dumps(data)
        
        u = urllib2.urlopen(self._api_base, data)
        resp = u.request('POST' if post else 'GET', '/api/%s/' % url.rstrip('/'), data, headers)
        
        return json.loads(resp.read())
        
    def create_invoice(self, order_id, price, merch_info, **kwargs):
        options = ['orderID', 'itemDesc', 'itemCode', 'notificationEmail', 'notificationURL', 'redirectURL', 
            	   'posData', 'price', 'currency', 'physical', 'fullNotifications', 'transactionSpeed', 'buyerName', 
        		   'buyerAddress1', 'buyerAddress2', 'buyerCity', 'buyerState', 'buyerZip', 'buyerEmail', 'buyerPhone']
                   
        post = dict()
        post['orderID'] = order_id
        post['price'] = price
        if type(merch_info) is dict:
            merch_info = json.dumps(merch_info)
        elif type(merch_info) is not str:
            raise TypeError("Unable to serialize non-dict/non-str merchant info")
        if self._validate_pos_data:
            post['posData'] = {'posData': merch_info, 'hash': None,}
            post['posData']['hash'] = self.gen_hash(merch_info)
        else:
            post['posData'] = merch_info
        
        for key, value in kwargs.items():
            if key in options:
                post[key] = value
        
        return self._send('invoice', data=post, post=True)
        
    def get_invoice(self, order_id):
        response = self._send('invoice/%s' % order_id, post=False)
        if type(response) is dict:
            response['posData'] = json.loads(response['posData'])
        return response
        
    def validate_notification(self, notification_data, deep_check=True):
        if type(notification_data) is str:
            notification_data = json.loads(notification_data)
            
        if type(notification_data['posData']) is str:
            notification_data['posData'] = json.loads(notification_data['posData'])
            
        if self._validate_pos_data:
            if not self.check_pos_data_hash(notification_data):
                raise BitPayValidationError('authentication failed (bad hash)')
            notification_data['posData'] = notification_data['posData']['posData']
            
        if deep_check:
            bp_data = self.get_invoice(notification_data['orderID'])
            intersect = notification_data.intersection(bp_data)
            if set(o for o in notification_data.intersection(bp_data) if bp_data[o] != notification_data[o]).__len__() != 0:
                raise BitPayValidationError('authentication failed (tampered data)')
        
        return notification_data
        
    def gen_hash(self, data):
        return crypt(data, self._api_key)
    
    def check_pos_data_hash(self, data):
        return data['posData']['hash'] == self.gen_hash(data['posData'])