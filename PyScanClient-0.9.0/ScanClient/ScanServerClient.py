'''
Copyright (c) 2014 
All rights reserved. Use is subject to license terms and conditions.
Created on 30 12, 2014
@author: Yongxiang Qiu
'''

from datetime import datetime

from collections import OrderedDict

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

import requests, numpy

class ScanServerClient(object):
    '''
    The ScanServerClient provides interfaces to interact with java-ScanServer,
    which includes methods such as Start,Pause,GetScanInfo... to manipulate 
    the behaviors and retrieve data from Scan.
    '''
    __baseURL = None
    __serverResource = "/server"
    __serverInfoResource = "/info"
    __simulateResource = "/simulate"
    __scansResource = "/scans"
    __scansCompletedResource = "/completed"
    __scanResource = "/scan"
     
    def __new__(cls, host = 'localhost',port=4810):
        '''   
        Singleton method to make sure there is only one instance alive.
        '''
        
        if not hasattr(cls, 'instance'):
            cls.instance = super(ScanServerClient,cls).__new__(cls)
        return cls.instance
    
    def __init__(self, host = 'localhost',port=4810):
        
        self.__baseURL = "http://"+host+':'+str(port)
        
        try:  
            requests.get(self.__baseURL+'/scans', verify=False).raise_for_status()
        except:
            raise Exception, 'Failed to create client to ' + self.__baseURL
        
        
        
    def submitScan(self,scanXML=None,scanName='UnNamed'):
        '''
        Create and submit a new scan.
        
        Using   POST {BaseURL}/scan/{scanName}
        Return  <id>{scanId}</id>
        
        :param scanXML: The XML content of your new scan
        :param scanName: The name you want to give the new scan
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> scanId = ssc.submitScan(scanXML='<commands><comment><address>0</address><text>Successfully adding a new scan!</text></comment></commands>',scanName='1stScan')
        '''
        
        if scanXML == None:
            scanXML = raw_input('Please enter your scanXML:') 
        try:
            url = self.__baseURL+self.__scanResource+'/'+scanName
            r = requests.post(url = url,data = scanXML,headers = {'content-type': 'text/xml'}) 
        except:
            raise Exception, 'Failed to submit scan.'
        
        if r.status_code == 200:
            return r.text
        else:
            return None

    def simulateScan(self,scanXML=None):
        '''
        Simulate a scan.
        
        Using   POST {BaseURL}/simulate
        Return  Success Messages in XML form
        
        :param scanXML: The XML content of your new scan
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> sid = ssc.simulateScan(scanXML='<commands><comment><address>0</address><text>Successfully simulating a new scan!</text></comment></commands>')
      
        '''
        if scanXML == None:
            scanXML = raw_input('Please enter your scanXML:') 
        r = requests.post(url = self.__baseURL+self.__simulateResource,data = scanXML,headers = {'content-type': 'text/xml'}) 
        if r.status_code == 200:
            return r.text
        else:
            return None
        
    def deleteScan(self,scanID = None):
        '''
        Remove a unique scans.
        
        Using DELETE {BaseURL}/scan/{scanID}.
        Return HTTP status code.
        
        :param scanID: The id of scan you want to delete.Must be an integer.
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> st = ssc.deleteScan(153)
      
        Return the status code. 0 if Error parameters.
        '''
        if scanID == None:
            scanID = raw_input('Please enter your scan ID:')
        elif not isinstance(scanID, int):
            scanID = input('Scan ID must be an integer.Please reenter:')
        
        try:
            r=requests.delete(url = self.__baseURL+self.__scanResource+'/'+str(scanID))
            print 'Scan %d deleted.'%scanID
        except:
            raise Exception, 'Failed to deleted scan '+str(scanID)
        return r.status_code

    def removeCompeletedScan(self):
        '''
        Remove completed scan.
        
        Using DELETE {BaseURL}/scans/completed.
        Return HTTP status code.
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> st = ssc.removeCompeletedScan()
        '''
        
        try:
            r = requests.delete(url = self.__baseURL+self.__scansResource+self.__scansCompletedResource)
            print 'All completed scans are deleted.'
        except:
            raise Exception, 'Failed to remove completed scan.'
        return r.status_code
    

    def get_scan(self, scanID):
        '''
        Get information for the scan with the given ID.

        :param scanID: scan ID
        :return: ScanInfo object
        '''
        try:
            # Not sure what content type this is requesting, should be XML.
            r = requests.get(self.__baseURL+self.__scanResource+'/'+str(scanID))
        except:
            raise Exception, 'Failed to get info from scan '+str(scanID)
        return ScanInfo(r.text)


    def get_data(self, scanID):
        '''
        Get data for the scan with the given ID.

        :param scanID: scan ID
        :return: ScanData object
        '''
        try:
            # Not sure what content type this is requesting, should be XML.
            r = requests.get(self.__baseURL+self.__scanResource+'/'+str(scanID)+'/data')
        except:
            raise Exception, 'Failed to get data from scan '+str(scanID)
        return ScanData(r.text)


    #############Detailed Design Needed#############
    def getScanInfo(self,scanID = None,infoType = None):
        '''
        Get all information of one scan.
        Using  GET {BaseURL}/scan/{scanID}                - get scan info
               GET {BaseURL}/scan/{scanID}/commands       - get scan commands
               GET {BaseURL}/scan/{scanID}/data           - get scan data
               GET {BaseURL}/scan/{scanID}/last_serial    - get scan data's last serial
               GET {BaseURL}/scan/{scanId}/devices        - get devices used by a scan
        Return all scan info in XML form.
        
        :param scanID: The id of scan you want to get.Must be an integer.
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> st = ssc.getScanInfo(153,scan)
        '''
        
        if scanID == None:
            scanID = raw_input('Please enter your scan ID:')
        elif not isinstance(scanID, int):
            scanID = input('Scan ID must be an integer.Please reenter:')
            
        if infoType == None:
            infoType = raw_input('Select the type of the info you want below-(scan, data, commands, last_serial, devices):')
        
        try:
            if infoType == 'scan':
                url = self.__baseURL+self.__scanResource+'/'+str(scanID)
            else:
                url = self.__baseURL+self.__scanResource+'/'+str(scanID)+'/'+infoType
            r = requests.get(url)
        except:
            raise Exception, 'Failed to get info from scan '+str(scanID)
        return r.text
                
    def getScanServerInfo(self):
        '''
        Get information of current server
        Using GET {BaseURL}/server/info
        Return:<Server></Server>
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> st = ssc.getScanServerInfo()
        '''
        
        try:
            r = requests.get(url = self.__baseURL+self.__serverResource+self.__serverInfoResource)
        except:
            raise Exception, 'Failed to get info from scan server.'
        return r.text
        
    def getAllScanInfo(self):
        '''
        Get information of all scans 
        Using GET {BaseURL}/scans - get all scan infos
        Return all info of all scans in XML form.
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> st = ssc.getAllScanInfo()
        '''
        try:
            r = requests.get(url = self.__baseURL+self.__scansResource)
        except:
            raise Exception, 'Failed to get info from scan server.'
        return r.text

    def pause(self,scanID=None):
        ''' 
        Pause a running scan
        
        Using PUT {BaseURL}/scan/{id}/pause
        Return Http Status Code
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> st = ssc.pause(153)
        '''

        if scanID == None:
            scanID = input('Enter id of the scan you want to pause:')
        elif not isinstance(scanID, int):
            scanID = input('Scan ID must be an integer.Please reenter:')
        
        try:
            r = requests.put(url=self.__baseURL+self.__scanResource+'/'+str(scanID)+'/pause')
        except:
            raise Exception, 'Failed to get info from scan server.'
        return r.status_code
        
    def abort(self,scanID=None):
        '''
        Abort running or paused scan
        
        Using PUT {BaseURL}/scan/{id}/abort
        Return Http Status Code
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> st = ssc.abort(153)
        '''
        
        if scanID == None:
            scanID = input('Enter id of the scan you want to abort:')
        elif not isinstance(scanID, int):
            scanID = input('Scan ID must be an integer.Please reenter:')
    
        try:
            r = requests.put(url=self.__baseURL+self.__scanResource+'/'+str(scanID)+'/abort')
        except:
            raise Exception, 'Failed to abort scan '+str(scanID)
        return r.status_code
    
    def resume(self,scanID=None):
        '''
        Resume paused scan
        Using PUT {BaseURL}/scan/{scanID}/resume
        
        Return Http Status Code
        
        Usage::

        >>> import ScanServerClient
        >>> ssc=ScanServerClient('localhost',4810)
        >>> st = ssc.abort(153)
        '''
        
        if scanID == None:
            scanID = input('Enter id of the scan you want to resume:')
        elif not isinstance(scanID, int):
            scanID = input('Scan ID must be an integer.Please reenter:')
        
        try:
            r = requests.put(url=self.__baseURL+self.__scanResource+'/'+str(scanID)+'/resume')
        except:
            raise Exception, 'Failed to resume scan ',scanID
        return r.status_code        
        
    def updateCommand(self,scanID=None,scanXML=None):
        '''
        Update property of a scan command.
        
        Using PUT {BaseURL}/scan/{scanID}/patch
        Return Http Status Code.
        
        Requires description of what to update:
          
            <patch>
                <address>10</address>
                <property>name_of_property</property>
                <value>new_value</value>
            </patch>
          
        '''
        if scanXML == None:
            scanXML = raw_input('Please enter your scanXML:') 
        
        if scanID == None:
            scanID = input('Enter id of the scan you want to update:')
        elif not isinstance(scanID, int):
            scanID = input('Scan ID must be an integer.Please reenter:')
        
        try:
            r = requests.put(url=self.__baseURL+self.__scanResource+'/'+str(scanID)+'/patch',data=scanXML,headers= {'content-type': 'text/xml'})
        except:
            raise Exception, 'Failed to resume scan '+str(scanID)
        return r.status_code
    
