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
        #if hasattr(cls, 'wsName'):
        #    cls.wsClient.delete_workspace({'workspace': cls.wsName})
        #    print('Test workspace was deleted')
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
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by

	print("Test Began")
	start = time.time()
	##TESTING
	#Set up test narrative
	print("Setting up files")
	suffix = int(time.time() + 1000)
	wsName = "test_media_Calling_" + str(suffix)
	ret = self.wsClient.create_workspace({'workspace':wsName})
	#wsName = "mikaelacashman:narrative_1497647542330"
	#wsName = 'mikaelacashman:narrative_1498766137171'#CallingSDKTest
	#Set up imported modules
	fba = fba_tools(os.environ['SDK_CALLBACK_URL'])
	genomeUtil = GenomeFileUtil(os.environ['SDK_CALLBACK_URL'])
	print("Init setup and calls done: "+str(time.time()-start))
	
	#Save the genome to test narrative
	#Must be a genbank type
	start = time.time()
	filenamegenome = "KBase_derived_BTheta.gbff"
	pathgenome = os.path.join(self.cfg['scratch'],filenamegenome)
	shutil.copy(os.path.join("test_files",filenamegenome),pathgenome)
	params = {'file':{'path':pathgenome},'genome_name':"BTheta",'workspace_name':wsName}
	tempgenome = genomeUtil.genbank_to_genome(params)
	print("Genome saved: "+str(time.time()-start))

	#Save the FBA model to test narrative
	start = time.time()
	filenamemodel = "m127.GF.xls"
	pathmodel = os.path.join(self.cfg['scratch'],filenamemodel)
	shutil.copy(os.path.join("test_files",filenamemodel),pathmodel)
	params = {'model_file':{'path':pathmodel},'model_name':"BT127GF.excel.FBAModel",'workspace_name':wsName,'genome':"BTheta",'biomass':["bio1"]}
	tempmodel = fba.excel_file_to_model(params)
	print("FBA Model saved: "+str(time.time()-start))


	for x in range(120,127):
		print("Loop "+str(x))
		start = time.time()
		#Save the media to test narrative
		#filename = "Jmmol.127.tsv"
		filename = "Jmmol." + str(x) + ".tsv"
		path = os.path.join(self.cfg['scratch'],filename)
		shutil.copy(os.path.join("test_files",filename),path)
		params = {'media_file':{'path':path},'media_name':'Jmmol'+str(x)+'.media','workspace_name':wsName}
		#params = {'media_file':{'path':path},'media_name':'Jmmol127.excel.media','workspace_name':wsName}
		print("saving...")
		tempmedia=fba.tsv_file_to_media(params)	
		#tempmedia=fba.excel_file_to_media(params)
		##print(tempmedia)
		print("Media " + str(x) + " saved")
	

		##Call to FBA
		#Set up the paramaters
		print("Setting up fba params")
		fbainput = {
			'fbamodel_id': "BT127GF.excel.FBAModel",
			'media_id': "Jmmol"+str(x)+".media",
			#'media_id': "Jmmol127.excel.media",
			'fba_output_id': "testout."+str(x),
			#'fba_output_id': "testout.127",
			'workspace': wsName
		}
        	##print(pformat(fbainput))
        	print("Calling FBA")
        	#Make the call to FBA
		files = fba.run_flux_balance_analysis(fbainput)
        	print("FBA done, now finishing output")
        	#print("sleeping...")
		#time.sleep(120)
		#print("awake!!!")
		print(files)
        	#Export the output FBA as tsv and excel
		#print("----attempting to download file as tsv and excel")
        	#excel_FBA = fba.export_fba_as_excel_file({'input_ref': files['new_fba_ref']})
		#tsv_FBA = fba.export_fba_as_tsv_file({'input_ref': files['new_fba_ref']})
		#print(tsv_FBA)
		#print(excel_FBA)
		print("Loop "+str(x)+" done: ",str(time.time()-start))       	

	#Delete test workspace
	#cls.wsClient.delete_workspace({'workspace': wsName})
        #print('Test workspace was deleted')
	#DONE

        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
