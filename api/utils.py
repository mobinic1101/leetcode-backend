import requests

def send_post_request(url, data=None, files=None, **kwargs):
    response = requests.post(url, data=data, files=files, **kwargs)
    return response