import os


DATABASE = {
    'qqp': {
        'host': os.environ.get('DATABASE_HOST'),
        'username': os.environ.get('DATABASE_USERNAME'),
        'password': os.environ.get('DATABASE_PASSWORD'),
        'port': int(os.environ.get('DATABASE_PORT', '5432'))
    }
}


