#coding:utf-8


class SimpleConfig:
    def __init__(self):
        self. props ={}

    def clear(self):
        self. props ={}

    def load(self ,file):
        try:
            f = open(file ,'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                line = line.strip()
                if line[:1] =='#': continue
                try:
                    key, val = line.split('=')
                    key = key.strip()
                    val = val.strip()
                    if not self.props.has_key(key):
                        self.props[key] = []
                    self.props[key].append(val)
                except:
                    pass
        except:
            pass

    def getValue(self, key):
        if self.props.has_key(key):
            return self.props[key][0]
        return ''

    def getValueList(self, key):
        if self.props.has_key(key):
            return self.props[key]  #
        return []