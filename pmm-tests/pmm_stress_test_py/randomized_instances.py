from subprocess import check_output, Popen, PIPE
from shlex import split
from uuid import uuid4
from random import randint
import threading, click, os, math

###############################################################################
# Main logic goes here, below
def pmm_framework_add_client(i_name, i_count):
    """
    Will call pmm-framework.sh script with given instance name and count.
    """
    # Not a multi-threaded run
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    command = "{}/pmm-framework.sh --addclient={},{}"
    new_command = command.format(dname[:-18], i_name, i_count)
    try:
        process = Popen(
                    split(new_command),
                    stdin=None,
                    stdout=None,
                    stderr=None)
        output, error = process.communicate()
    except Exception as e:
        print(e)
    else:
        return 0

def pmm_framework_wipe_client():
    """
    For wiping added instances from pmm + to shutdown previosly started instances(pysically)
    """
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    command = "{}/pmm-framework.sh --wipe-clients"
    new_command = command.format(dname[:-18])
    try:
        process = Popen(
                        split(new_command),
                        stdin=None,
                        stdout=None,
                        stderr=None)
        output, error = process.communicate()
    except Exception as e:
        print(e)
    else:
        return 0


def getting_instance_socket():
    # For obtaining socket file path for each added instances
    # Return: the list of sockets
    command = "sudo pmm-admin list | grep 'mysql:metrics' | sed 's|.*(||;s|)||'"
    prc = check_output(command, shell=True)
    return prc.split()


def adding_instances(sock, threads=0):
    """
    Will try to add instances with randomized name, based on already added instances
    """
    # Should Not be a multi-threaded run -> see comment at the end of function
    try:
        if threads == 0:
            command = "sudo pmm-admin add mysql --user=root --socket={} --service-port={} {} "
            new_command = command.format(sock, str(randint(10000, 60000)), str(uuid4()))
            print("Running -> " + new_command)
            process = Popen(
                            split(new_command),
                            stdin=None,
                            stdout=None,
                            stderr=None)
            process.communicate()
        elif threads > 0:
            command = "sudo pmm-admin add mysql --user=root --socket={} --service-port={} {} "
            new_command = command.format(sock, str(randint(10000, 60000)), str(uuid4()))
            print("Running -> " + new_command)
            process = Popen(
                            split(new_command),
                            stdin=None,
                            stdout=None,
                            stderr=None)
    except Exception as e:
        print(e)
    else:
        return 0
        # Untill pmm-admin is not thread-safe there is no need to run with true multi-thread;
        #process.communicate()

def repeat_adding_instances(sock, threads, count, i, pmm_count):
    for j in range(count):
        # For eg, with --pmm_instance_count 20 --threads 10
        # Here count = 2 from previous function
        # 0 + 1 + 10 * 2 >= 20
        # 1 + 1 + 10 * 2 >= 20
        if j + i * count >= pmm_count:
            break

        adding_instances(sock, threads)


def runner(pmm_count, i_name, i_count, threads=0):
    """
    Main runner function; using Threading;
    """
    pmm_framework_wipe_client()
    pmm_framework_add_client(i_name, i_count)
    sockets = getting_instance_socket()
    try:
        for sock in sockets:
            if threads > 0:
                # Enabling Threads
                # Workers count is equal to passed threads number, \
                # and we have to divide pmm_count to workers count to get loop range for every thread
                count = int(math.ceil(pmm_count/float(threads)))
                workers = [threading.Thread(target=repeat_adding_instances(sock, threads, count, i, pmm_count), name="thread_"+str(i))
                                    for i in range(threads)]
                [worker.start() for worker in workers]
                [worker.join() for worker in workers]

            elif threads == 0:
                for i in range(pmm_count):
                    adding_instances(sock, threads)

    except Exception as e:
        print(e)
    else:
        return 0


def create_db(db_count, i_type):
    """
    Function to create given amount of databases.
    Using create_database.sh script here.
    """
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    bash_command = '{}/create_database.sh {} {}'
    new_command = bash_command.format(dname[:-18], i_type, db_count)
    try:

        process = Popen(
                        split(new_command),
                        stdin=None,
                        stdout=None,
                        stderr=None)
        output, error = process.communicate()
    except Exception as e:
        print(e)
    else:
        return 0
    #process.communicate()

