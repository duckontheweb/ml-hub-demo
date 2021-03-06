from typing import Any, Iterator, List, Mapping
import os
import pathlib
from urllib.parse import urljoin
from functools import lru_cache

import toml
import requests.auth

MLHUB_URL = 'https://api.radiant.earth/mlhub/v1/'
MLHUB_CONFIG_FILE = '.ml-hub'
MLHUB_ENV_VARIABLE = 'MLHUB_API_TOKEN'


class BearerTokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['authorization'] = f'Bearer {self.token}'
        return r


class Session(requests.Session):
    """Custom session class that adds the auth token and the "accept" header."""
    def __init__(self, api_token):
        super().__init__()
        self.headers = {
            **self.headers,
            'accept': 'application/json'
        }
        self.auth = BearerTokenAuth(api_token)

    @classmethod
    def from_environment(cls):
        """Gets the session instance by looking for a MLHUB_API_TOKEN environment variable for the API token.

        Returns
        -------
        session : Session

        Raises
        ------
        EnvironmentError
            If no MLHUB_API_TOKEN environment variable is found.
        """
        if MLHUB_ENV_VARIABLE not in os.environ:
            raise EnvironmentError(f'Could not find {MLHUB_ENV_VARIABLE} in environment variables.')
        return cls(api_token=os.environ['MLHUB_API_TOKEN'])

    @classmethod
    def from_config(cls):
        """
        Gets the session instance by looking for a .ml-hub TOML file in either the current working directory or the user's home directory
        and getting the API token from the ``auth.api_token`` value in this file.

        Returns
        -------
        session : Session

        Raises
        ------
        FileNotFoundError
            If no config file could be found in either the current working directory or the user home directory.
        ValueError
            If no ``auth.api_token`` property is found in the TOML config file.
        """
        config_path = os.path.join(os.getcwd(), MLHUB_CONFIG_FILE)
        if not os.path.exists(config_path):
            os.path.join(pathlib.Path.home(), MLHUB_CONFIG_FILE)

        if not config_path:
            raise FileNotFoundError(f'Could not find {MLHUB_CONFIG_FILE} file in CWD or user home directory.')

        with open(config_path, 'r', encoding='utf-8') as src:
            config = toml.load(src)

        api_token = config.get('auth', {}).get('api_token')
        if not api_token:
            raise ValueError(f'No auth.api_token property found in {config_path}.')
        return cls(api_token=api_token)


@lru_cache(maxsize=None)
def get_session(api_token: str = None) -> requests.Session:
    """
    Get a class:`requests.Session` instance that uses Bearer token authentication to make requests. If an ``api_token`` argument is given, this
    will be used as the API Token when authenticating with ML Hub. If this value is ``None``, then it will first try to fetch the token from a
    MLHUB_API_TOKEN environment variable. If this environment variable is not found, it will try to find a ``.ml-hub`` TOML config file (first in the
    current working directory and then in the user home directory) and will use any ``auth.api_token`` value found there as the API token.

    Parameters
    ----------
    api_token : str, optional
        An API token to use when creating the session. If not provided, will attempt to get the API token from the environment or a .ml-hub config file.

    Returns
    -------
    session : Session
    """
    if api_token:
        return Session(api_token=api_token)
    try:
        return Session.from_environment()
    except EnvironmentError:
        return Session.from_config()


def get(path, *, api_token: str = None, **kwargs) -> dict:
    """Makes a GET request to the given ``path``. ``path`` may be either a relative path (in which case it will be joined to the ML Hub root URL), or an
    absolute URL.

    Parameters
    ----------
    path : str
        The path to which the GET request will be made.
    api_token : str, optional
        An optional ML Hub API Token to use to make the request. This will be passed to :func:`get_session`.
    kwargs : dict, optional
        Additional keyword arguments to pass along to the :func:`requests.get` method. Note that these will `override` any default
        values for these keyword arguments rather than merge them.

    Returns
    -------
    dict : response
        The JSON response as a dictionary.

    Raises
    ------
    requests.exceptions.HTTPError
        If an API error is encountered.
    """

    s = get_session(api_token=api_token)
    r = s.get(urljoin(MLHUB_URL, path), **kwargs)

    r.raise_for_status()

    return r.json()


def paginate(link: str, items_property: str = 'features') -> Iterator[Any]:
    """Paginates through the results for the given link by recursively following any links found in the response with a "rel" type of "next". If the response
    is a list, then it will yield each item from the list. If the response is a dictionary/mapping, then it will get the value of the ``items_property`` in
    the mapping (defaults to ``"features"``) and yield each item found in that iterable.

    Parameters
    ----------
    link : str
        The original link for which to retrieve results.
    items_property : str, optional
        The property containing the individual items to yield.

    Yields
    -------
    item : Any
        Individual items as found in the ``items_property`` list.

    Raises
    ------
    ValueError
        If not list of items can be parsed from the response.
    """
    while True:
        # Fetch the response and parse the list of items
        r = get(link)
        if isinstance(r, List):
            items = r
        elif isinstance(r, Mapping):
            items = r.get(items_property)
        else:
            raise ValueError(f'Could not parse list of items from response of type {type(r)}')

        yield from iter(items)

        # Find a "next" link, if it exists, otherwise break
        link = next((link_ for link_ in r['links'] if link_['rel'] == 'next'), {'href': None})['href']
        if not link:
            break
