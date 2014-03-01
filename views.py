from django.http import HttpResponse, Http404
from django.template import RequestContext as RC
from django.shortcuts import render_to_response as rr, redirect
from hashlib import sha256
import urllib
import urllib2
from xml.etree.ElementTree import XML
import hmac
from django.views.decorators.csrf import csrf_exempt

# SET THESE PARAMETER VALUES # 
MOBIKWIK_MERCHANT_ID = "" # enter your merchant ID
MOBIKWIK_SECRET_KEY = ""  # enter the secret key 
TEST_MODE = False  # make it true or false for switching mode of wallet to test or live.

def remote_call(url):
    data = ""            
    try: 
        print url                         
	reqt = urllib2.Request(url)
	response = urllib2.urlopen(reqt)
	data = str(response.read().strip())
        print data
    except Exception as e : 
	print "Error occur = %s" % e 
    return data
	
def send_checksum_string(orderid):
    action = 'gettxnstatus'; # fixed value
    checksum_string = "'%s''%s''%s'" % (action,MOBIKWIK_MERCHANT_ID,orderid)
    print MOBIKWIK_MERCHANT_ID
    return checksum_string
	
def make_checksum(checksum_string) : 
    a = hmac.new(MOBIKWIK_SECRET_KEY,checksum_string,sha256)
    checksum = a.digest().encode('hex')
    print "checksum >>>> %s" % checksum
    return checksum

# receive the response from mobikwik wallet at this function //
# This contains val = all post parameters sent by mobikwik 
@csrf_exempt 
def wallet_mobikwik_response(req):
    if req.POST : 
        val = req.POST
	if val['statuscode'] == "0" or val['statuscode'] == 0 : 
	    orderid = val['orderid']
            ACTUAL_AMOUNT = 10  # provide here the actual amount of the current orderid from your database or session
	    if float(ACTUAL_AMOUNT) == float(val['amount']) : 
	        csumstring = send_checksum_string(orderid)
		sndchecksum = make_checksum(csumstring)
                if TEST_MODE == False : MOBIKWIK_CHECK_STATUS_URL = "https://www.mobikwik.com/wallet.do"
                else : MOBIKWIK_CHECK_STATUS_URL = "https://test.mobikwik.com/mobikwik/wallet.do"
		MOBIKWIK_CHECK_STATUS_URL += "?action=gettxnstatus&mid=%s&checksum=%s&orderid=%s" % (MOBIKWIK_MERCHANT_ID,sndchecksum,orderid)
		data = remote_call(MOBIKWIK_CHECK_STATUS_URL)
		try : 
	        	tree = XML(data)
			try : 
			    amount2 = tree.find('.//amount').text 
			except Exception as e :
			    print "amount not found"
			try : 
			    statuscode2 = tree.find('.//statuscode').text 
			except Exception as e :
			    print "statuscode not found"
			try : 
			    orderid2 = tree.find('.//orderid').text 
			except Exception as e :
			    print "orderid not found"
			try : 
			    refid2 = tree.find('.//refid').text 
			except Exception as e :
			    print "refid not found"					
			try : 
			    statusmessage2 = tree.find('.//statusmessage').text 
			except Exception as e :
			    print "statusmessage not found"
			try : 
			    ordertype2 = tree.find('.//ordertype').text 
			except Exception as e :
			    print "ordertype not found"
			try : 
			    checksum2 = tree.find('.//checksum').text 
			except Exception as e :
			    print "checksum not found"
			ckstring2 = "'%s''%s''%s''%s''%s''%s'" % (statuscode2,orderid2,refid2,amount2,statusmessage2,ordertype2)
		        if statuscode2 == "0" or statuscode2 == 0 :
		            # now match checksum
                            cksum2 = make_checksum(ckstring2)	
                            if cksum2 == checksum2 and float(amount2) == float(ACTUAL_AMOUNT) and orderid2 == orderid :
				# now mark a txns as paid 
				return HttpResponse("Transaction Successful")
					
                            else : 
				return HttpResponse("Fraud Detected")
			else : 
			    return HttpResponse("Transaction failed because of reason = %s" % statusmessage2)
		except Exception as e: 
		    return HttpResponse("Error Occur  = %s" % e )
        				
	    else : 
		return HttpResponse("Txn Failed ! Fraud Detected")			
	else : 
	    return HttpResponse("Txn Failed Because of reason : %s" % val['statusmessage'])
    else : 
        return HttpResponse("No Parameters received")
        		
