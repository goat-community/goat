class Config(object):
    PORT = 5000
    DEBUG = False
    TESTING = False
    REMOTE_DEBUGGING = False


class ProductionConfig(Config):
    DEBUG = False
class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True


class DebuggingConfig(Config):
    REMOTE_DEBUGGING = True
    REMOTE_DEBUGGING_PORT = 3000


object_name = {
    'production': 'config.ProductionConfig',
    'development': 'config.DevelopmentConfig',
    'testing': 'config.TestingConfig',
    'debugging': 'config.DebuggingConfig',
}
