'''
Created on 30 Jul 2017

@author: jdrumgoole
'''
from datetime import datetime
import socket
import sys

from pymongo_import.canonical_path import Canonical_Path

class Restarter(object):
    '''
    Track insertion of a collection of docs by adding the last inserted
    ID into a collection called "restartlog". Each time we insert we add
    a doc with a timestamp and an ID field and a count of the number of 
    entries inserted to date. The doc also contains a batch
    start time.
    
    These class assumes the object ID is defined by default as per the MongoDB docs
    (https://docs.mongodb.com/manual/reference/method/ObjectId/). In this case in a single run 
    of the pymongoimport the IDs will contain identical host and process components. We can use 
    these fields to identify inserts that happened in the previous run. So we search for all inserts
    with an ID greater than the ID in the restartlog. 
    
    We then scan that list of inserts for a matching ID
    (remember we may be running multiple batch uploads in parallel) to find the inserts related to this 
    batch restart. Once we have that list of matching inserts then we have the count of objects inserted.
    Now we know where the restart position should be (restartlog number of entries + len( list of matching inserts)
    We can now skip() to that position in the input file and update the restart log.

    '''


    def __init__(self, database, input_filename, batch_size, cmd=None ):
        '''
        Constructor
        '''
        self._audit = database[ "audit" ]
        self._name = Canonical_Path( input_filename )
        self._batch_size = batch_size
        self._hostname =  socket.gethostname()
        if cmd is None:
            self._cmd = " ".join( sys.argv )
        else:
            self._cmd = cmd

        self._restartDoc = self._audit.find_one( { "name" : self._name(),
                                                   "state" : "inprogress" })
        
        if self._restartDoc is None :
            self.start()
        
    @staticmethod
    def split_ID( doc_id ):
        '''
        Split a MongoDB Object ID
        a 4-byte value representing the seconds since the Unix epoch,
        a 3-byte machine identifier,
        a 2-byte process id, and
        A 3-byte counter, starting with a random value.
        '''
        id_str     = str( doc_id )
        #        epoch 0        machine   1    process ID  2    counter 3
        return ( id_str[ 0:8 ],id_str[ 8:14],id_str[ 14:18], id_str[ 18:24]  )
    

    def start(self ):
        self._audit.insert_one( { "name"       : self._name(),
                                  "start"      : datetime.utcnow(),
                                  "last_doc_id"     : None,
                                  "count"      : 0,
                                  "batch_size" : self._batch_size,
                                  "command"    : self._cmd,
                                  "state"      : "inprogress"})
    
    def update(self, doc_id, count ):
        
        self._audit.find_one_and_update( { "name"      : self._name(),
                                           "state"     : "inprogress" },
                                         { "$set"      : { "count"     : count,
                                                           "end"       : datetime.utcnow(),
                                                           "last_doc_id"    : doc_id,
                                                           "state"     : "inprogress"}})
        
    def restart(self, collection ):
        '''
        Get the restart doc. Now find any docs created after the restart doc was created
        within the same process and machine. Count those so we know where we are.
        Return the new doc count that we can skip too.
        '''
        
        self._restartDoc = self._audit.find_one( { "name"  : self._name(),
                                                   "state" : "inprogress" })
        
        if self._restartDoc is None: # skip nothing, nothing to restart
            return 0
        
        count = self._restartDoc[ "count"]
        ( _, machine, pid, _ ) = Restarter.split_ID( self._restartDoc[ "last_doc_id"])
        
        cursor = collection.find( { "_id" : { "$gt" : self._restartDoc[ "last_doc_id" ]}})
        
        for i in cursor:
            ( _, i_machine, i_pid, _ ) = Restarter.split_ID( i[ "_id"])
              
            if i_machine == machine and i_pid == pid :
                count = count + 1
                
            if count == self._restartDoc[ "batch_size"]:
                # we have the full batch, we can't have inserted more than 
                # this before updating the restart doc
                break
            
        return count
            
    def finish(self ):
        
        self._restartDoc = self._audit.find_one_and_update( 
            { "name"      : self._name(),
              "state"     : "inprogress" },
            { "$set" : { "end"      : datetime.utcnow(),
                         "state"          : "completed" }} )
        
    def reset(self ):
        
        self._restartDoc = self._audit.find_one_and_update( { "name"      : self._name() },
                                                                 { "$set" : { "timestamp"      : datetime.utcnow(),
                                                                              "batch_size"     : self._batch_size,
                                                                              "count"          : 0,
                                                                              "last_doc_id"         : 0,
                                                                              "state"          : "inprogress" }} )