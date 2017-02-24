"""
Module for booting up the application
"""

import os, json
import measure, persistence


class App(object):
    """
    Application main class
    """

    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self._config = None

    @property
    def config(self):
        """
        Getter for config
        """
        if self._config is None:
            raise ValueError('Call boot before accessing configuration')
        return self._config

    @config.setter
    def config(self, value):
        """
        Setter for config
        """
        self._config = value

    def get_app_dir(self):
        """
        Return the app directory
        """
        return os.path.dirname(os.path.abspath(__file__))

    def boot(self):
        """
        Boot the application
        """
        # Change working directory
        self.__change_workdir()

        # Load the configuration
        self.config = self.__load_config(self.config_path)

        # Inject configuration in all modules
        self.__inject()

    def __inject(self):
        """
        Inject CONFIG in all other modules
        """
        measure.CONFIG = self.config

    def __load_config(self, config_path):
        """
        Read configuration and return it
        """
        with open(config_path) as config_file:
            data = json.load(config_file)
        return data

    def __change_workdir(self):
        """
        Call to make to change the workdir to the app directory
        """
        path = self.get_app_dir()
        os.chdir(path)
        return path
