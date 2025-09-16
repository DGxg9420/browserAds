import os
import tomllib
import platform


class Constant:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            super().__setattr__(key, value)  # 初始化时允许赋值

    def __setattr__(self, name, value):
        raise AttributeError(f"Cannot modify constant: {name}")

    def search(self, name):
        for key, value in self.__dict__.items():
            if key.startswith(name):
                return value
        raise AttributeError(f"No attribute found with name starting with {name}")

BCP_47_LANGS_LIST = ['af-ZA', 'am-ET', 'ar-SA', 'az-AZ', 'be-BY', 'bg-BG', 'bn-IN', 'bs-BA', 'ca-ES', 'cs-CZ', 'cy-GB', 'da-DK', 'de-AT', 'de-CH', 'de-DE', 'el-GR', 'en-AU', 'en-CA', 'en-GB', 'en-IE', 'en-IN', 'en-NZ', 'en-US', 'en-ZA', 'es-AR', 'es-CL', 'es-CO', 'es-ES', 'es-MX', 'es-PE', 'et-EE', 'fa-IR', 'fi-FI', 'il-PH', 'fr-BE', 'fr-CA', 'fr-CH', 'fr-FR', 'ga-IE', 'gl-ES', 'gu-IN', 'he-IL', 'hi-IN', 'hr-HR', 'hu-HU', 'id-ID', 'is-IS', 'it-CH', 'it-IT', 'ja-JP', 'jv-ID', 'km-KH', 'kn-IN', 'ko-KR', 'lo-LA', 'lt-LT', 'lv-LV', 'ml-IN', 'mr-IN', 'ms-MY', 'nb-NO', 'ne-NP', 'nl-BE', 'nl-NL', 'no-NO', 'pa-IN', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU', 'si-LK', 'sk-SK', 'sl-SI', 'sq-AL', 'sr-RS', 'sv-FI', 'sv-SE', 'sw-KE', 'ta-IN', 'te-IN', 'th-TH', 'tr-TR', 'uk-UA', 'ur-PK', 'vi-VN', 'zh-CN', 'zh-HK', 'zh-SG', 'zh-TW', 'zu-ZA']

BCP_47_LANGS = Constant(**{lang.split('-')[1]: lang for lang in BCP_47_LANGS_LIST})

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = tomllib.load(open(os.path.join(BASE_DIR, 'config.toml'), 'rb'))

PLATFORM = platform.system()

if __name__ == '__main__':
    print(BCP_47_LANGS.search('CN'))
    print(BASE_DIR)
    print(CONFIG)