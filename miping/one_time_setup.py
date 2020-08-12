# One time setup, to run miping properly
import sys
import getopt
import os
import requests
import zipfile
import io
import getpass

from subprocess import check_call
from shutil import copyfile
# from whichcraft import which
from shutil import which


def main(
    setup_webserver,
    domain
):
    """
    TODO main
    """
    webserver = False

    print("Setting up miping")
    if setup_webserver == 'True' or setup_webserver is True:
        print('Will setup webserver')
        if domain in ("miping", "localhost"):
            # domain is in preconfigured files
            print("Domain will be: " + str(domain))
            webserver = True
        else:
            # check if config file exists in miping for domain
            path = os.path.dirname(os.path.abspath(__file__))
            fullPath = path + 'webapp/webfiles/' + domain
            exists = os.path.isfile(fullPath)
            if exists is True:
                print("Domain will be: " + str(domain))
                webserver = True
            else:
                print("No config file for domain " + str(domain))
    else:
        print('Will not setup webserver')

    # current working dir
    path = os.getcwd()
    # create data, glove dirs
    makeDir(path, '/data')
    makeDir((path + '/data'), '/glove')
    # log files
    makeDir('/var/log', '/miping')

    # download glove
    downloadGloVe(path + '/data/glove/', 'glove.db')

    # setup webserver if specified
    if webserver is True:
        user = getpass.getuser()
        print("Setting up webserver")
        mipingDir = os.path.dirname(os.path.abspath(__file__))
        workingDir = os.getcwd()
        # make sure nginx is installed
        print("Making sure nginx webserver is installed")
        if is_tool('nginx') is True:
            print("nginx is already installed")
        else:
            print("Installing nginx via apt-get")
            check_call(
                ['apt-get', 'install', '-y', 'nginx']
            )

        # cp to data and modify root in config file
        print("Copy and modify nginx")
        # .txt is necessary so files get properly copied
        src = (
            mipingDir +
            '/webapp/webfiles/sites-available/' +
            domain +
            '.txt'
        )
        copyfile(
            src,
            workingDir + '/data/' + domain + ".txt"
        )
        modify_nginx_conf(
            confPath=(workingDir + '/data/' + domain + ".txt"),
            wwwRoot=(mipingDir + '/webapp/webfiles/www')
        )

        try:
            print("Copy nginx sites-available")
            src = os.path.realpath(workingDir + '/data/' + domain + ".txt")
            trg = (
                os.path.realpath(
                    '/etc/nginx/sites-available/' + domain + ".txt"
                )
            )
            if not os.path.exists('/etc/nginx/sites-available/' + domain):
                # only copy if file not already exists
                copyfile(src, trg)
                # remove .txt ending
                os.rename(
                    trg,
                    '/etc/nginx/sites-available/' + domain
                )
            else:
                print("Exists already")
        except Exception as e:
            print(e)
            print("Try to run script as root")

        try:
            print("Copy nginx sites-enabled")
            src = ('/etc/nginx/sites-available/' + domain)
            dst = ('/etc/nginx/sites-enabled/localhost')
            if not os.path.exists(dst):
                # only create symlink if not already exists
                os.symlink(src, dst)
            else:
                print("Exists already")
        except FileExistsError as e:
            print(e)

        # cp to data and modify supervisor config
        print("Copy and modify supervisor config")
        copyfile(
            mipingDir + '/webapp/webfiles/miping-gunicorn.conf',
            workingDir + '/data/miping-gunicorn.conf'
        )

        user = getpass.getuser()
        gunicornPath = which('gunicorn')
        if gunicornPath is None or gunicornPath == 'None':
            print(
                "Please make sure gunicorn is installed. " +
                "Try to NOT run as root."
            )
        else:
            modify_supervisor_conf(
                confPath=(workingDir + '/data/miping-gunicorn.conf'),
                currentDir=workingDir,
                user=user,
                gunicornPath=gunicornPath
            )

        # cp start_webserver and modify
        print("Copy and modify start_webserver.sh")
        if which('supervisord') is None or which('supervisord') == "None":
            print("Try to run not as root. supervisord not found.")
        else:
            copyfile(
                        mipingDir + '/webapp/webfiles/start_webserver.sh',
                        workingDir + '/data/start_webserver.sh'
            )
            modify_web_sh(
                confPath=(workingDir + '/data/start_webserver.sh'),
                pythonBinaryDir=which('supervisord')
            )

            # cp stop_webserver and modify
            print("Copy and modify stop_webserver.sh")
            copyfile(
                        mipingDir + '/webapp/webfiles/stop_webserver.sh',
                        workingDir + '/data/stop_webserver.sh'
            )
        # prepare files for ssl
        prepare_ssl(workingDir)


