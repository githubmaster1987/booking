import requests
import config_scrapy

def solve_captcha(url, captcha_site_key, n_value):
    #
    s = requests.Session()

    # here we post site key to 2captcha to get captcha ID (and we parse it here too)
    captcha_id = s.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(config_scrapy.captcha_api_key, captcha_site_key, url)).text.split('|')[1]
    # then we parse gresponse from 2captcha response
    recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(config_scrapy.captcha_api_key, captcha_id)).text

    print("***********************solving ref captcha************************")

    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        sleep(5)
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(config_scrapy.captcha_api_key, captcha_id)).text
    recaptcha_answer = recaptcha_answer.split('|')[1]

    print("^^^^^^^^^^^^^^^^^^^^^^^solved ref captcha^^^^^^^^^^^^^^^^^^^^^^^^^")

    # # we make the payload for the post data here, use something like mitmproxy or fiddler to see what is needed
    params = {
        'n': n_value,
        'g-recaptcha-response': recaptcha_answer  # This is the response from 2captcha, which is needed for the post request to go through.
        }
    # response = s.post(url, params)
    # print response.request.headers
    # print response.headers
    return params
