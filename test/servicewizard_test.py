
import os, sys
import timeit
testdir = os.path.dirname(os.path.abspath(__file__))

import unittest


import timeit

from biokbase.ServiceWizard.Impl import ServiceWizard
try:
            from ConfigParser import ConfigParser
except ImportError:
            from configparser import ConfigParser

class RunTesterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cp = ConfigParser()
        cp.read(testdir + '/../test.cfg')

        config = {
            'rancher-compose-bin': testdir+'/../bin/rancher-compose',
            'rancher-env-url': 'http://127.0.0.1:8080',
            'catalog-url': 'https://ci.kbase.us/services/catalog',
            'catalog-admin-token': '',
            'auth-service-url': 'https://ci.kbase.us/services/auth/api/legacy/KBase/Sessions/Login',
            'auth-service-url-allow-insecure': False,
            'rancher-compose-bin': 'rancher-compose',
            'kbase-endpoint': 'https://ci.kbase.us/services',
            'temp-dir': testdir+'/temp',
            'access-key': '',
            'secret-key': ''
        }
	cls.v1 = '1.0.0'
	cls.v2 = '1.1.0'

        for item in cp.items('ServiceWizard'):
                config[item[0]] = item[1]
        cls.token = config['catalog-admin-token']

        cls.ctx = {'token':'asdf', 'user_id': 'auser'}
        cls.service = 'helloservice'
        cls.service_name = 'HelloService'

        cls.wiz = ServiceWizard(config)


    def test_start(self):

        # check the status of helloservice v1, this should start things up.
        # Start v1
        start = timeit.default_timer()
        self.wiz.start(self.ctx,{'module_name':self.service,'version': self.v1})
        status = self.wiz.get_service_status(self.ctx,{'module_name':self.service,'version': self.v1})[0]
        stop = timeit.default_timer()
        self.assertEquals(status['up'] , 1)
        print('took ' + str(stop-start) + 's');

        # checking status again should be much faster
        start = timeit.default_timer()
        status = self.wiz.get_service_status(self.ctx,{'module_name':self.service,'version': self.v1})[0]
        stop = timeit.default_timer()
        self.assertEquals(status['up'] , 1)
        print('took ' + str(stop-start) + 's');

        status = self.wiz.stop(self.ctx,{'module_name':self.service,'version': self.v1})[0]

    def test_start_two(self):
        self.wiz.start(self.ctx,{'module_name':self.service,'version': self.v1})
        status = self.wiz.get_service_status(self.ctx,{'module_name':self.service,'version': self.v1})[0]
        self.assertEquals(status['up'] , 1)
        self.wiz.start(self.ctx,{'module_name':self.service,'version': self.v2})
        status = self.wiz.get_service_status(self.ctx,{'module_name':self.service,'version': self.v2})[0]
        self.assertEquals(status['up'] , 1)

        # listing status
        status_list = self.wiz.list_service_status(self.ctx,{})[0]
        ct = 0
        for s in status_list:
            if s['module_name']==self.service_name and s['version'] == self.v1:
                self.assertEquals(s['up'] , 1)
                ct += 1
            if s['module_name']==self.service_name and s['version'] == self.v2:
                self.assertEquals(s['up'] , 1)
                ct += 1
        self.assertEquals(ct, 2)

        # starting something that is already running should be fine, start and list status again
        status = self.wiz.start(self.ctx,{'module_name':self.service,'version': self.v2})[0]
        self.assertEquals(status['up'] , 1)

        # Stop v2 and make sure the other stays up
        status = self.wiz.stop(self.ctx,{'module_name':self.service,'version': self.v2})[0]
        self.assertEquals(status['up'] , 0)
        status = self.wiz.get_service_status(self.ctx,{'module_name':self.service,'version': self.v1})[0]
        self.assertEquals(status['up'] , 1)

        # status list should show that just one is stopped
        status_list = self.wiz.list_service_status(self.ctx,{})[0]
        ct = 0
        for s in status_list:
            if s['module_name']==self.service_name and s['version'] == self.v1:
                self.assertEquals(s['up'] , 1)
                ct += 1
            if s['module_name']==self.service_name and s['version'] == self.v2:
                self.assertEquals(s['up'] , 0)
                ct += 1
        self.assertEquals(ct, 2)

        # stop the other one too
        status = self.wiz.stop(self.ctx,{'module_name':self.service,'version': self.v1})[0]
        self.assertEquals(status['up'] , 0)
        status_list = self.wiz.list_service_status(self.ctx,{})[0]
        for s in status_list:
            if s['module_name']==self.service_name and self.v1 in s['release_tags']:
                self.assertEquals(status['up'] , 0)
            if s['module_name']==self.service_name and self.v2 in s['release_tags']:
                self.assertEquals(status['up'] , 0)


        # now start back up just one
        status = self.wiz.start(self.ctx,{'module_name':self.service,'version': self.v2})[0]
        self.assertEquals(status['up'] , 1)
        status_list = self.wiz.list_service_status(self.ctx,{})[0]
        for s in status_list:
            if s['module_name']==self.service_name and self.v1 in s['release_tags']:
                self.assertEquals(status['up'] , 0)
            if s['module_name']==self.service_name and self.v2 in s['release_tags']:
                self.assertEquals(status['up'] , 1)

        # startup the other one too
        status = self.wiz.start(self.ctx,{'module_name':self.service,'version': self.v1})[0]
        self.assertEquals(status['up'] , 1)
        status_list = self.wiz.list_service_status(self.ctx,{})[0]
        for s in status_list:
            if s['module_name']==self.service_name and self.v1 in s['release_tags']:
                self.assertEquals(status['up'] , 1)
            if s['module_name']==self.service_name and self.v2 in s['release_tags']:
                self.assertEquals(status['up'] , 1)



    def test_log(self):
        ctx = {'token': self.token, 'user_id': 'scanon'}
        status = self.wiz.start(ctx,{'module_name': self.service, 'version': self.v1})[0]
        log = self.wiz.get_service_log(ctx, {'service': {'module_name': self.service,'version': self.v1} })[0]
	self.assertGreater(len(log), 0)
        ws = self.wiz.get_service_log_web_socket(ctx, {'service': {'module_name': self.service, 'version': self.v1} })[0]
	self.assertGreater(len(ws), 0)
        status = self.wiz.stop(self.ctx,{'module_name':self.service, 'version': self.v1})[0]

