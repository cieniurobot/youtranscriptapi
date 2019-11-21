import os
import sys
import tarfile
import shutil
import logging
from fabric.tasks import task

'''

    Logging

'''

logger = logging.getLogger("youtranscript-api-fabric")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

'''

    VARS

'''
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
logger.debug('BASE_PATH: {}'.format(BASE_PATH))

REMOTE_PATH = '/home/crm/youtranscript_api'
logger.debug('REMOTE_PATH: {}'.format(REMOTE_PATH))

BUILD_PATH = os.path.join(BASE_PATH, 'build')
logger.debug('BUILD_PATH: {}'.format(BUILD_PATH))

BUILD_DIST_FILE = 'dist.tar.gz'
logger.debug('BUILD_DIST_FILE: {}'.format(BUILD_DIST_FILE))

BUILD_DIST_PATH = os.path.join(BUILD_PATH, BUILD_DIST_FILE)
logger.debug('BUILD_DIST_PATH: {}'.format(BUILD_DIST_PATH))

SOURCE_FOLDER = 'src'
SOURCE_PATH = os.path.join(BASE_PATH, SOURCE_FOLDER)
logger.debug('SOURCE_PATH: {}'.format(SOURCE_PATH))

REMOTE_PYTHON_PATH = "/usr/bin/python3"
logger.debug('REMOTE_PYTHON_PATH: {}'.format(REMOTE_PYTHON_PATH))

DOCKER_COMPOSE_FILE = "docker-compose.yml"


@task
def exists(conn, path):
    logger.info("run: exists")
    result = conn.run("ls {}".format(path), warn=True)
    return not result.failed


@task
def compress_build(conn):
    logger.info("run: compress_build")
    with tarfile.open(BUILD_DIST_PATH, "w:gz") as tar:
        for file in os.listdir(BUILD_PATH):
            file_path = os.path.join(BUILD_PATH, file)
            tar.add(file_path, arcname=os.path.basename(file_path))
    logger.info("finished: compress_build")


@task
def build(conn):
    """

    Build app

    :param conn:
    :return:
    """
    if os.path.isdir(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)

    os.mkdir(BUILD_PATH)
    shutil.copytree(SOURCE_PATH, os.path.join(BUILD_PATH, SOURCE_FOLDER))
    shutil.copy(os.path.join(BASE_PATH, 'Pipfile'), os.path.join(BUILD_PATH, 'Pipfile'))
    shutil.copy(os.path.join(BASE_PATH, 'wsgi.py'), os.path.join(BUILD_PATH, 'wsgi.py'))
    shutil.copy(os.path.join(BASE_PATH, 'Pipfile.lock'), os.path.join(BUILD_PATH, 'Pipfile.lock'))
    shutil.copy(os.path.join(BASE_PATH, DOCKER_COMPOSE_FILE), os.path.join(BUILD_PATH, DOCKER_COMPOSE_FILE))
    shutil.copytree(os.path.join(BASE_PATH, "config"), os.path.join(BUILD_PATH, "config"))
    shutil.copy(os.path.join(BASE_PATH, "Dockerfile"), os.path.join(BUILD_PATH, "Dockerfile"))
    compress_build(conn)


@task
def extract_build(conn):
    logger.info("run: extract_build")
    conn.run("tar xvzf {} -C {}".format(os.path.join(REMOTE_PATH, BUILD_DIST_FILE), REMOTE_PATH))
    if exists(conn, os.path.join(REMOTE_PATH, BUILD_DIST_FILE)):
        conn.run("rm {}".format(os.path.join(REMOTE_PATH, BUILD_DIST_FILE)))


@task
def install(conn):
    """

    Install app with dependencies into remote host

    :param conn:
    :return:
    """
    logger.info("run: install")
    result = conn.run("pipenv install")
    logger.info("result.stdout: {}".format(result.stdout.strip()))


@task
def hostname(conn):
    logger.info("run: hostname")
    response = conn.run("hostname")
    logger.info("response of \"hostname\": {}".format(response))
    return response


@task
def remote_mkdir(conn):
    logger.info("run: remote_mkdir")
    try:
        result = conn.run("mkdir -p {}".format(REMOTE_PATH))
        logger.info("result of \"mkdir\": {}".format(result.stdout.strip()))
        return result
    except Exception as e:
        logger.info(e)
        return False


@task
def remote_cleanup(conn):
    logger.info("run: remote_cleanup")
    try:
        result = conn.run("rm -rf {}/*".format(REMOTE_PATH))
        logger.info("result of \"rm\": {}".format(result.stdout.strip()))
        return result
    except Exception as e:
        logger.info(e)
        return False


@task
def upload(conn):
    logger.info("run: upload")
    conn.put(BUILD_DIST_PATH, os.path.join(REMOTE_PATH, BUILD_DIST_FILE))
    conn.put(os.path.join(BASE_PATH, DOCKER_COMPOSE_FILE), os.path.join(REMOTE_PATH, DOCKER_COMPOSE_FILE))


@task
def compose(conn):
    logger.info("run: compose")
    result = conn.run("docker-compose -f {} up -d --build".format(os.path.join(REMOTE_PATH, DOCKER_COMPOSE_FILE)))
    logger.info("result of \"docker-compose up\": {}".format(result.stdout.strip()))
    return result


@task
def deploy(conn):
    """

    Deploy scripts into server by ssh

    :param conn:
    :return:
    """
    build(conn)
    remote_mkdir(conn)
    remote_cleanup(conn)
    upload(conn)
    extract_build(conn)
    compose(conn)
    logger.info('finished: deploy')
