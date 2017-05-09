/*
A KBase module: CallingApp
*/

module CallingApp {
    /*
        Insert your typespec information here.
    */
    
    typedef structure {
	string workspace;
        string fbamodel_id;
        string media;
        string fbaOutput_id;
    }CallingParams;

    typedef structure {
	string temp;
    }CallingResults;

    funcdef CallingFBA(CallingParams params) returns (CallingResults) authentication required;
};
