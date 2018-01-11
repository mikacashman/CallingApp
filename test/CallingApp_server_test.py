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
from random import randint

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint, pformat  # noqa: F401

from CallingApp.authclient import KBaseAuth as _KBaseAuth
from biokbase.workspace.client import Workspace as workspaceService
from CallingApp.CallingAppImpl import CallingApp
from CallingApp.CallingAppServer import MethodContext
from fba_tools.fba_toolsClient import fba_tools
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil

class CallingAppTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('CallingApp'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        #user_id = requests.post(
        #    'https://kbase.us/services/authorization/Sessions/Login',
        #    data='token={}&fields=user_id'.format(token)).json()['user_id']
        #user_id = auth_client.get_user(token)
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
        #config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        #cls.cfg = {}
        #config = ConfigParser()
        #config.read(config_file)
        #for nameval in config.items('CallingApp'):
        #    cls.cfg[nameval[0]] = nameval[1]
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
        TESTING = True

        if (not isMika):
            #Set up test narrative
            print("Setting up files")
            suffix = int(time.time() + 1000)
            wsName = "test_media_Calling_" + str(suffix)
            ret = self.wsClient.create_workspace({'workspace':wsName})
            
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
                print("IF THIS IS A REAL EXPERIMENT GO BACK AND CHANGE THE isMika BOOL---------")
                #Use Mika's workspace for faster testing
                #DO NOT RUN REAL EXPERIMENT IN HERE
                #Set up test narrative
                print("Setting up files")
                wsName = 'mikaelacashman:narrative_1500516864725'#EColi_test (production)	
            
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
        #set to force the file to dump every buffersize
        bufsize = 1 
        OV_file = open(OV_filename,"w+",bufsize)
        status_filename = self.cfg['scratch'] + "/status.out"
        status_file = open(status_filename,"w+",bufsize)
        ID_filename = self.cfg['scratch'] + "/ID.out"
        ID_file = open(ID_filename,"w+",bufsize) 

        #=================================================================
        #============== Change Range of Values here ======================
        #=================================================================
        
        #Read in the test file
        input_filename = "IDs_test.txt"
        input_path = os.path.join(self.cfg['scratch'],input_filename)
        print(input_path)
        test_path=os.path.join("test_files",input_filename)
        print(test_path)
        try:
            test_file = open(test_path,"r")
        except IOError:
            print("Couldn't open test file")
        shutil.copy(os.path.join("test_files",input_filename),input_path)	

        Tests=[]

        print(input_path)
        with open(input_path,'r') as IN:
            for line in IN:
                ID=line.strip()
                params=ID.split(",")
                Tests.append(params)
                
        print("Tests length")
        print(len(Tests))        
        print(len(Tests[0]))
        print(Tests[0])

        count = 0
        returnVal = {}
        IDs = []
        OVs = []
        times = []
            
        #=================================================================
        #============== Set number of runs here ==========================
        #=================================================================
        #NUM_TESTS = 1


        print("Begining loop.  Elapsed time: " + str(time.time()-FullStart))
        for params in Tests:
            #Set up basic fbaparams
            fbaparams = {
                'workspace':wsName,
                "fbamodel_id":  "EC.CDG.GF.FBAModel",
                "media_id":  "CDG.media",
                "target_reaction":  "bio1",
                "fba_output_id":  "test_file_params",
            }
           
            #Fill in the new parameters 
            fbaparams['fva']          =int(params[0])
            fbaparams['minimize_flux']=int(params[1])
            fbaparams['simulate_ko']  =int(params[2])
            fbaparams['activation_coefficient']  =float(params[3])
            fbaparams['max_c_uptake']=float(params[4])
            fbaparams['max_n_uptake']=float(params[5])
            fbaparams['max_o_uptake']=float(params[6])
            fbaparams['max_p_uptake']=float(params[7])
            fbaparams['max_s_uptake']=float(params[8])

            ##FBA
            start = time.time()
            ##Call to FBA
            files = fba.run_flux_balance_analysis(fbaparams)
            new_fba_ref = files['new_fba_ref']
            print("--Files")
            print(files)
            print("--fbaparams")
            print(fbaparams)

            #Save Ouptuts to files
            IDs =  	str(fbaparams['fva']) + "," + \
                str(fbaparams['minimize_flux']) + "," + \
                str(fbaparams['simulate_ko']) + "," + \
                str(fbaparams['activation_coefficient']) + "," + \
                str(fbaparams['max_c_uptake']) + "," + \
                str(fbaparams['max_n_uptake']) + "," + \
                str(fbaparams['max_o_uptake']) + "," + \
                str(fbaparams['max_p_uptake']) + "," + \
                str(fbaparams['max_s_uptake'])
            print("--IDs")
            print(IDs)

            OVs=(str(self.wsClient.get_object(
                {'workspace':wsName,
                'id':fbaparams['fba_output_id']})['data']['objectiveValue']))
            times=(str(time.time()-start))
            ID_file.write("%s\n" %",".join(params))
            OV_file.write("%s\n" %OVs)
            status_file.write("%s\n" %times)
            count+=1
            print("--params")
            print(params)
            print("--Ovs")
            print(OVs)
            print("================================")
            print("================================")

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
        if (not isMika):
            #Delete test workspace
            self.wsClient.delete_workspace({'workspace': wsName})
            print('Test workspace was deleted')
        print('Total elapsed time: ' + str(time.time()-FullStart))
        #DONE

        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
	
		  
