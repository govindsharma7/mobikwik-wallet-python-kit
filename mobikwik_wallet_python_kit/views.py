from django.http import HttpResponse, Http404
from django.template import RequestContext as RC
from django.shortcuts import render_to_response
from hashlib import sha256
import urllib
import urllib2
from xml.etree.ElementTree import XML
import hmac
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf

# SET THESE PARAMETER VALUES # 
MOBIKWIK_MERCHANT_ID = "MBK9002" # enter your merchant ID. Test Merchant ID Prefilled.
MOBIKWIK_SECRET_KEY = "ju6tygh7u7tdg554k098ujd5468o"  # enter the secret key. Test Secret ID prefilled.
TEST_MODE = True  # make it true or false for switching mode of wallet to test or live.

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
    checksum_string = "'%s''%s'" % (MOBIKWIK_MERCHANT_ID,orderid)
    print MOBIKWIK_MERCHANT_ID
    return checksum_string
    
def make_checksum(checksum_string) : 
    a = hmac.new(MOBIKWIK_SECRET_KEY,checksum_string,sha256)
    checksum = a.digest().encode('hex')
    print "checksum >>>> %s" % checksum
    return checksum

def calculate_response_checksum(statuscode, orderid, amount, statusmessage):
    checksum_string = "'%s''%s''%s''%s''%s'" % (statuscode, orderid, amount, statusmessage, MOBIKWIK_MERCHANT_ID)
    a = hmac.new(MOBIKWIK_SECRET_KEY,checksum_string,sha256)
    checksum = a.digest().encode('hex')
    return checksum

# receive the response from mobikwik wallet at this function //
# This contains val = all post parameters sent by mobikwik
@csrf_exempt
def mobikwik_wallet_response(req):
    if req.POST :
        val = req.POST
        responseChecksum = calculate_response_checksum(val['statuscode'], val['orderid'], val['amount'], val['statusmessage'])
        if(responseChecksum == val['checksum']):
            if val['statuscode'] == "0" or val['statuscode'] == 0 :
                orderid = val['orderid']
                ACTUAL_AMOUNT = 200  # provide here the actual amount of the current orderid from your database or session
                if float(ACTUAL_AMOUNT) == float(val['amount']) :
                    csumstring = send_checksum_string(orderid)
                    sndchecksum = make_checksum(csumstring)
                    if(TEST_MODE == False):
                        MOBIKWIK_CHECK_STATUS_URL = "https://www.mobikwik.com/checkstatus"
                    else: 
                        MOBIKWIK_CHECK_STATUS_URL = "https://test.mobikwik.com/mobikwik/checkstatus"
                    MOBIKWIK_CHECK_STATUS_URL += "?mid=%s&checksum=%s&orderid=%s" % (MOBIKWIK_MERCHANT_ID,sndchecksum,orderid)
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
                            cksum2 = make_checksum(ckstring2)    
                            if cksum2 == checksum2 and float(amount2) == float(ACTUAL_AMOUNT) and orderid2 == orderid :
                                # now mark a txns as paid 
                                return HttpResponse("Transaction Successful")
                            else: 
                                return HttpResponse("Fraud Detected")
                        else : 
                            return HttpResponse("Transaction failed because of reason = %s" % statusmessage2)
                    except Exception as e: 
                        return HttpResponse("Error Occur  = %s" % e )
                                
                else : 
                    return HttpResponse("Txn Failed ! Fraud Detected")            
            else : 
                return HttpResponse("Txn Failed Because of reason : %s" % val['statusmessage'])
        else:
            return HttpResponse("Txn Failed! Fraud Detected. Response Checksum did not match")        
    else : 
        return HttpResponse("No Parameters received")
            
def posttomobikwik(req):
    phone = req.POST['cell']
    email = req.POST['email']
    amount = req.POST['amount']
    orderid = req.POST['orderid']
    mid = MOBIKWIK_MERCHANT_ID
    returnurl = req.POST['redirecturl']
    string = "'%s''%s''%s''%s''%s''%s'" % (phone,email,amount,orderid,returnurl,mid)
    checksum = make_checksum(string)
    parameters = {"cell" : str(phone) , "email" : email , "amount" : str(amount) , "orderid" : str(orderid) , "mid" : mid , "redirecturl" : str(returnurl) , "checksum" : checksum}

    body = ''
    if(TEST_MODE == True):
        body = """<html><body style="display:none"><form name="myform" id="demo_form" action="https://test.mobikwik.com/mobikwik/wallet" method="POST">"""
    else:
        body = """<html><body style="display:none"><form name="myform" id="demo_form" action="https://www.mobikwik.com/wallet" method="POST">"""

    for key,val in parameters.items(): body += """<input type="hidden" name = "%s" value="%s"><br/>""" % (key,val)
    body += """</body><script>document.myform.submit();</script></html>"""
    return HttpResponse(body)

@csrf_exempt
def index(request):
	return render_to_response('index.html')
                
