from dotenv import load_dotenv
from uvicorn import run

load_dotenv()

from equiny.app import create_app  # noqa: E402

app = create_app()


def main() -> None:
    from equiny.constants import ENV

    run('main:app', host=ENV.HOST, port=ENV.PORT, reload=True)


if __name__ == '__main__':
    main()