def create_table(table_count, i_type):
    """
    Function to create given amount of tables.
    Using create_table.sh script here.
    """
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    bash_command = '{}/create_table.sh {} {}'
    new_command = bash_command.format(dname[:-18], i_type, table_count)
    try:

        process = Popen(
                        split(new_command),
                        stdin=None,
                        stdout=None,
                        stderr=None)
        output, error = process.communicate()
    except Exception as e:
        print(e)
    else:
        return 0

def create_sleep_query(query_count, i_type):
    """
    Function to create given amount of sleep() queries.
    Using create_sleep_queries.sh script here
    """
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    bash_command = '{}/create_sleep_queries.sh {} {}'
    new_command = bash_command.format(dname[:-18], i_type, query_count)
    try:
        process = Popen(
                        split(new_command),
                        stdin=None,
                        stdout=None,
                        stderr=None)
    except Exception as e:
        print(e)
    else:
        return 0
    #output, error = process.communicate()

def create_unique_query(query_count, i_type):
    """
    Function to create and run given number unique queries against instances.
    Using create_unique_queries.sh script here
    """
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    bash_command = '{}/create_unique_queries.sh {} {}'
    new_command = bash_command.format(dname[:-18], i_type, query_count)
    try:
        process = Popen(
                        split(new_command),
                        stdin=None,
                        stdout=None,
                        stderr=None)
    except Exception as e:
        print(e)
    else:
        return 0

def insert_blob(insert_count, i_type):
    """
    Function to create demo image file and run insert statements up to the given number.
    Using create_blob_img.sh script here.
    """
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    bash_command = '{}/create_blob_img.sh {} {}'
    new_command = bash_command.format(dname[:-18], i_type, insert_count)
    try:
        process = Popen(
                        split(new_command),
                        stdin=None,
                        stdout=None,
                        stderr=None)
    except Exception as e:
        print(e)
    else:
        return 0

##############################################################################
# Command line things are here, this is separate from main logic of script.
def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("PMM Stress Test Suite Version 1.0")
    ctx.exit()

@click.command()
@click.option(
    '--version',
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Version information.")
@click.option(
    "--threads",
    type=int,
    nargs=1,
    default=0,
    help="Give non-zero number to enable multi-thread run!")
@click.option(
    "--instance_type",
    type=str,
    nargs=1,
    required=True,
    help="Passing instance type(ps, ms, md, pxc, mo) to pmm-framework.sh")
@click.option(
    "--instance_count",
    type=int,
    nargs=1,
    default=2,
    required=True,
    help="How many physical instances you want to start? (Passing to pmm-framework.sh)")
@click.option(
    "--pmm_instance_count",
    type=int,
    nargs=1,
    #default=2,
    required=True,
    help="How many pmm instances you want to add with randomized names from each physical instance? (Passing to pmm-admin)")
@click.option(
    "--create_databases",
    type=int,
    nargs=1,
    default=0,
    help="How many databases to create per added instance for stress test?")
@click.option(
    "--create_tables",
    type=int,
    nargs=1,
    default=0,
    help="How many tables to create per added instance for stress test?")
@click.option(
    "--create_sleep_queries",
    type=int,
    nargs=1,
    default=0,
    help="How many connections to open with 'select sleep()' per added instance for stress test?")
@click.option(
    "--create_unique_queries",
    type=int,
    nargs=1,
    default=0,
    help="How many unique queries to create and run against added instances?"
)
@click.option(
    "--insert_blobs",
    type=int,
    nargs=1,
    default=0,
    help="How many times to insert test binary image into demo table?"
)


def run_all(threads, instance_type,
            instance_count, pmm_instance_count,
            create_databases, create_tables,
            create_sleep_queries, create_unique_queries,
            insert_blobs):
    if (not threads) and (not instance_type) and (not instance_count) and (not pmm_instance_count) and (not create_databases):
        print("ERROR: you must give an option, run with --help for available options")
    else:
        runner(pmm_instance_count, instance_type, instance_count, threads)
        if create_databases:
            create_db(create_databases, instance_type)
        if create_tables:
            create_table(create_tables, instance_type)
        if create_sleep_queries:
            create_sleep_query(create_sleep_queries, instance_type)
        if create_unique_queries:
            create_unique_query(create_unique_queries, instance_type)
        if insert_blobs:
            insert_blob(insert_blobs, instance_type)


if __name__ == "__main__":
    run_all()

###############################################################################
