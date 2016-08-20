auth.settings.extra_fields['auth_user']= [
    Field('telegram_user', 'string'),
]

auth.define_tables(username=False, signature=False)

db.define_table('category',
                Field('name', 'string'),
                Field('slug', 'string'),
                Field('parent', 'reference category'),
                format=lambda r: r.name or 'anonymous')


db.define_table('chat',
                Field('name', 'string'),
                Field('username', 'string'),
                Field('members', 'integer'),
                Field('url', 'string'),
                Field('category', db.category),
                Field('description', 'text'),
                Field('image', 'upload'),
                Field('updated_at', 'datetime', default=request.now),
                format=lambda r: r.name or 'anonymous')

db.chat.category.requires = IS_IN_DB(
    db, 'category.id', '%(name)s', zero=T('Escolha uma categoria')
)
db.chat.updated_at.requires = IS_DATETIME()
db.chat.url.requires = IS_NOT_EMPTY()
db.chat.description.requires = IS_NOT_EMPTY()

categories = db(db.category).select(orderby=db.category.name)
