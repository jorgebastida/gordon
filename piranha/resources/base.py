class BaseResource(object):

    REQUIRED_SETTINGS = ()

    def __init__(self, name, app, settings):
        self.name = name
        self.app = app
        self.settings = settings
        for key in self.REQUIRED_SETTINGS:
            if key not in self.settings:
                raise Exception("Required setting {}".format(key))

    @classmethod
    def register_type_pre_project_template(cls, project, template):
        pass

    @classmethod
    def register_type_project_template(cls, project, template):
        pass

    @classmethod
    def register_type_pre_resources_template(cls, project, template):
        pass

    @classmethod
    def register_type_resources_template(cls, project, template):
        pass

    @classmethod
    def register_type_post_resources_template(cls, project, template):
        pass

    def register_pre_project_template(self, template):
        pass

    def register_project_template(self, template):
        pass

    def register_pre_resources_template(self, template):
        pass

    def register_resources_template(self, template):
        pass

    def register_post_resources_template(self, template):
        pass
