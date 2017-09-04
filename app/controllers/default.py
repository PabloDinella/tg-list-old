# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

import datetime
import time
import re
import os
import urllib2

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value

def download_and_save_image(url, name):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    r = urllib2.Request(url, headers=headers)
    image = urllib2.urlopen(r).read()

    path = os.path.join(request.folder, 'uploads', name + '.jpg')
    output = open(path,'wb')
    output.write(image)
    output.close()
    return path

def updateentries():
    from bs4 import BeautifulSoup

    chats = db(db.chat.id).select()

    # for chat in chats:
    #     if not re.match(r'^https?://', chat.url):
    #         chat.update_record(url='https://' + chat.url)

    # image = urllib2.urlopen('https://cdn1.telesco.pe/file/M5ErrvYy53JcB2zpw2ctlspoBqEvA2d_kCli5lQCQl3D1mUF26b-NkjpdiXLN1lim7vU0uElI91ir-rtI1F8X0OVhgqszHNm4YKp7y3EvNMiIsbiwOaaBeBagF3j7cEZgL23Yr06TzZf4wyhc8PvJ5FY1X3stLUZBuQOJGv1xRvyQwtOj9GTD7VsTl0UNDgjUsbQu0yiSVw9sZv4qptSO0dLl5nTCl2cNKt13yXS1IIM6BFvgEeXnc69ziX4R7zep4P3uPyUfNKlUaRbpsSeMDMJLXgLM2GbWRLU_M2aKtwcp2iyS2-5tJyfBztwvCKm0azPoGgPTj2shGRmXfOvqQ').read()
    # updating = db(db.chat).select().first().update_record(image=image)
    # updating = db(db.chat).select().first().update_record(image=db.chat.image.store(image, 'image'))
    # print updating


    for chat in chats:
        try:
            data = urllib2.urlopen(chat.url).read()
            soup = BeautifulSoup(data)
            name = soup.find(class_="tgme_page_title").get_text()
            members = int(soup.find(class_="tgme_page_extra").get_text().split(' ')[0])
            image_url = soup.find(class_="tgme_page_photo_image")['src']
            image_path = download_and_save_image(image_url, slugify(name))

            image_read = open(image_path, 'rb')
            updating = chat.update_record(
                name=name,
                members=members,
                image=db.chat.image.store(image_read, slugify(name) + '.jpg'),
                description=chat.description.replace(chat.url, '')
            )
            print updating
            print name
            print members
            print '\n'

        except Exception as e:
            print chat.description, e

    return dict(oi='hehe')

def run():
    import os
    import json

    jayzon = open(os.path.join(request.folder, 'uploads', 'entries.json'))
    data = json.load(jayzon)

        # for chat in data['canal']:
        #     for tag in chat['tags']:
        #         if db(db.chat.url == chat['link']).select().first():
        #             break
        #         cat_parsed = re.sub(r'([a-z])([A-Z])', r'\1 \2', tag)
        #         cat = db(db.category.name == cat_parsed).select(db.category.id).first()
        #         cat = cat.id if cat else db(db.category.slug == 'sem-categoria').select(db.category.id).first().id
        #         db.chat.validate_and_insert(
        #             name=chat['link'].split('/')[-1],
        #             sent_by=db(db.auth_user).select().first().id,
        #             url=chat['link'],
        #             description=chat['desc'],
        #             category=cat,
        #             kind=2
        #         )


    return dict(grupos=data['grupo'])

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    category = db(db.category.slug == request.args(0)).select().first()
    search = db.chat.name.like('%'+request.vars.search+'%') if request.vars.search else ''

    if category:
        query = db.chat.category == category
    else:
        query = db.chat

    if search:
        query = search

    chats = db(query).select()

    return locals()

def load():
    import json
    from pprint import pprint
    import re
    import os
    filepath = os.path.join(request.folder,'uploads','chats.json')

    with open(filepath) as data_file:
        data = json.load(data_file)

    chats = []

    for chat in data:
        print "- - - - >", re.search('http[^\s]*', chat).group()

    # pprint(data)
    return locals()


@auth.requires_login()
def edit():
    """
    """
    record = db(db.chat.id == request.args(0)).select().first()
    form = SQLFORM(db.chat,
                   record,
                   _class='ui form',
                   submit_button='Enviar')

    if request.post_vars:
        request.post_vars.updated_at = request.now
        request.post_vars.sent_by = auth.user.id if not record else record.sent_by

    if form.accepts(request.post_vars):
        db.history.insert(who=auth.user.id, chat=form.vars.id)
        category_slug = db.category(request.post_vars.category).slug
        return redirect(URL('default', 'index', args=category_slug or ''))
    elif form.errors:
        response.flash = "Ops, houve algum problema..."

    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    user = auth.login_bare(request.post_vars.email,request.post_vars.password)
    if request.post_vars and not user:
        response.flash = "Login inválido"

    if user and not request.vars._next:
        return redirect(URL('default', 'index'))

    return dict(form=auth())


def lost_pass():
    # auth.messages.reset_password ='Recuperar senha: reset_password'+ '/?key='+'%(key)s'
    auth.messages.reset_password ='Recuperar senha: ' + URL('default', 'reset_pass', vars={'key':''}, host=True) + '%(key)s'
    form = auth.retrieve_password()

    return locals()


def reset_pass():
    form = auth.reset_password()

    return locals()


def signup():
    # def onvalidation():
        # print "entrou aqui"
    # auth.settings.register_onvalidation.append(onvalidation)
    db.auth_user.last_name.requires = None
    form = auth.register()

    return locals()


def profile():
    db.auth_user.last_name.requires = None
    form = auth.profile()

    return locals()


def change_password():
    db.auth_user.last_name.requires = None
    if request.post_vars:
        if len(request.post_vars.new_password) < 6:
            session.pass_too_short = "Senha muito curta"
            redirect(URL())
    form = auth.change_password()

    return locals()


@request.restful()
def api():
    response.view = 'generic.'+request.extension
    def GET(*args,**vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    # def POST(table_name,**vars):
    #     return db[table_name].validate_and_insert(**vars)
    # def PUT(table_name,record_id,**vars):
    #     return db(db[table_name]._id==record_id).update(**vars)
    # def DELETE(table_name,record_id):
    #     return db(db[table_name]._id==record_id).delete()
    # return dict(GET=GET, POST=POST, PUT=PUT, DELETE=DELETE)
    return dict(GET=GET)


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
