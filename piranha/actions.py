import json

class Ref(object):

    def __init__(self, name):
        self.name = name

    def serialize(self):
        return {'Ref': self.name}


class BaseAction(object):

    properties = ()

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if key in self.properties:
                setattr(self, key, value)

    def serialize(self):
        data = dict([[k, getattr(self, k, None)] for k in self.properties])
        data['_type'] = self.__class__.__name__
        return self._serialize(data)

    def _serialize(self, obj):
        if hasattr(obj, 'serialize'):
            return obj.serialize()
        elif isinstance(obj, dict):
            return dict((k, self._serialize(v)) for k, v in obj.iteritems())
        elif hasattr(obj, '__iter__'):
            return [self._serialize(v) for v in obj]
        return obj

    def to_json(self, *args, **kwargs):
        return json.dumps(self.serialize(), *args, **kwargs)


class Collection(BaseAction):

    properties = ('actions', 'parameters', 'parallelizable')

    def __init__(self, parallelizable=True):
        self.actions = []
        self.parameters = {}
        self.parallelizable = parallelizable

    def add(self, action):
        self.actions.append(action)

    def add_parameter(self, name, default=None, description="", type="string"):
        self.parameters[name] = {
            "default": default,
            "description": description,
            "type": type,
        }


class UploadToS3(BaseAction):

    properties = ('bucket', 'key', 'filename')
