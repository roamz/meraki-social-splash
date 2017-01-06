# Cisco Meraki Splash Page Server with Social OAuth
Provide a free Wifi internet service to your customers in exchange for gaining valuable customer insights through their social media profiles.

## Overview

This Python Flask application demonstrates how the Cisco Meraki External Captive Portal API can be used for delivering a custom Captive Portal / Splash Page using Social networks for authentication on Cisco Meraki access points.

### Technology

This is Python Flask app that supports signin to Facebook, Instagram, Twitter, Weibo and Wechat using the Flask-oauthlib and can be extended to support any oAuth authentication API.

Other technologies used:
* Docker
* Nginx
* uWSGI

### Credit


|[![alt text](https://s3.amazonaws.com/localmeasure-static/assets/logo_full.png "Local Measure, 2017")](https://www.localmeasure.com)|&|[![alt text](https://meraki.cisco.com/img/cisco-meraki.png "Cisco Meraki")](https://meraki.cisco.com)|
| :-------------: |:--------: |:-------------:| 



# Meraki Setup

## Configure an SSID on your Cisco Meraki network

* Logon to the Meraki Dashboard
* Navigate to the configuration overview for your selected network
* Select an SSID for the list and select Edit Settings or create a new SSID
* Under Splash Page select the Click-Through option.
* Scroll down the page and enable the "Walled garden" for the following sites:

```
path.to.your.splash.com
*.facebook.com
*.fbcdn.net
*.facebook.net
*.akamaihd.net
*.instagram.com
api.weibo.com
*.twitter.com
*.twimg.com
```

Note: The Walled Garden is to provide access to your splash page content prior to authentication. You might need to contact the Meraki support team and ask them to "enable domain based walled garden support".

## Configure the Splash Page

* Logon to the Meraki Dashboard
* Navigate to the configuration overview for your selected network
* Select 'Splash Page' configuration
* For the Splash Page url use http://path.to.your.splash.com/meraki/


# Running the Flask App

## Clone and set up the the app
```
git clone "https://github.com/localmeasure/meraki-social-splash"
pip install -r requirements.txt
```   

## Environment configuration

The server uses environment variable to store the app configuration, this keeps sensitive oauth keys safe.
See here for a list of keys that can be configured: https://github.com/localmeasure/meraki-social-splash/blob/master/main.py#L18-L25

### - example bash shell export script
```
// splash-exports.sh
export INSTAGRAM_CONSUMER_KEY=ibrwi7fw34gi7wfg33
export INSTAGRAM_CONSUMER_SECRET=ibrwi7fw34gi7wfg33ibrwi7fw34gi7wfg33
```

## Run the server using Python

This will run the server in debug mode using python
```
source splash-exports.sh
python main.py
```

## Run the server for production environments

To run this app in production, use Docker. The docker file included uses an Ubuntu base image configured for Nginx and uWSGI and can be used on your local machine using docker.
```
make dockerize
```
The server will be running on http://localhost:5000/ (you will probably need to set your environment variables in the Dockerfile or some other method)

# Help

## Testing and demos

To show the oauth workflow without requiring it to be connected to a Meraki access point you can open an example splash page at http://localhost:5000/ or http://path.to.your.splash.com/ and sign in through social.

## How does EXCAP work

For more into about Cisco Meraki External Captive Portal (EXCAP) see here: https://meraki.cisco.com/lib/pdf/meraki_whitepaper_captive_portal.pdf


## Warranty

This source code is intended as a prototype and proof of concept. It comes with no warranty or guarantees. Please contact us via [Issues](https://github.com/localmeasure/meraki-social-splash/issues) for help or to contribute to this code.

Cheers!
