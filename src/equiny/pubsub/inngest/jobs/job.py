from contextlib import contextmanager

from equiny.database.sqlalchemy import Sqlalchemy


class Job:
    @contextmanager
    @staticmethod
    def sqlalchemy_session():
        sqlalchemy = Sqlalchemy.get_session()
        try:
            yield sqlalchemy
        except Exception:
            sqlalchemy.rollback()
            raise
        else:
            sqlalchemy.commit()
        finally:
            sqlalchemy.close()
