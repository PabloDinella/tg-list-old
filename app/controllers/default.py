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
        if not record:
            request.post_vars.sent_by = auth.user.id
        else:
            request.post_vars.sent_by = record.sent_by

    if form.accepts(request.post_vars):
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