'''
ssc=ScanServerClient(host='localhost',port=4810)
for i in range(278,283):
    ssc.abort(i)
else:
    print 'All scans aborted.'
    '''

class ScanInfo(object):
    '''
    The ScanInfo class contains scan details as returned by the Scan Server
    and is constructed from the the raw XML response similar to the following:

    <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <scan>
        <id>15</id>
        <name>example1</name>
        <created>1424465207911</created>
        <state>Idle</state>
        <runtime>0</runtime>
        <total_work_units>22</total_work_units>
        <performed_work_units>0</performed_work_units>
        <address>-1</address>
        <command/>
    </scan>


    :param xml: string containing scan information in XML format
    '''
    
    _ROOT_TAG = "scan"
    _ID_TAG = "id"
    _NAME_TAG = "name"
    _STATE_TAG = "state"
    _CREATED_TAG = "created"
    _ADDRESS_TAG = "address"
    _RUNTIME_TAG = "runtime"
    _COMMAND_TAG = "command"
    _TOTAL_WORK_TAG = "total_work_units"
    _COMPLETED_WORK_TAG = "performed_work_units"

    def __init__(self, xml):
        root = ElementTree.fromstring(xml)
        if root.tag != self._ROOT_TAG:
            raise ValueError("ScanInfo: Expecting root tag '{}' not '{}'".format(self._ROOT_TAG, root.tag))
        self.id = int(root.findtext(self._ID_TAG))
        self.name = root.findtext(self._NAME_TAG)
        self.created = datetime.fromtimestamp(float(root.findtext(self._CREATED_TAG))/1000) # milliseconds to seconds
        self.state = root.findtext(self._STATE_TAG)
        self.runtime = root.findtext(self._RUNTIME_TAG)
        self.total_work = int(root.findtext(self._TOTAL_WORK_TAG))
        self.completed_work = int(root.findtext(self._COMPLETED_WORK_TAG))
        self.address = int(root.findtext(self._ADDRESS_TAG))
        self.command = root.findtext(self._COMMAND_TAG)
    
    def is_idle(self):
        return (self.state == "Idle")
    
    def is_running(self):
        return (self.state == "Running")
    
    def is_finished(self):
        return (self.state == "Finished")
        
    def is_aborted(self):
        return (self.state == "Aborted")
    
    def progress(self):
        return ((100.0 * self.completed_work) / self.total_work)
    
    def __str__(self):
        return "ScanInfo{{ id={info.id}, name='{info.name}', state={info.state} created='{info.created}' }}".format(info=self)



