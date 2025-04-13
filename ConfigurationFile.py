#very simple module for easily managing simple key/value json files

import os
import json

class ConfigurationFile:
    def __init__(self, file='Config'):
        self.file = file

    def __getConfigPath(self):
        #builds the config file path
        path = os.path.join(os.getcwd(), 'Data', 'Configs')
        if not os.path.isdir(path):
            os.makedirs(path)
        
        path = os.path.join(path, f'{self.file}.json')
        return path
    
    def getFilePath(self):
        return self.__getConfigPath()

    def __getConfigJSONDictionary(self):
        #returns the config json file as a dictionary
        path = self.__getConfigPath()

        if os.path.exists(path):
            with open(path, 'r+') as f:
                config = json.load(f)
        else:
            config = {}

        return config

    def __saveConfigFile(self, config):
        #updates the config file
        path = self.__getConfigPath()

        with open(path, 'w') as f:
            json.dump(config, f, indent = 4)

    def __is_serializable(value):
        try:
            json.dumps(value)
            return True
        except(TypeError, OverflowError):
            return False
        
    def setValue(self, key, value):
        #saves a value to the config file
        config = self.__getConfigJSONDictionary()

        if not ConfigurationFile.__is_serializable(value):
            value = str(value)

        config[key] = value
        self.__saveConfigFile(config)

    def getValue(self, key, default=None):
        #returns a value from the config file
        config = self.__getConfigJSONDictionary()

        if key in config.keys():
            return config[key]
        else:
            return default