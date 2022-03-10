import yaml

class ReadYaml(object):
    def __init__(self):
        self.file_name = 'config.yml'
        self.encoding = 'utf-8'

    def read_conf(self):
        conf = open(file=self.file_name,mode='r',encoding=self.encoding)
        str_conf = conf.read()
        dict_conf = yaml.load(stream=str_conf,Loader=yaml.FullLoader)
        return dict_conf