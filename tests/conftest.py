"""Special pytest fixture configuration file.

This file automatically provides all fixtures defined in it to all
pytest tests in this directory and sub directories.

See https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files

pytest fixtures are used to initialize object for test functions. The
fixtures run for a function are based on the name of the argument to
the test function.

Scope = 'session' means that the fixture will be run onec and reused
for the whole test run session. The default scope is 'function' which
means that the fixture will be re-run for each test function.

"""
import pytest
import importlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from pathlib import Path

DB_FILE = "./pytest.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

CONNECT_ARGS = {"check_same_thread": False} if 'sqlite' in SQLALCHEMY_DATABASE_URL  \
    else {}

SQL_DATA_FILE = './tests/data.sql'

DELETE_DB_FILE_ON_EXIT = True


def escape_bind(stmt):
    return stmt.replace(':0', '\:0')


@pytest.fixture(scope='session')
def engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=CONNECT_ARGS)
    return engine


@pytest.fixture(scope='session')
def create_and_load_db_tables(engine):
    print("Making tables...")
    try:
        from arxiv_db.tables import arxiv_tables
        arxiv_tables.metadata.create_all(bind=engine)
        print("Done making tables.")
        test_load_db_file(engine, SQL_DATA_FILE)
        yield engine
    finally: # cleanup
        if DELETE_DB_FILE_ON_EXIT:
            Path(DB_FILE).unlink(missing_ok=True)
            print(f"Deleted {DB_FILE}. Set DELETE_DB_FILE_ON_EXIT to control.")


def test_load_db_file(engine, test_data: str):
    with engine.connect() as db:
        cmd_count = 0
        badcmd = False
        print(f"Loading test data from file '{test_data}'...")
        with open(test_data) as sql:
            cmd = ""
            for ln, line in enumerate(map(escape_bind, sql)):
                try:
                    if line.startswith("--"):
                        continue
                    elif line and line.rstrip().endswith(";"):
                        cmd = cmd + line
                        if cmd:
                            #print(f"About to run '{cmd}'")
                            db.execute(text(cmd))
                            cmd_count = cmd_count + 1
                            cmd = ""
                        else:
                            #print("empty command")
                            cmd = ""
                    elif not line and cmd:
                        #print(f"About to run '{cmd}'")
                        db.execute(text(cmd))
                        cmd_count = cmd_count + 1
                        cmd = ""
                    elif not line:
                        continue
                    else:
                        cmd = cmd + line
                except Exception as err:
                    badcmd = f"At line {ln} Running command #{cmd_count}. {err}"
                    break

        if badcmd:
            # moved this out of the except to avoid pytest printing huge stack traces
            raise Exception(badcmd)
        else:
            print(f"Done loading test data. Ran {cmd_count} commands.")

