from flask_rest.database import orm


class Proxy(orm.Model):
    __tablename__ = 'screens'
    id = orm.Column(
        orm.Integer,
        primary_key=True,
    )

    ip = orm.Column(orm.Text)
    port = orm.Column(orm.Text)
    login = orm.Column(orm.Text)
    password = orm.Column(orm.Text)

    quality = orm.Column(orm.SmallInteger)
    status = orm.Column(orm.SmallInteger)

    STATUS_VACANT = 0
    STATUS_RESERVED = 1

    fields = ('ip', 'port', 'login', 'password', 'quality', 'status')

    def as_dict(self):
        result = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        return result