def prepare_ssl(
    workingDir
):
    """
    TODO prepare_ssl
    """
    # check and create ssl keys
    # check if certificate exists
    existsCert = os.path.isfile('/etc/ssl/certs/cert.pem')
    existsKey = os.path.isfile('/etc/ssl/private/key.pem')
    if existsCert is False or existsKey is False:
        CERT_FILE = workingDir + "cert.pem"
        KEY_FILE = workingDir + "key.pem"
        # check if local keys exist
        existsCert = os.path.isfile(workingDir + "cert.pem")
        existsKey = os.path.isfile(workingDir + "key.pem")
        if existsCert is False or existsKey is False:
            # one of both does not exist
            print("Creating SSL key and certificate")
            # create files in local directory
            # and move later
            create_self_signed_cert(
                CERT_FILE=CERT_FILE,
                KEY_FILE=KEY_FILE
            )

        # try to move, only possible if sufficient permissions
        destCert = "/etc/ssl/certs/cert.pem"
        destKey = "/etc/ssl/private/key.pem"
        try:
            print("Copying certificate to /etc/ssl/certs")
            copyfile(CERT_FILE, destCert)
        except Exception as e:
            print(e)
            print("Try with root")

        try:
            print("Copying key to /etc/ssl/private")
            copyfile(KEY_FILE, destKey)
        except Exception as e:
            print(e)
            print("Try with root")

    else:
        print("SSL key and certificate exist")


def create_self_signed_cert(
    CERT_FILE,
    KEY_FILE,
):
    """
    TODO create_self_signed_cert
    """
    from OpenSSL import crypto
    from socket import gethostname

    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "DE"
    cert.get_subject().ST = "Braunschweig"
    cert.get_subject().L = "Braunschweig"
    cert.get_subject().O = "Dummy Company Ltd"
    cert.get_subject().OU = "Dummy Company Ltd"
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')

    with open(CERT_FILE, "wt") as f:
        f.write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8")
        )
    with open(KEY_FILE, "wt") as f:
        f.write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8")
        )


def modify_web_sh(
    confPath,
    pythonBinaryDir,
):
    """
    TODO modify_web_sh
    """
    print("Modify webserver.sh")
    print("Supervisor binary " + str(pythonBinaryDir))
    # Read in the file
    with open(confPath, 'r') as file:
        filedata = file.read()

    # Replace the target string
    # user name
    filedata = filedata.replace(
        'supervisorctl',
        pythonBinaryDir
    )

    filedata = filedata.replace(
        'supervisord',
        pythonBinaryDir
    )

    # Write the file out again
    with open(confPath, 'w') as file:
        file.write(filedata)

    return


def modify_nginx_conf(
    confPath,
    wwwRoot,
):
    """
    TODO modify_supervisor_conf
    """
    print("Modify nginx config")
    # Read in the file
    with open(confPath, 'r') as file:
        filedata = file.read()

    # Replace the target string
    # user name
    filedata = filedata.replace(
        'root /miping/webapp/webfiles/www',
        'root ' + str(wwwRoot)
    )

    # Write the file out again
    with open(confPath, 'w') as file:
        file.write(filedata)

    return


def modify_supervisor_conf(
    confPath,
    currentDir,
    user,
    gunicornPath
):
    """
    TODO modify_supervisor_conf
    """
    print("Modify supervisor config")
    # Read in the file
    with open(confPath, 'r') as file:
        filedata = file.read()

    # Replace the target string
    # user name
    filedata = filedata.replace(
        'user=root',
        'user=' + str(user)
    )
    # directory
    filedata = filedata.replace(
        'directory=MiningPersonalityInGerman',
        'directory=' + str(currentDir)
    )
    # gunicorn binary
    filedata = filedata.replace(
        'command=/bin/gunicorn',
        'command=' + str(gunicornPath)
    )

    # Write the file out again
    with open(confPath, 'w') as file:
        file.write(filedata)

    return


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    return which(name) is not None


def downloadGloVe(
    path,
    filename,
    zip_file_url='https://miping.uber.space/downloads/glove.zip'
):
    """
    TODO downloadGloVe
    """
    # check if already exists
    exists = os.path.isfile(path + filename)
    if exists is True:
        print("GloVe database file already exists")
    else:
        # download glove file
        print("Downloading GloVe file, this takes a while")
        r = requests.get(zip_file_url, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        # unzip file
        z.extractall(path)


def makeDir(
    parent,
    directory,
):
    """
    makeDir
    """
    path = parent + directory
    # check if already exists
    exists = os.path.isdir(path)
    if exists is False:
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s " % path)


if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            argv,
            "hi:d:",
            ["setup_webserver=", "domain="]
        )
    except getopt.GetoptError:
        print(
            'one_time_setup.py --setup_webserver <Boolean> ' +
            '--domain localhost'
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                 'usage: sudo python3 miping/one_time_setup.py ' +
                 '--setup_webserver True ' +
                 '-d "localhost"'
            )
            sys.exit()
        elif opt in ("-i", "--setup_webserver"):
            setup_webserver = arg
        elif opt in ("-d", "--domain"):
            domain = arg
    main(
        setup_webserver=setup_webserver,
        domain=domain
    )
