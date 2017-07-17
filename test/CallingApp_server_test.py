# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests
import random
import shutil
import linecache #for searching for sampled lines in combinatoric file

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
	print("Test Began")
	start = time.time()
	FullStart = time.time()
	
	#Set up test narrative
	print("Setting up files")
	suffix = int(time.time() + 1000)
	wsName = "test_media_Calling_" + str(suffix)
	ret = self.wsClient.create_workspace({'workspace':wsName})
	#wsName = 'mikaelacashman:narrative_1498766137171'#CallingSDKTest
	
	#Set up imported modules
	fba = fba_tools(os.environ['SDK_CALLBACK_URL'])
	genomeUtil = GenomeFileUtil(os.environ['SDK_CALLBACK_URL'])
	print("Init setup and calls done: "+str(time.time()-start))
	
	#Save the genome to test narrative
	#Must be a genbank type
	start = time.time()
	#filenamegenome = "KBase_derived_BTheta.gbff"
	filenamegenome = "MA.gbff"	
	pathgenome = os.path.join(self.cfg['scratch'],filenamegenome)
	shutil.copy(os.path.join("test_files",filenamegenome),pathgenome)
	params = {'file':{'path':pathgenome},'genome_name':"MA",'workspace_name':wsName}
	tempgenome = genomeUtil.genbank_to_genome(params)
	print("Genome saved: "+str(time.time()-start))

	#Save the FBA model to test narrative
	#Currently all the same
	#To alter move into for loop
	start = time.time()
	#filenamemodel = "m125.GF.xls"
	filenamemodel = "MA.GF.xls"
	pathmodel = os.path.join(self.cfg['scratch'],filenamemodel)
	shutil.copy(os.path.join("test_files",filenamemodel),pathmodel)
	params = {'model_file':{'path':pathmodel},
		'model_name':"MAGF.FBAModel",
		'workspace_name':wsName,
		'genome':"MA",
		'biomass':["bio1"]}
	tempmodel = fba.excel_file_to_model(params)
	print("FBA Model saved: "+str(time.time()-start))

	#Save the media to test narrative
	#filename = "Jmmol.125.tsv"
	filename = "MA1.media.tsv"
	path = os.path.join(self.cfg['scratch'],filename)
	shutil.copy(os.path.join("test_files",filename),path)
	params = {'media_file':{'path':path},
		'media_name':'MA1.media',
		'workspace_name':wsName}
	tempmedia=fba.tsv_file_to_media(params)	
	print("Media saved (" + str(time.time()-start) + ")")

	#Loop over FBA
	#change range as desired
	#test currently suports a max range(120,128)
	#has timed out on me before so can just run once for a check
	##for x in range(120,128):
	
	#Set up output files
	OV_filename = self.cfg['scratch'] + "/OV.out"
	OV_file = open(OV_filename,"w+")
	status_filename = self.cfg['scratch'] + "/status.out"
	status_file = open(status_filename,"w+")
	ID_filename = self.cfg['scratch'] + "/ID.out"
	ID_file = open(ID_filename,"w+")	
	sample_filename = self.cfg['scratch'] + "/samples.out"
	sample_file = open(sample_filename,"w+")	
	allID_filename = "IDs52488.out"
	allID_path = os.path.join(self.cfg['scratch'],allID_filename)
	shutil.copy(os.path.join("test_files",allID_filename),allID_path)

	#Set up basic fbaparams
	fbaparams = {
        	'workspace':wsName,
		"fbamodel_id":  "MAGF.FBAModel",
        	"media_id":  "MA1.media",
        	"target_reaction":  "bio1",
        	"fba_output_id":  "test_file_params",
        	"fva":  1, 
        	"minimize_flux":  1,  
        	"simulate_ko":  1,  
        	"feature_ko_list":  [], 
        	"reaction_ko_list":  "", 
        	"custom_bound_list":  [], 
        	"media_supplement_list":  "", 
        	"exp_threshold_percentile":  0.5,
        	"exp_threshold_margin":  0.1,
        	"activation_coefficient":  0.5 
	}
	

	fbaMAtest = [
		["-100;cpd00009;1","-100;cpd00029;1","-100;cpd00084;10","-100;cpd00011;10"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;0"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;1"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;2"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;3"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;4"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;5"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;6"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;7"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;8"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;9"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;0","-100;cpd00011;10"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;0"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;1"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;2"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;3"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;4"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;5"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;6"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;7"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;8"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;9"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;1","-100;cpd00011;10"],
		["-100;cpd00009;1","-100;cpd00029;2","-100;cpd00084;2","-100;cpd00011;0"]
	]

	for p in fbaMAtest:
		fbaparams['custom_bound_list']=p
		print(fbaparams)
		returnVal = {}
		count = 1

		#temptemp
		files = fba.run_flux_balance_analysis(fbaparams)
		new_fba_ref = files['new_fba_ref']
		returnVal['OV'] = str(self.wsClient.get_object(
			{'workspace':wsName,
			'id':fbaparams['fba_output_id']})['data']['objectiveValue'])
		returnVal['time'] = str(time.time()-start)       	
		OV_file.write("%s\n" %returnVal['OV'])
		print("OV")
		print(returnVal['OV'])
		
	#testing the ID file
	for i in range(0,0):
		t = linecache.getline(allID_path,i)
		print (t)
		print (t.split(","))


	#Random Sample from file
	#set and print a random seed
	#generate the list to sample
	sample = random.sample(xrange(0,52488),10)
	sample_file.write(str(sample))
	sample_file.close()
	#use seek (correctly) to generate the tests to run
	print("Begining loop.  Elapsed time: " + str(time.time()-FullStart))
	#for samp in sample:
	for samp in range(1,1):
		print("loop: " + str(count) + "	   elapsed time: " + str(time.time()-FullStart))
		ID=linecache.getline(allID_path,samp+1).strip()
		params=ID.split(",")
		fbaparams['fva']	  =float(params[0])
		fbaparams['minimize_flux']=float(params[1])
		fbaparams['simulate_ko']  =float(params[2])
		fbaparams['exp_threshold_percentile']=float(params[3])
		fbaparams['exp_threshold_margin']    =float(params[4])
		fbaparams['activation_coefficient']  =float(params[5])
		fbaparams['max_c_uptake']=float(params[6])
		fbaparams['max_n_uptake']=float(params[7])
		fbaparams['max_p_uptake']=float(params[8])
		fbaparams['max_s_uptake']=float(params[9])
		fbaparams['max_o_uptake']=float(params[10])

		ID_file.write(",".join(params))
		ID_file.write("\n")
									
		##Make the call to FBA
		start = time.time()
		##Call to FBA
		files = fba.run_flux_balance_analysis(fbaparams)
		new_fba_ref = files['new_fba_ref']
		returnVal['OV'] = str(self.wsClient.get_object(
			{'workspace':wsName,
			'id':fbaparams['fba_output_id']})['data']['objectiveValue'])
		returnVal['time'] = str(time.time()-start)       	
		count+=1
		OV_file.write("%s\n" %returnVal['OV'])
		status_file.write("%s\n" %returnVal['time'])
	OV_file.close()
	status_file.close()
	ID_file.close()
	#Delete test workspace
	self.wsClient.delete_workspace({'workspace': wsName})
        print('Test workspace was deleted')
	print('Total elapsed time: ' + str(time.time()-FullStart))
	#DONE

        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
	
		  