class ScanData(object):
    '''
    The ScanData class contains the data from a running or finished scan and
    is constructed from the raw XML response similar to the following:
    <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <data>
        <device>
            <name>D_M:LS1_CA01:BPM_D1144:POSH_RD</name>
            <samples>
                <sample id="0">
                    <time>1424466313887</time>
                    <value>-0.0147678</value>
                </sample>
                <sample id="1">
                    <time>1424466313889</time>
                    <value>-0.0148757</value>
                </sample>
                <!-- more samples -->
            </samples>
        </device>
        <!-- more devices --> 
    </data>

    The ScanData class has the following properties:

    times - dictionary of timestamp values as an NDArray and keyed by device name
    values - dictionary of scan data values as an NDArray and keyed by device name
    devices - list of device names

    :param xml: string containing scan data in XML format
    '''

    _ROOT_TAG = "data"
    _NAME_TAG = "name"
    _TIME_TAG = "time"
    _VALUE_TAG = "value"
    _DEVICE_TAG = "device"
    _SAMPLE_TAG = "sample"
    _SAMPLES_TAG = "samples"
    _SAMPLE_ID_ATT = "id"

    def __init__(self, xml):
        root = ElementTree.fromstring(xml)
        if root.tag != self._ROOT_TAG:
            raise ValueError("ScanData: Expecting root tag '{}' not '{}'".format(self._ROOT_TAG, root.tag))
        self.times = OrderedDict()
        self.values = OrderedDict()
        for device in root.iter(self._DEVICE_TAG):
            data = []
            name = device.findtext(self._NAME_TAG)
            for sample in device.find(self._SAMPLES_TAG).iter(self._SAMPLE_TAG):
                sid = int(sample.get(self._SAMPLE_ID_ATT))
                # Consider converting timestamp to datetime object.
                data.append((sid, float(sample.findtext(self._TIME_TAG)),
                                    float(sample.findtext(self._VALUE_TAG))))
            data.sort(key=lambda x: x[0])
            times = numpy.empty(len(data))
            values = numpy.empty(len(data))
            for idx in xrange(len(data)):
                times[idx] = data[idx][1]
                values[idx] = data[idx][2]
            self.times[name] = times
            self.values[name] = values
        self.devices = list(self.values.keys())
