# -*- coding: utf-8 -*-
#BEGIN_HEADER
from fba_tools.fba_toolsClient import fba_tools
import os
import sys
import traceback
import uuid
from biokbase.workspace.client import Workspace as workspaceService
from pprint import pprint, pformat
#END_HEADER


class CallingApp:
    '''
    Module Name:
    CallingApp

    Module Description:
    A KBase module: CallingApp
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/mikacashman/CallingApp.git"
    GIT_COMMIT_HASH = "27b072467fc50bd885617ca32326af474a96c9ef"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
	self.callback_url = os.environ['SDK_CALLBACK_URL']
	self.workspaceURL = config['workspace-url']
	self.scratch = config['scratch']
        #END_CONSTRUCTOR
        pass


    def CallingFBA(self, ctx, params):
        """
        :param params: instance of type "CallingParams" (Insert your typespec
           information here.) -> structure: parameter "workspace" of String,
           parameter "fbamodel_id" of String, parameter "media" of String,
           parameter "fbaOutput_id" of String
        :returns: instance of type "CallingResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN CallingFBA
	
	fba = fba_tools(self.callback_url);
		
	 ### STEP 1 - Parse input and catch any errors
	if 'workspace' not in params:
		raise ValueError('Parameter workspace is not set in input arguments')
	workspace_name=params['workspace']
 	if 'fbamodel_id' not in params:
		raise ValueError('Parameter FBAModel is not set in input arguments')
	if 'media' not in params:
		raise ValueError('Parameter Media is not set in input arguments')
	if 'fbaOutput_id' not in params:
		raise ValueError('Parameter FBA output ID is not set in input arguments')

	### STEP 2 - Get the Input Data
	print("Params are good, now getting the input data")
	token = ctx['token']
	wsClient = workspaceService(self.workspaceURL, token=token)
	#try:
	#	fbamodel = wsClient.get_objects([{'ref':params['fbamodel_id']}])[0]['data']
	#except:
	#	exc_type, exc_value, exc_traceback = sys.exc_info()
	#	lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
	#	orig_error = ''.join('   ' + line for line in lines)
	#	raise ValueError('Error loading FBAModel object from workspace:\n' + orig_error)
	#print('Got FBAModel')
	#try:
	#	media = wsClient.get_objects([{'ref':params['media']}])[0]['data']
	#except:
	#	exc_type, exc_value, exc_traceback = sys.exc_info()
 	#	lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
	#	orig_error = ''.join('   ' + line for line in lines)
 	#	raise ValueError('Error loading Media object from workspace:\n' + orig_error)
 	#print('Got Media')
	#print(pformat(fbamodel))
	#print(pformat(media))
	#print(params['fbaOutput_id'])
	
	print("Setting up fba params")
	fbamodel_input = params.get('fbamodel_id')
	media_input = params.get('media')
	fbaOutput_input = params.get('fbaOutput_id')

	fbainput = {
		'fbamodel_id': params['fbamodel_id'],
		'media_id': media_input,
		'fba_output_id': fbaOutput_input,
		#'target_reaction': "bio1",
		'workspace': workspace_name
		}
	#fbainput = {
	#	'fbamodel_id': params['fbamodel_id'],
	#	'media_id': params['media'],
	#	'fba_output_id': params['fbaOutput_id'],
	#	'target_reaction': "bio1",
	#	'workspace': params['workspace']
	#	}
	# Code Cell params way of calling FBA 
	#fbainput = {
	#	'model': params['fbamodel_id'],
	#	'formulation': { 'media': params['media'], 'media_workspace' : params['workspace']},
	#	'workspace': params['workspace'],
	#	'fba': params['fbaOutput_id']
	#	}
	print(type(fbainput))
	#print(pformat(fbainput))
	print("Calling FBA")
	files = fba.run_flux_balance_analysis(fbainput)
	print("FBA done, now finishing output")
	reportObj = { 
                'objects_created':[],
                'text_message':"Meow"
        }   
        #save report
        provenance = [{}]
        if 'provenance' in ctx:
                provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects']=[workspace_name+'/'+params['fbamodel_id']]
        report_info_list = None
        try:
                report_info_list = wsClient.save_objects({
                        'workspace':workspace_name,
                        'objects':[
                        {   
                                'type':'KBaseReport.Report',
                                'data':reportObj,
                                'name':'CallingFBA_report' + str(hex(uuid.getnode())),
                                'meta':{},
                                'hidden':1, # important!  make sure the report is hidden
                                'provenance':provenance
                        }   
                        ]   
                })  
        except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                orig_error = ''.join('    ' + line for line in lines)
                raise ValueError('Error saving Report object to workspace:\n' + orig_error)
        report_info = report_info_list[0]
        print('Ready to return')
        returnVal = { 
                'report_name':'FS_report',
                'report_ref': str(report_info[6]) + '/' + str(report_info[0]) + '/' + str(report_info[4])
        }   

        #END CallingFBA
        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method CallingFBA return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
