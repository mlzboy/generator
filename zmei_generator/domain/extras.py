class Extra(object):

    def post_process(self):
        pass

    def get_required_apps(self):
        return []

    def get_required_deps(self):
        return []

    def get_required_settings(self):
        return {}

    def get_required_urls(self):
        return []

    @classmethod
    def write_settings(cls, apps, f):
        pass

    @classmethod
    def generate(cls, apps, target_path):
        pass


class ApplicationExtra(Extra):

    def __init__(self, application):
        super().__init__()

        self.application = application


class ModelExtra(Extra):

    def __init__(self, model) -> None:
        super().__init__()

        self.model = model


class PageExtra(Extra):

    def __init__(self, page) -> None:
        super().__init__()

        self.page = page


class Extendable(object):

    def register_extension(self):
        pass