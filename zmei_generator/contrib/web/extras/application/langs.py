from django.conf.locale import LANG_INFO

from zmei_generator.domain.application_def import ApplicationDef
from zmei_generator.domain.extras import ApplicationExtra
from zmei_generator.parser.gen.ZmeiLangParser import ZmeiLangParser
from zmei_generator.parser.utils import BaseListener


class LangsAppExtra(ApplicationExtra):

    def __init__(self, application):
        super().__init__(application)

        self.langs = None

    def get_name(cls):
        return 'langs'

    def get_required_deps(self):
        return ['django-modeltranslation==0.13-beta1']

    def get_required_apps(self):
        return ['modeltranslation']

    @classmethod
    def write_settings(cls, apps, f):
        _langs = {}
        for app in apps.values():
            if not app.langs:
                continue
            for code in app.langs.langs:
                name = LANG_INFO[code]['name_local'].capitalize()
                _langs[code] = name

        if len(_langs) == 0:
            _langs = {'en': 'English'}

        langs = tuple([(code, name) for code, name in _langs.items()])

        f.write('\n# LANGUAGE SETTINGS')
        f.write('\nLANGUAGES = {}'.format(repr(langs)))
        f.write('\nMAIN_LANGUAGE = {}\n'.format(repr(langs[0][0])))
        f.write('\nMIDDLEWARE += ["django.middleware.locale.LocaleMiddleware"]')
        f.write("\nLOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]")


class LangsAppExtraParserListener(BaseListener):

    def __init__(self, application: ApplicationDef) -> None:
        super().__init__(application)

        self.langs_extra = None

    def enterAn_langs(self, ctx: ZmeiLangParser.An_langsContext):
        self.langs_extra = LangsAppExtra(self.application)
        self.application.extras.append(self.langs_extra)
        self.application.langs = self.langs_extra

    def exitAn_langs(self, ctx: ZmeiLangParser.An_langsContext):
        self.langs_extra = None

    def enterAn_langs_list(self, ctx: ZmeiLangParser.An_langs_listContext):
        self.langs_extra.langs = [x.strip() for x in ctx.getText().split(',')]



