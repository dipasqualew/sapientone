from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sapientone.dependencies import get_env_vars, ExpectedEnvironmentVariables

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_api_keys(
    env_vars: ExpectedEnvironmentVariables = Depends(get_env_vars),
):
    return [env_vars.SAPIENTONE_API_KEY]


def api_key_auth(
    api_keys: list[str] = Depends(get_api_keys),
    api_key: str = Depends(oauth2_scheme),
):
    if api_key not in api_keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden")
