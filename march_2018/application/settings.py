DATABASES = {
    'default': {
        'provider': 'postgresql',
        'username': 'postgres',
        'password': '',
        'host': 'database',
        'name': 'steam',
    }
}

CREDENTIALS = {
    'steam': {
        'api_key': '',
        'username': '',
        'password': '',
        'guard': {
            'steamid': '',
            'shared_secret': '',
            'identity_secret': ''
        }
    }
}
