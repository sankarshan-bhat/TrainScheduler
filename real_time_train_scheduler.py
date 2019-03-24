import urllib
import requests
import json
from collections import defaultdict
from collections import OrderedDict
import sys
import os
import datetime

'''
Author: Sankarshan Umesh Bhat
Date: 12/21/2018

'''
class Schedules:
    def __init__(self, api_key,cmd,url):
    	self.api_key = api_key
    	self.cmd = cmd
    	self.url = url
    	#we can add all the station code to name mapping here. for now I have added only 1 
    	self.station_code_to_name_dict = {'mont':'Montgomery St. (SF)'}

    def display_output(self,sorted_list,source):
    	print "----------------------------------------------------------------------"
    	currentDT = datetime.datetime.now()
    	cur_time = currentDT.strftime("%I:%M:%S %p")
    	print "Current time:",cur_time,"  Source Station:",self.station_code_to_name_dict[source]
    	print ""

    	print "Soonest availabe trains with destination"
    	print "----------------------------------------------------------------------"
    	print "Departure_time","    Destination"
    	print "(from now)"
    	print "----------------------------------------------------------------------"
    	for element in sorted_list:
	    		print element[0]," min            ",element[1]

    def order_destinations(slef,sorted_destination,sorted_list):
    	i =0
    	for key,val in sorted_destination.iteritems():
	    		dst_list = val
	    		for dst in dst_list:
	    			if i < 10:
	    				sorted_list.append((key,dst))
	    				i += 1
	    			else:
	    				return
	  

	'''
	Note : test data is used only when we invoke with isTestMode set to true
	and in this case the function wont fetch the data from the API
	'''
    def fetch_real_time_schedule(self,origin_station,result_len,isTestMode=False,test_data=None):
    	request_url = self.url +  \
        					urllib.urlencode({'cmd':self.cmd,
                              'orig':origin_station,
                              'key':self.api_key,'json':'y'})

        # if testMode is enabled dont make the API call
        if isTestMode:                                                            
    		json_response = test_data
    	else:
    		response = requests.get(request_url)
    		json_response = json.loads(response.content)


    	'''
    	iterate the station list and creates a destination_dict dictionary 
    	which contians information about for which minute we have train to
    	particualr destination.
    	'''

    	try:
    		destination_dict =defaultdict(dict)
    		#make sure key 'root' exist in the json_response
    		if json_response.get('root') != None :
    			#make sure key 'station' exist in the json_response
    			if 'station' in json_response['root']:
	    			station_list = json_response['root']['station']
	    			#make sure station_list is not empty
	    			if len(station_list) > 0:
	    				for station in station_list:
	    					destinations = station.get('etd')
	    					#make sure destinations is not empty
	    					if destinations != None and len(destinations) > 0:
	    						for dst in destinations:
	    							dst_station = dst.get('destination')
	    							# if destination station name is absetn in the response then dont include thar station in the final result
	    							if dst_station == None or dst_station =="":
	    								continue
	    							estimates = dst.get('estimate')
	    							#make sure estimates is not empty
	    							if estimates != None and len(estimates) > 0:
	    								for est in estimates:
	    									minute = est.get('minutes')
	    									#make sure minutes exist in the est dict
	    									if minute !=None and minute != "":
		    									'''
		    									If the value of the minute is leaving, it means train is going to leave now so min should
		    									be set to 0 otherwise convert it to the number and add it in a dictionary
		    									'''
		    									if minute.lower() == 'leaving':
		    										minute = 0
		    									else:
		    										#conver to int so that we can sort it later
		    										minute = int(minute)

		    									'''
		    									handle the case wherein if we have a multiple destinations with same departure
		    									time. 
		    									if we have minute in the dict already then I append the destination station to the min list 
		    									else create the new list with minute as the key and add the station.
		    									'''

		    									if minute in destination_dict:
		    										destination_dict[minute].append(dst_station)
		    									else:
		    										destination_dict[minute] =[]
		    										destination_dict[minute].append(dst_station)

	    	#Sort the dict based on minute so that we get the destination with soonest departure first
	    	# in case of identical departure times it displays both the destinations with the order same as that of original API.
	    	sorted_destination = OrderedDict(sorted(destination_dict.items(), key=lambda t: t[0]))
	    	#print sorted_destination
	    	sorted_list =[]
	    	self.order_destinations(sorted_destination,sorted_list)
	    	self.display_output(sorted_list,origin_station)

	    	
	    	

    	except Exception as e:
    		exc_type, exc_obj, exc_tb = sys.exc_info()
    		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    		print(exc_type, fname, exc_tb.tb_lineno)
    		print "exception",e
    	

