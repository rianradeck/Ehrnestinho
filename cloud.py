import os

from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

load_dotenv()
ENDPOINT = os.getenv("VM_ENDPOINT")


def get_auth():
    credential_file = "./gccred.json"

    credentials = service_account.Credentials.from_service_account_file(
        credential_file
    )
    scoped_credentials = credentials.with_scopes(
        ["https://www.googleapis.com/auth/cloud-platform"]
    )

    return AuthorizedSession(scoped_credentials)


session = get_auth()


def start_vm():
    if get_info()["status"] == "RUNNING":
        return 0

    response = session.post(f"{ENDPOINT}/start")

    if response.status_code != 200:
        raise Exception(
            "GC API was not able to start the VM. "
            f"Returned with {response.status_code}"
        )

    return response.status_code


def stop_vm():
    if get_info()["status"] == "TERMINATED":
        return 0

    response = session.post(f"{ENDPOINT}/stop")

    if response.status_code != 200:
        raise Exception(
            "GC API was not able to start the VM. "
            f"Returned with {response.status_code}"
        )

    return response.status_code


def get_info():
    response = session.get(url=ENDPOINT)

    if response.status_code != 200:
        raise Exception(
            "GC API was not able to start the VM. "
            f"Returned with {response.status_code}"
        )

    return response.json()


if __name__ == "__main__":
    print(get_info())
    pass
