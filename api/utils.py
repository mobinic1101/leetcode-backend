import requests
import docker
from django.conf import settings

def send_post_request(url, data=None, files=None, **kwargs):
    response = requests.post(url, data=data, files=files, **kwargs)
    return response


def start_code_runner_container():
    client = docker.from_env()
    container = client.containers.run(
        image="code-runner-image",
        detach=True,
        ports={"5000/tcp": settings.CODE_RUNNER_PORT},
        auto_remove=True,
        name="code-runner-container")
    # !!! warning the above function is not at its final state.