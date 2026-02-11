from sqlalchemy.orm import Session


class SqlalchemyRepository:
    sqlalchemy: Session

    def __init__(self, session: Session) -> None:
        self.sqlalchemy = session
