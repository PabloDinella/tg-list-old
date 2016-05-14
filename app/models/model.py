db.define_table('category',
                Field('name', 'string'),
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
                format=lambda r: r.name or 'anonymous')
