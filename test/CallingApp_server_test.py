# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint, pformat  # noqa: F401


from biokbase.workspace.client import Workspace as workspaceService
from CallingApp.CallingAppImpl import CallingApp
from CallingApp.CallingAppServer import MethodContext
from fba_tools.fba_toolsClient import fba_tools
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil

class CallingAppTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
	token = environ.get('KB_AUTH_TOKEN', None)
        user_id = requests.post(
            'https://kbase.us/services/authorization/Sessions/Login',
            data='token={}&fields=user_id'.format(token)).json()['user_id']
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'CallingApp',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('CallingApp'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = CallingApp(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
	
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')
	return

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_CallingApp_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_fbaCall(self):
	#fba = fba_tools(self.callback_url)
	#filename = "Jmmol.120.tsv"
	#path = os.path.join(cls.cfg['scratch'],filename)
	#shutil.copy(os.path.join("media",filename),path)
	#fba = fba_tools(os.environ['SDK_CALLBACK_URL'])
	#for files in os.listdir("/kb/module/work/media"):
	#	print(files)
		#tempfile = "/kb/module/work/media/" + files
		#print(tempfile)
		#params = {'media_file':{'path':tempfile},'media_name':'Jmmol120.media','workspace_name':self.getWsName()}
		#tempmedia=fba.tsv_file_to_media(params)
	#params = {'media_file':{'path':path},'media_name':'Jmmol120.media'}
	#os.path.join(
	#params = {'media_file':{'path':"/kb/module/work/media/Jmmol.120.tsv"},'media_name':'Jmmol120.media','workspace_name':self.getWsName()}
	#tempmedia=fba.tsv_file_to_media(params)
        #ret = self.getImpl().CallingFBA(self.getContext(), {'workspace':'mikaelacashman:1487002527453','fbamodel_id':'BTheta.FBA','media':tempmedia,'fbaOutput_id':'test.out'})
	
	##TESTING
	#Set up test narrative
	print("Setting up files")
	#suffix = int(time.time() + 1000)
	#wsName = "test_Calling_" + str(suffix)
	wsName = "mikaelacashman:narrative_1498775075894" #CallingAppOV
	#ret = cls.wsClient.create_workspace({'workspace':wsName})
	#Set up imported modules
	fba = fba_tools(os.environ['SDK_CALLBACK_URL'])

	#Save the FBA model to test narrative
	start = time.time()
	filenamemodel = "m127.GF.xls"
	##filenamemodel = "m127.GF.sbml"
	###filenamemodelR = "m127.GF.r.tsv"
	###filenamemodelC = "m127.GF.c.tsv"
	pathmodel = os.path.join(self.cfg['scratch'],filenamemodel)
	shutil.copy(os.path.join("test_files",filenamemodel),pathmodel)
	###pathmodelR = os.path.join(self.cfg['scratch'],filenamemodelR)
	###shutil.copy(os.path.join("test_files",filenamemodelR),pathmodelR)
	###pathmodelC = os.path.join(self.cfg['scratch'],filenamemodelC)
	###shutil.copy(os.path.join("test_files",filenamemodelC),pathmodelC)
	params = {'model_file':{'path':pathmodel},'model_name':"BT127GF.excel.FBAModel",'workspace_name':wsName,'genome':"BTheta",'biomass':["bio1"]}
	tempmodel = fba.excel_file_to_model(params)
	##params = {'model_file':{'path':pathmodel},'model_name':"BT127GF.sbml.FBAModel",'workspace_name':wsName,'genome':"BTheta",'biomass':["bio1"]}
	##tempmodel = fba.sbml_file_to_model(params)
	###params = {'model_file':{'path':pathmodelR},'model_name':"BT127GF.tsv.FBAModel",'workspace_name':wsName,'genome':"BTheta",'biomass':["bio1"],	'compounds_file':{'path':pathmodelC}}
	###tempmodel = fba.tsv_file_to_model(params)
	print("FBA Model saved: "+str(time.time()-start))
	
	
	##Call to FBA
	#Set up the paramaters
	print("Setting up fba params")
	fbainput = {
		'fbamodel_id': "BT127GF.FBAModel",
		'media_id': "Jmmol125.media",
		'fba_output_id': "testout",
		'workspace': wsName
	}
        print(pformat(fbainput))
        print("Calling FBA")
        #Make the call to FBA
	files = fba.run_flux_balance_analysis(fbainput)
        print("FBA done, now finishing output")
        print(files)
	new_fba_ref = files['new_fba_ref']
	print("Objective Value is: " + str(self.wsClient.get_object({'workspace':wsName,'id':fbainput['fba_output_id']})['data']['objectiveValue']))
	
	#OLD CODE
	#print(files['objective'])#this should work but it doesn't, maybe because the model didn't grow?
	#print(self.wsClient.list_objects({'workspaces':wsName}))
	#new_fba = self.wsClient.get_object({'id':'testout','wsName':wsName})
	#print(new_fba['objectiveValue'])
        #Export the output FBA as tsv and excel
	print("----attempting to download file as tsv and excel")
        excel_FBA = fba.export_fba_as_excel_file({'input_ref': files['new_fba_ref']})
	#tsv_FBA = fba.export_fba_as_tsv_file({'input_ref': files['new_fba_ref']})
	#print(tsv_FBA)
	print(excel_FBA)
       	
	#Delete test workspace
	#cls.wsClient.delete_workspace({'workspace': wsName})
        #print('Test workspace was deleted')
	#DONE
	 
