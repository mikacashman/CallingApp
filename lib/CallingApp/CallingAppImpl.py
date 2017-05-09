# -*- coding: utf-8 -*-
#BEGIN_HEADER
from fba_tools.fba_toolsClient import fba_tools
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
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
	self.callback_url = os.enviorn['SDK_CALLBACK_URL']
        #END_CONSTRUCTOR
        pass


    def CallingFBA(self, ctx, params):
        """
        :param params: instance of type "CallingParams" (Insert your typespec
           information here.) -> structure: parameter "workspace" of String
        :returns: instance of type "CallingResults" -> structure: parameter
           "temp" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN CallingFBA
	fba = fba_tools(self.callback_url);
	
	 ### STEP 1 - Parse input and catch any errors
	if 'workspace_name' not in params:
		raise ValueError('Parameter workspace is not set in input arguments')
	workspace_name=params['workspace_name']
 	if 'fbamodel_id' not in params:
		raise ValueError('Parameter FBAModel is not set in input arguments')
	if 'media' not in params:
		raise ValueError('Parameter Media is not set in input arguments')
	if 'fbaOutput_id' not in params:
		raise ValueError('Parameter FBA output ID is not set in input arguments')

	### STEP 2 - Get the Input Data
	token = ctx['token']
	wsClient = workspaceServices(self.workspaceURL, token=token)
	try:
		fbamodel = wsClient.get_objects([{'ref':params['fbamodel_id']}])[0]['data']
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		orig_error = ''.join('   ' + line for line in lines)
		raise ValueError('Error loading FBAModel object from workspace:\n' + orig_error)
	print('Got FBAModel')
	try:
		media = wsClient.get_objects([{'ref':params['media']}])[0]['data']
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
 		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		orig_error = ''.join('   ' + line for line in lines)
 		raise ValueError('Error loading Media object from workspace:\n' + orig_error)
 	print('Got Media')

	fbainput = [{'fbamodel_id':params['fbamodel_id'],'media_id':parmas['media'],'fba_output_id':params['fbaOutput_id']}]
	#need input files here
	files = fba.run_flux_balance_analysis(fbainput)

        #END CallingFBA

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method CallingFBA return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [files]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
