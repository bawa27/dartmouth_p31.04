#Python 3
import http.client as httplib
import urllib.parse as urllib
import time
from xml.dom.minidom import parseString

host = "gea.esac.esa.int"
port = 443
pathinfo = "/tap-server/tap/async"


#-------------------------------------
#Create job

params = urllib.urlencode({\
	"REQUEST": "doQuery", \
	"LANG":    "ADQL", \
	"FORMAT":  "csv", \
	"PHASE":  "RUN", \
	"JOBNAME":  "Any name (optional)", \
	"JOBDESCRIPTION":  "Any description (optional)", \
	"QUERY":   "SELECT g.source_id,g.parallax,g.parallax_error,g.phot_g_mean_mag,g.bp_rp FROM gaiaedr3.gaia_source as g WHERE g.parallax > 12 AND g.parallax_over_error > 15 AND g.phot_g_mean_flux_over_error>100 AND g.phot_rp_mean_flux_over_error>40 AND g.phot_bp_mean_flux_over_error>40 AND g.ruwe < 1.4 AND g.astrometric_excess_noise < 1.8"                          
	})

headers = {\
	"Content-type": "application/x-www-form-urlencoded", \
	"Accept":       "text/plain" \
	}

connection = httplib.HTTPSConnection(host, port)
connection.request("POST",pathinfo,params,headers)

#Status
response = connection.getresponse()
print ("Status: " +str(response.status), "Reason: " + str(response.reason))

#Server job location (URL)
location = response.getheader("location")
print ("Location: " + location)

#Jobid
jobid = location[location.rfind('/')+1:]
print ("Job id: " + jobid)

connection.close()

#-------------------------------------
#Check job status, wait until finished

while True:
	connection = httplib.HTTPSConnection(host, port)
	connection.request("GET",pathinfo+"/"+jobid)
	response = connection.getresponse()
	data = response.read()
	#XML response: parse it to obtain the current status
	#(you may use pathinfo/jobid/phase entry point to avoid XML parsing)
	dom = parseString(data)
	phaseElement = dom.getElementsByTagName('uws:phase')[0]
	phaseValueElement = phaseElement.firstChild
	phase = phaseValueElement.toxml()
	print ("Status: " + phase)
	#Check finished
	if phase == 'COMPLETED': break
	#wait and repeat
	time.sleep(0.2)


connection.close()

#-------------------------------------
#Get results
connection = httplib.HTTPSConnection(host, port)
connection.request("GET",pathinfo+"/"+jobid+"/results/result")
response = connection.getresponse()
data = response.read().decode('iso-8859-1')
#print(type(data))
#print(data)
outputFileName = "example_output.cvs"
outputFile = open(outputFileName, "w")
outputFile.write(data)
outputFile.close()
connection.close()
print ("Data saved in: " + outputFileName)
