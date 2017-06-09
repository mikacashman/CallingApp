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
	##TESTING
	print("Setting up files")
	suffix = int(time.time() + 1000)
	wsName = "test_Calling_" + str(suffix)
	ret = cls.wsClient.create_workspace({'workspace':wsName})
	fba = fba_tools(os.environ['SDK_CALLBACK_URL'])
	genomeUtil = GenomeFileUtil(os.environ['SDK_CALLBACK_URL'])
	
	filenamegenome = "KBase_derived_BTheta.gbff"
	pathgenome = os.path.join(cls.cfg['scratch'],filenamegenome)
	shutil.copy(os.path.join("test_files",filenamegenome),pathgenome)
	params = {'file':{'path':pathgenome},'genome_name':"BTheta",'workspace_name':wsName}
	tempgenome = genomeUtil.genbank_to_genome(params)
	print("Genome saved")

	filename = "Jmmol.120.tsv"
	path = os.path.join(cls.cfg['scratch'],filename)
	shutil.copy(os.path.join("test_files",filename),path)
	params = {'media_file':{'path':path},'media_name':'Jmmol120.media','workspace_name':wsName}
	tempmedia=fba.tsv_file_to_media(params)	
	print("Media saved")
	
	filenamemodel = "kb|g.436.fbamdl61.xls"
	pathmodel = os.path.join(cls.cfg['scratch'],filenamemodel)
	shutil.copy(os.path.join("test_files",filenamemodel),pathmodel)
	params = {'model_file':{'path':pathmodel},'model_name':"BT127GF.FBAModel",'workspace_name':wsName,'genome':"BTheta",'biomass':["bio1"]}
	tempmodel = fba.excel_file_to_model(params)
	print("FBA Model saved")

	#Actual Call
	print("Setting up fba params")
        #fbamodel_input = params.get('fbamodel_id')
        #media_input = params.get('media')
        #fbaOutput_input = params.get('fbaOutput_id')

        fbainput = { 
                'fbamodel_id': tempmodel['ref'],
                'media_id': tempmedia['ref'],
                'fba_output_id': "testOutinTest",
                #'target_reaction': "bio1",
                'workspace': wsName
        }   
        print(type(fbainput))
        print(pformat(fbainput))
        print("Calling FBA")
        files = fba.run_flux_balance_analysis(fbainput)
        print("FBA done, now finishing output")
        print(files)
        print("----attempting to download file as sbml")
        #smbl_file = fba.model_to_sbml_file({'workspace_name': params['workspace'],'model_name': fbainput['fba_output_id']})
        sbml_file = fba.export_fba_as_tsv_file({'input_ref': files['new_fba_ref']})
	print(sbml_file)



	#print("Ready to call")
	#print(params)
	#ret = cls.getImpl().CallingFBA(self.getContext(), {'workspace':wsName,'fbamodel_id':'BT127GF.FBAModel','media':tempmedia,'fbaOutput_id':'test.out'})
        
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

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
	pass
	#print os.environ['HOME']
	#fba = fba_tools(self.callback_url)
	#Ranjan
	#filename = "Jmmol.120.tsv"
	#path = os.path.join(cls.cfg['scratch'],filename)
	#shutil.copy(os.path.join("media",filename),path)

	#print(self.callback_url)
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
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
