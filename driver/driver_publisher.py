#!/usr/bin/env python3


import json, collections
import sys
import datetime
import uuid


class Publisher:

    def __init__(self, session=None):
        """
        """
        print(datetime.datetime.now(),' - driver_publisher.__init__:')
        print('\n\targs: ',locals(),'\n')
        
        self.topic = {
            'frontend' : 'com.opentrons.frontend',
            'driver' : 'com.opentrons.driver',
            'labware' : 'com.opentrons.labware',
            'bootstrapper' : 'com.opentrons.bootstrapper'
        }

        self.clients = {
            # uuid : 'com.opentrons.[uuid]'
        }
        self.max_clients = 4

        self.id = str(uuid.uuid4())

        self.caller = None

        if session is not None:
            self.caller = session


    def handshake(self, data):
        print(datetime.datetime.now(),' - driver_publisher.handshake:')
        print('\n\targs: ',locals(),'\n')

        data_dict = json.loads(data)
        if isinstance(data_dict, dict):
            if 'from' in data:
                print('* data has "from"')
                client_id = data_dict['from']
                print('client_id: ',client_id)
                if client_id in self.clients:
                    print('* from is a client')
                    if 'data' in data_dict:
                        if 'message' in data_dict['data']:
                            if 'extend' in data_dict['data']['message']:
                                print('handshake called again on client ',client_id,'. We could have done something here to repopulate data')
                                self.publish( client_id , client_id , client_id, 'handshake','driver','result','already_connected')
                            if 'shake' in data_dict['data']['message']:
                                self.publish_client_ids(client_id,client_id)
                else:
                    print('* from is NOT a client')
                    if len(self.clients) > self.max_clients:
                        self.publish( 'frontend', '' , '' , 'handshake' , 'driver' , 'result' , 'fail' )
                    else:
                        if client_id != "":
                            self.clients[client_id] = 'com.opentrons.'+client_id
                            self.publish( 'frontend' , client_id , client_id, 'handshake', 'driver', 'result','success')
                        else:
                            self.gen_client_id()
            else:
                print('* data does NOT have "from"')
                self.gen_client_id()

            if 'get_ids' in data_dict:
                publish_client_ids('','')
        else:
            self.gen_client_id()


    def gen_client_id(self):
        ret_id = ''
        if len(self.clients) > self.max_clients:
            self.publish( 'frontend', '' , '' , 'handshake' , 'driver' , 'result' , 'fail' )
        else:
            client_id = str(uuid.uuid4())
            self.clients[client_id] = 'com.opentrons.'+client_id
            self.publish( 'frontend' , client_id , client_id , 'handshake' , 'driver' , 'result' , 'success' )
            ret_id = client_id
        return ret_id


    def client_check(self, id_, session_id):
        if id_ in self.clients:
            return True
        else:
            return False


    def publish_client_ids(self, id_, session_id):
        if id_ in self.clients:
            self.publish( id_ , id_ , session_id, 'handshake' , 'driver' , 'ids' , list(self.clients) )
        else:
            self.publish( 'frontend' , '' , session_id, 'handshake' , 'driver' , 'ids' , list(self.clients) )
        return list(self.clients)


    def set_caller(self, session):
        """
        """
        print(datetime.datetime.now(),' - driver_publisher.set_caller:')
        print('\n\targs: ',locals(),'\n')
        self.caller = session


    def publish(self,topic,to,session_id,type_,name,message,param):
        """
        """
        print(datetime.datetime.now(),' - driver_publisher.publish:')
        print('\n\targs: ',locals(),'\n')
        if self.caller is not None and topic is not None and type_ is not None:
            if name is None:
                name = 'None'
            if message is None:
                message = ''
            if param is None:
                param = ''
            if self.caller is not None:
                if self.caller._myAppSession is not None:
                    msg = {'type':type_,'to':to,'from':self.id,'sessionID':session_id,'data':{'name':name,'message':{message:param}}}
                    try:
                        if topic in self.topic:
                            print('TOPIC: ',self.topic)
                            print(datetime.datetime.now(),'url topic: ',self.topic.get(topic))
                            self.caller._myAppSession.publish(self.topic.get(topic),json.dumps(msg))
                        elif topic in self.clients:
                            print('CLIENTS: ',self.clients)
                            print(datetime.datetime.now(),'url topic: ',self.clients.get(topic))
                            self.caller._myAppSession.publish(self.clients.get(topic),json.dumps(msg))


                    except:
                        print(datetime.datetime.now(),' - publisher.py - publish - error:\n\r',sys.exc_info())
            else:
                print(datetime.datetime.now(),' - publisher.py - publish - error: caller._myAppSession is None')
        else:
            print(datetime.datetime.now(),' - publisher.py - publish - error: calller, topic, or type_ is None')
