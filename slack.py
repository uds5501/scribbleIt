import requests


def slack(mess):
    url = "https://hooks.slack.com/services/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"

    # mess = "It disds sffd"
    payload = {'text': mess}
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        'Postman-Token': "bc268f50-6b0d-4d2c-a9fa-dbbc96a57297"
        }

    response = requests.request("POST", url, data=str(payload), headers=headers)

    print(response.text)
