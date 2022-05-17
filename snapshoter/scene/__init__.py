import os
import shutil
import pathlib


def make_folders(keystr, cq_abbr, output_path):
    '''
    Make folders for the static in the given output_path

    The folders will look like:

    output_path/keystr/cq_abbr/
    output_path/keystr/cq_abbr/pub
    output_path/keystr/cq_abbr/pub/graphdata
    output_path/keystr/cq_abbr/pub/graphdata/keystr

    '''
    # first, the pub
    folders = [
        '',   # this means create sub-folder under `output_path`
        'pub',
        'pub/graphdata',
        'pub/graphdata/' + keystr,
        'static'
    ]

    for folder in folders:
        full_path = os.path.join(
            output_path, keystr, cq_abbr, folder
        )
        if os.path.exists(full_path):
            print('* existed folder %s' % full_path)

        else:
            os.makedirs(full_path, exist_ok=True)
            print('* created folder %s' % full_path)

    return 1

    
def make_page(client, url, full_fn, param=None):
    '''
    Make static page from url
    '''
    try:
        rv = client.get(url)
    except Exception as err:
        print('* ERROR', err)
        print('* error when getting %s' % url)
        return -1

    with open(full_fn, 'w') as f:
        f.write(rv.data.decode('utf8'))
    
    print('* made static page %s -> %s' % (
        url, full_fn
    ))

    return 1


def copy_static_files(keystr, cq_abbr, output_path, libs=None):
    '''
    Copy the static files
    '''
    # get the current path of this file
    cur_path = pathlib.Path(__file__).parent.absolute()

    # get the source static path
    static_path = os.path.join(
        cur_path, '..', '..', 'lnma', 'static'
    )

    # get the destination path
    _output_path = os.path.join(
        output_path, 'static'
    )

    # copy these two folders
    folders = ['css', 'img']

    # add some libs
    if libs is not None:
        folders = folders + libs

    for folder in folders:
        shutil.copytree(
            os.path.join(static_path, folder),
            os.path.join(_output_path, folder)
        )
        print('* copied static %s' % folder)

    return 1


def copy_graphdata_files(keystr, cq_abbr, output_path, paths):
    '''
    Copy the graphdata files
    '''
    # get the current path of this file
    cur_path = pathlib.Path(__file__).parent.absolute()

    # get the source graphdata path
    graphdata_path = os.path.join(
        cur_path, 
        '..', 
        '..', 
        'instance', 
        'pubdata', 
        keystr,
        cq_abbr
    )
    print('* got graphdata_path: %s' % graphdata_path)

    # get the destination path
    _output_path = os.path.join(
        output_path, 'pub', 'graphdata', keystr
    )
    print('* got _output_path: %s' % _output_path)

    for path in paths:
        src_path = os.path.join(graphdata_path, path)
        dst_path = os.path.join(_output_path, path)

        if not os.path.exists(src_path):
            print('* Skip NON-EXIST path %s' % src_path)
            continue

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)

        elif os.path.isfile(src_path):
            shutil.copyfile(src_path, dst_path)

        else:
            raise Exception('Error when copying %s' % src_path)

        print('* copied graphdata %s' % path)

    return 1