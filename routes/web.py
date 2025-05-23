import os
from hashlib import sha3_256
from renus.core.config import Config
from renus.core.request import Request
from renus.core.routing import Router
from renus.core.response import FileResponse, JsonResponse, TextResponse
from renus.core.status import Status
from app.extension.codenus.setting.model import Setting
from app.extension.codenus.translate.model import Translate

def index(request:Request):
    header = {
        'Cache-Control': 'max-age=0'
    }
    fldr="admin" if request.subdomain=="admin" else "index"
    r= FileResponse(f'public/{fldr}/index.html', headers=header)
    r.set_cookie('langs',",".join(Setting(request).langs()),max_age=60*60*24*30)
    return r



def public_index(name: str,request:Request):
    fldr = "admin" if request.subdomain == "admin" else "index"
    if os.path.isfile(f'public/{fldr}/{name}'):
        header = {
            'Cache-Control': 'max-age=2592000',  # 30*24*60*60
        }

        return FileResponse(f'public/{fldr}/{name}', headers=header)
    else:
        return index(request)

def default(request,package):
    site_default = Setting(request).hub.get('site_default', None)
    site_color = Setting(request).hub.get('site_color', None)
    if site_default is None:
        return JsonResponse({}, Status.HTTP_404_NOT_FOUND)
    if request.cookies:
        lang = request.cookies.get('lang', site_default['lang'])
    else:
        lang = site_default['lang']
    langs = Setting(request).hub.get('translates',{}).get('langs', {})
    rtl = site_default['rtl']

    meta_tag = Setting(request).hub.get('meta_tag', '')
    if Config('app').get('env', 'production') == 'local':
        meta_tag = ''

    colors = ''
    if site_color:
        colors += 'body {'
        for color, value in site_color.items():
            if color != 'id':
                colors += f'--color-{color}:{value};'
        colors += '}'
    translates = Translate(request)
    translates.hidden_fields = ['_id']
    translates = translates.where({
        lang: {'$exists': True},
        'packages': {'$in': ['renusify',package]}
    }).select('key', lang).get()
    fonts = site_default.get('fonts', {}).get(lang, False)
    s = ''
    if fonts:
        if len(fonts) == 1:
            f = fonts[0]
            typefont = 'woff2' if f.endswith('.woff2') else 'woff'
            s += f'<link f="siteDefault" href="{f}" as="font" type="font/{typefont}" crossorigin="anonymous">'
            s += '<style f="siteDefault">@font-face {font-family: fontOne;font-style: normal;font-display: swap;src: local(fontOne), ' + f'url({f}) format("{typefont}")' + '}*{font-family: fontOne, sans-serif}</style>'
        elif len(fonts) == 2:
            f = fonts[0]
            f2 = fonts[1]
            typefont = 'woff2' if f.endswith('.woff2') else 'woff'
            typefont2 = 'woff2' if f2.endswith('.woff2') else 'woff'
            s += f'<link f="siteDefault" href="{f}" as="font" type="font/{typefont}" crossorigin="anonymous">'
            s += f'<link f="siteDefault" href="{f2}" as="font" type="font/{typefont2}" crossorigin="anonymous">'
            s += '<style f="siteDefault">@font-face {font-family: fontOne;font-style: normal;font-display: swap;src: local(fontOne), ' + f'url({f}) format("{typefont}")' + '}*{font-family: fontOne, sans-serif } '
            s += '@font-face {font-family: fontTwo;font-style: normal;font-display: swap;src: local(fontTwo), ' + f'url({f2}) format("{typefont2}")' + '}.font-two{font-family: fontTwo, sans-serif}</style>'
    fonts = s
    r = {
        'fonts': fonts,
        'translates': translates,
        'colors': colors,
        'meta_tag': meta_tag,
        'lang': lang,
        'langs': langs,
        'rtl': rtl
    }

    r['hash']= sha3_256(str(r).encode()).hexdigest()
    return JsonResponse(r)
def opt(path, request):
    host = request.headers.get('host', '')
    allows = Config('app').get('cors_allow', [])
    if host in allows or '*' in allows:
        return TextResponse('', headers={
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        })
    else:
        for site in allows:
            if site.startswith('*') and host.endswith(site.replace('*', '')):
                return TextResponse('', headers={
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                })


    return TextResponse('', Status.HTTP_405_METHOD_NOT_ALLOWED)

r = Router()
r.option(r'{path:[\w\W]*}', func=opt)
r.get('/', func=index)
r.get('api/site-default/{package}', func=default)
r.get(r'/{name:[\s\S]*}', func=public_index)