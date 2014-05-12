Payment Module : Mobikwik Wallet
***********************************************************************
   
Mobikwik Wallet - Adding money to your wallet lets you pay for your services and recharges in just one click, or even via SMS or by dialling a number.
	
Our aim is to solve the payment pain points for eCommerce in India.
		
***********************************************************************

Introduction :
When you Extract the zip file, it has five files
    - index.html
    - views.py
    - urls.py (contains urls mapped to corresponding views)
    - settings.py (contains settings for Django)
    
************************************************************************

DESCRIPTION :

1) Whole payment test can be made on test server with prefilled details or on live with details you received from mobikwik after your merchant acount is activated . Please find below description of the major files present in the integration kit:

* index.html - This is a sample form where you have to insert the User's order id, amount, email, merchantname. 
Merchant Id is pre-filled with default values which are used in testing mode. 
			  
* views.py - In this file, you can set the configuration settings for the integration. You can specify your live merchant id, secret key, test mode here. The kit is by default prefilled with the test credentials.
    
    This file also contains the function posttomobikwik which recieves the POST request from index.html file, calculates the checksum and sends the parameters to the Mobikwik URL. 
	
    This file also handles the response from mobikwik. The function mobikwik_wallet_response will be called at time of response from mobikwik. Please provide redirect url(in index.html) which is the url to this function. This response is received as an XML file with parameters: 
		1. Status Code: 0 for success, and not 0 for error. 
		2. Status message: Success or Failure. 
		3. Order Id
		4. Ref Id
		5. Amount
		6. Order type
		7. Checksum
	In this verification process, the checksum received, amount received and received order id are compared to the ones we sent.
	
* urls.py - This file contains the mappings for urls to corresponding views. 

************************************************************************
Note: To get Mobikwik wallet Merchant Id and Secret Key, you need to signup at http://wallet.mobikwik.com and fill in the details under integration tab. 
As you fill in all the required details, you will be provided with a merchant id and a secret key that will be generated there at http://wallet.mobikwik.com  
		
***********************************************************************
