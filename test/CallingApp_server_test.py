# -*- coding: utf-8 -*-
# This version will take a random sample of configurations
# from a file in test/test_files (set to IDs52488.out right
# now) and runs FBA through them.
#
# OUTPUT: samples chosen, OVs, time for each loop, IDs

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

	#To run tests faster (for Mika) use bool
	#Real tests should have bool=FALSE
	isMika = True 

	if (not isMika):
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
		filenamegenome = "EC_NCBI.gbff"
		pathgenome = os.path.join(self.cfg['scratch'],filenamegenome)
		shutil.copy(os.path.join("test_files",filenamegenome),pathgenome)
		params = {'file':{'path':pathgenome},'genome_name':"Ecoli",'workspace_name':wsName}
		tempgenome = genomeUtil.genbank_to_genome(params)
		print("Genome saved: "+str(time.time()-start))

		#Save the FBA model to test narrative
		#Currently all the same
		#To alter move into for loop
		start = time.time()
		filenamemodel = "EC.GF.xls"
		pathmodel = os.path.join(self.cfg['scratch'],filenamemodel)
		shutil.copy(os.path.join("test_files",filenamemodel),pathmodel)
		params = {'model_file':{'path':pathmodel},
			'model_name':"EC.CDG.GF.FBAModel",
			'workspace_name':wsName,
			'genome':"Ecoli",
			'biomass':["bio1"]}
		tempmodel = fba.excel_file_to_model(params)
		print("FBA Model saved: "+str(time.time()-start))

		#Save the media to test narrative
		filename = "CDG.media.tsv"
		path = os.path.join(self.cfg['scratch'],filename)
		shutil.copy(os.path.join("test_files",filename),path)
		params = {'media_file':{'path':path},
			'media_name':'CDG.media',
			'workspace_name':wsName}
		tempmedia=fba.tsv_file_to_media(params)	
		print("Media saved (" + str(time.time()-start) + ")")

	else:
		#Set up test narrative
		print("Setting up files")
		#suffix = int(time.time() + 1000)
		#wsName = "test_media_Calling_" + str(suffix)
		#ret = self.wsClient.create_workspace({'workspace':wsName})
		wsName = 'mikaelacashman:narrative_1498142336734'#ExploreFBAParams (production)
		
		#Set up imported modules
		fba = fba_tools(os.environ['SDK_CALLBACK_URL'])
		genomeUtil = GenomeFileUtil(os.environ['SDK_CALLBACK_URL'])
		print("Init setup and calls done: "+str(time.time()-start))
		
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

	#=================================================================
	#============== Change Test File Here ============================
	#=================================================================
	allID_filename = "IDs_overnight_test1.out"
	allID_path = os.path.join(self.cfg['scratch'],allID_filename)
	shutil.copy(os.path.join("test_files",allID_filename),allID_path)

	#Set up basic fbaparams
	fbaparams = {
        	'workspace':wsName,
		"fbamodel_id":  "EC.CDG.GF.FBAModel",
        	"media_id":  "CDG.media",
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
	#fbaparams['custom_bound_list']=["-100;cpd00009;1","-100;cpd00029;1","-100;cpd00084;10","-100;cpd00011;10"]

	#Random Sample from file
	#set and print a random seed
	#generate the list to sample
	#sample = random.sample(xrange(0,2),NUM_TESTS)
	#sample_file.write(str(sample))
	#sample_file.close()
	
	#Run random tests from exisiting file
	rand_filename = "IDs_172mil_V1.out"
	rand_filepath = os.path.join(self.cfg['scratch'],rand_filename)
	shutil.copy(os.path.join("test_files",rand_filename),rand_filepath)
	#rand_filenamecopied = self.cfg['scratch'] + "./IDs_172milTest.out"
	rand_file = open(rand_filepath,"r")
	#rand_file = open(rand_filenamecopied,"r")
	#read in lines to a data structure
	tests = rand_file.readlines()
	print("Number of tests to run: " + str(len(tests)))	

	count = 0
	returnVal = {}
	IDs = []
	OVs = []
	times = []

		
	NUM_TESTS = 20
	print("Begining loop.  Elapsed time: " + str(time.time()-FullStart))
	#for samp in sample:
	for t in range(0,NUM_TESTS):
		print("loop: " + str(count) + "	   elapsed time: " + str(time.time()-FullStart))
		#ID=linecache.getline(allID_path,samp+1).strip()
		#params=ID.split(",")
		params = tests[t].strip().split(",")
		IDs.append(tests[t])	
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
		fbaparams['thermodynamic_constraints']=float(params[11])
		fbaparams['find_min_media']=float(params[12])
		fbaparams['all_reversible']=float(params[13])	

		#ID_file.write(",".join(params))
		#ID_file.write("\n")
									
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
		#OV_file.write("%s\n" %returnVal['OV'])
		#status_file.write("%s\n" %returnVal['time'])
		OVs.append(returnVal['OV'])
		times.append(returnVal['time'])		

		#print IDs every 10 runs
		if count%10 == 0 and count>1:
			for j in range(0,9):
				ID_file.write(IDs[j])
				OV_file.write("%s\n" %OVs[j])
				status_file.write("%s\n" %times[j])
			IDs = []
			OVs = []
			times = []
				

		#Downloading (takes 3-6 mintues per file)
		#print("FBA done, now finishing output (" + str(time.time()-start) + ")")
        	#Export the output FBA as tsv and excel
		#print("----download FBA as tsv")
		#tsv_FBA = fba.export_fba_as_tsv_file({'input_ref': files['new_fba_ref']})
		#print(tsv_FBA)
		#print("File downloaded (" + str(time.time()-start) + ")") 
	
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
	
		  