if __name__ == '__main__':
	url = 'http://api.bart.gov/api/etd.aspx?'
	api_key = 'MW9S-E7SL-26DU-VV8V'
	cmd = 'etd'
	schedules_obj = Schedules(api_key,cmd,url)
	'''
	I have written the code such that the function takes the destination and number of destinations
	to be included in the final result as the input so that we can pass the values as we wish. 
	'''
	schedules_obj.fetch_real_time_schedule('mont',10)

	'''
	I have included the below Test cases to check the functionality of the code
	'''
	#test case 1 
	'''
	pass empty stations -> the program displays empty results
	'''
	test_dat = { "root": { "uri": { "#cdata-section": "http://api.bart.gov/api/etd.aspx?json=y&cmd=etd&orig=mont" }, "station": [], "time": "06:17:31 PM PST", "date": "12/21/2018", "message": "", "@id": "1" }, "?xml": { "@version": "1.0", "@encoding": "utf-8" } }
	schedules_obj.fetch_real_time_schedule('mont',10,True,test_dat)

	#test case 2 
	'''
	pass two destinations with same departure time 
	in this case  Daly City and Dublin/Pleasanton both depart in 9 mins
	'''
	test_dat = {"root": {"uri": {"#cdata-section": "http://api.bart.gov/api/etd.aspx?json=y&cmd=etd&orig=mont"}, "station": [{"name": "Montgomery St.", "etd": [{"abbreviation": "ANTC", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "12"}, {"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "26"}, {"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "41"}], "destination": "Antioch"}, {"abbreviation": "DALY", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#0099cc", "minutes": "1"}, {"direction": "South", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#339933", "minutes": "9"}, {"direction": "South", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#0099cc", "minutes": "16"}], "destination": "Daly City"}, {"abbreviation": "DUBL", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "9"}, {"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "24"}, {"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "39"}], "destination": "Dublin/Pleasanton"}, {"abbreviation": "MLBR", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "RED", "delay": "80", "platform": "1", "length": "9", "hexcolor": "#ff0000", "minutes": "6"}, {"direction": "South", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ff0000", "minutes": "20"}, {"direction": "South", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ff0000", "minutes": "35"}], "destination": "Millbrae"}, {"abbreviation": "RICH", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#ff0000", "minutes": "4"}, {"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "8", "hexcolor": "#ff0000", "minutes": "19"}, {"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#ff0000", "minutes": "34"}], "destination": "Richmond"}, {"abbreviation": "SFIA", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "13"}, {"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "43"}, {"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "58"}], "destination": "SF Airport"}, {"abbreviation": "MLBR", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "28"}], "destination": "SFO/Millbrae"}, {"abbreviation": "WARM", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "15"}, {"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "29"}, {"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "44"}], "destination": "Warm Springs"}], "abbr": "MONT"}], "time": "06:30:46 PM PST", "date": "12/21/2018", "message": "", "@id": "1"}, "?xml": {"@version": "1.0", "@encoding": "utf-8"}}
	schedules_obj.fetch_real_time_schedule('mont',10,True,test_dat)

	#test case 3 
	'''
	pass few destinations with departure time as 'Leaving' (indicated train will leave in 0 min)
	in this case  for destations Antioch and  Daly City train will leave in 0 min(leaving)
	'''
	test_dat = {"root": {"uri": {"#cdata-section": "http://api.bart.gov/api/etd.aspx?json=y&cmd=etd&orig=mont"}, "station": [{"name": "Montgomery St.", "etd": [{"abbreviation": "ANTC", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "Leaving"}, {"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "26"}, {"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "41"}], "destination": "Antioch"}, {"abbreviation": "DALY", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#0099cc", "minutes": "Leaving"}, {"direction": "South", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#339933", "minutes": "9"}, {"direction": "South", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#0099cc", "minutes": "16"}], "destination": "Daly City"}, {"abbreviation": "DUBL", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "9"}, {"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "24"}, {"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "39"}], "destination": "Dublin/Pleasanton"}, {"abbreviation": "MLBR", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "RED", "delay": "80", "platform": "1", "length": "9", "hexcolor": "#ff0000", "minutes": "6"}, {"direction": "South", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ff0000", "minutes": "20"}, {"direction": "South", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ff0000", "minutes": "35"}], "destination": "Millbrae"}, {"abbreviation": "RICH", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#ff0000", "minutes": "4"}, {"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "8", "hexcolor": "#ff0000", "minutes": "19"}, {"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#ff0000", "minutes": "34"}], "destination": "Richmond"}, {"abbreviation": "SFIA", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "13"}, {"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "43"}, {"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "58"}], "destination": "SF Airport"}, {"abbreviation": "MLBR", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "28"}], "destination": "SFO/Millbrae"}, {"abbreviation": "WARM", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "15"}, {"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "29"}, {"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "44"}], "destination": "Warm Springs"}], "abbr": "MONT"}], "time": "06:30:46 PM PST", "date": "12/21/2018", "message": "", "@id": "1"}, "?xml": {"@version": "1.0", "@encoding": "utf-8"}}
	schedules_obj.fetch_real_time_schedule('mont',10,True,test_dat)

	#test case 4 
	'''
	pass destination station name empty to make sure we dont incude that in the final result
	in this case the first two destinations which corresponds to 0th min is passed as empty
	so the final result should not include any destinations with departure time as 0th min.
	'''
	test_dat = {"root": {"uri": {"#cdata-section": "http://api.bart.gov/api/etd.aspx?json=y&cmd=etd&orig=mont"}, "station": [{"name": "Montgomery St.", "etd": [{"abbreviation": "ANTC", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "Leaving"}, {"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "26"}, {"direction": "North", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#ffff33", "minutes": "41"}], "destination": ""}, {"abbreviation": "DALY", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#0099cc", "minutes": "Leaving"}, {"direction": "South", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#339933", "minutes": "9"}, {"direction": "South", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#0099cc", "minutes": "16"}], "destination": ""}, {"abbreviation": "DUBL", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "9"}, {"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "24"}, {"direction": "North", "bikeflag": "1", "color": "BLUE", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#0099cc", "minutes": "39"}], "destination": "Dublin/Pleasanton"}, {"abbreviation": "MLBR", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "RED", "delay": "80", "platform": "1", "length": "9", "hexcolor": "#ff0000", "minutes": "6"}, {"direction": "South", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ff0000", "minutes": "20"}, {"direction": "South", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ff0000", "minutes": "35"}], "destination": "Millbrae"}, {"abbreviation": "RICH", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#ff0000", "minutes": "4"}, {"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "8", "hexcolor": "#ff0000", "minutes": "19"}, {"direction": "North", "bikeflag": "1", "color": "RED", "delay": "0", "platform": "2", "length": "9", "hexcolor": "#ff0000", "minutes": "34"}], "destination": "Richmond"}, {"abbreviation": "SFIA", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "13"}, {"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "43"}, {"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "58"}], "destination": "SF Airport"}, {"abbreviation": "MLBR", "limited": "0", "estimate": [{"direction": "South", "bikeflag": "1", "color": "YELLOW", "delay": "0", "platform": "1", "length": "10", "hexcolor": "#ffff33", "minutes": "28"}], "destination": "SFO/Millbrae"}, {"abbreviation": "WARM", "limited": "0", "estimate": [{"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "15"}, {"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "29"}, {"direction": "North", "bikeflag": "1", "color": "GREEN", "delay": "0", "platform": "2", "length": "10", "hexcolor": "#339933", "minutes": "44"}], "destination": "Warm Springs"}], "abbr": "MONT"}], "time": "06:30:46 PM PST", "date": "12/21/2018", "message": "", "@id": "1"}, "?xml": {"@version": "1.0", "@encoding": "utf-8"}}
	schedules_obj.fetch_real_time_schedule('mont',10,True,test_dat)

	#test case 5 -> Make the HTTP call
	schedules_obj.fetch_real_time_schedule('mont',10)