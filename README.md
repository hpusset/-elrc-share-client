Overview
--------

**elrc-share-client** is an interactive command-line tool for retrieving, creating and updating ELRC-SHARE resources.


## Installation
1. Install Python 3.6
2. `cd` to a preferred directory and create a virtual environment based on Python 3.6

    `cd /path/to/my/directory`
    
    `virtualenv --python=/path/to/python3.6/python3 elrc_env`
    
3. Activate the new virtual environment
    
    `source elrc_env/bin/activate` for Linux
    
    `elrc_env/Scripts/activate` for Windows
    
4. install the *elrc-share-client* package with pip

    `pip install git+https://github.com/MiltosD/ELRC-Client.git@dev`
    
5. Start the ELRC-SHARE shell

    `elrc-shell`
## User Authentication
Users that intend to use the elrc-share-client must have an active account on ELRC-SHARE repository.
#### Available Commands
- `login <username> <password>`
- `logout`
## Resource Retrieval
#### Available Commands
- `getj`
- `getx`
- `download`

### `getj`
Returns a json representation of a resource or a list of resources
(as seperate json strings). If no resources are
specified, the command will return all the resources that a logged in
user has access to, based on their
permissions, in a single json object. In addition to the metadata, the
result also contains information about
the publication status of the resource and it's download location (if
no dataset has been uploaded this location
will be an empty directory).

**Arguments**

A list of space seperated resource ids

**Options**

 `-p` or `--pretty`: Pretty prints the json output.

 `--my`: Returns only the resources that the user owns (useful
 for admins, ec members and erlc reviewers).

**User group permissions**

- *Administrators*: all resources
- *ELRC Reviewers*: all resources
- *EC members*: all published, ingested and own resources
- *Simple editors*: own resources
- *Contributors*: no resources

**Examples**

    # Get a json representation of the resource with id 100
    getj 100
    
    # Get a formatted json representation of the resource with id 100
    getj 100 --pretty
    
    # Get json representations of the resources with ids 10, 11, and 23
    getj 10 11 23
    
    Get a json representation of all the resources that the currently logged in user has access to
    getj

### `getx`
Returns an XML representation of a resource or a list of resources
(as seperate xml strings) that a logged in user has access to.

**Arguments**

A list of space seperated resource ids

**User group permissions**

- *Administrators*: all resources
- *ELRC Reviewers*: all resources
- *EC members*: all published, ingested and own resources
- *Simple editors*: own resources
- *Contributors*: no resources

Results returned by the `getj` and `getx` commands can be saved to a file using output redirection `>`. 
If no path is specified, the result will be saved in the default directory (`/home/<user>/ELRC-Downloads` 
for Linux and `C:\Users\<UserName>\Downloads\ELRC-Downloads` for Windows).

    getj 100 --pretty > resource-100.json
    getj 100 --pretty > /path/to/my/directory/resource-100.json
    
### `download`
Retrives the zipped dataset of a resource or a list of resources that a logged in user has access to. The .zip archive is saved as *archive-<resource-id>.zip*

**Options**

`-d` or `--dest`: The location where the zip archive is to be saved. If
no destination is specified, the archive will be saved in the default
directory.

**Examples**
    
    # download the datasets of the resources with ids 100 and 110
    download 100 110
    
    # download the datasets of the resources with ids  100 and 110 into the specified destination
    download 100 110 --dest /path/to/my_dir

## Resource Creation/Update
#### Available Commands
- `create`
- `update`
- `upload`

### `create`
Creates a new resource from an xml file, with optional dataset
(.zip archive) to upload. If no dataset is provided, the command will
try to upload any .zip archive that has the same name with the xml file,
within the same directory (e.g. resource1.xml, resource1.zip). For batch
creation, pass the full path to the directory containing the metadata xml files, along with any dataset.

**Arguments**

The full path to the metadata xml file or the containing directory (for
batch creation).

**Options**

`-z` or `--data`: The full path to the .zip archive to be uploaded along
with the new resource (not used for batch creation).

**Examples**

    # create resource metadata
    create /path/to/resource.xml
    
    # create resource metadata with dataset
    create /path/to/resource.xml --data /path/to/dataset.zip
    
    # create resources from directory
    create /path/to/resources/directory

### `update`
Updates a resource description from an xml file.

**Arguments**

An ELRC-SHARE resource id.

**Options**

`-f` or `--file`: The full path to the metadata xml file.

**Examples**
    
    # Update the resource with id 100 with the specified xml file
    update 100 --file /path/to/updated/xml_file.xml

### `upload`
Uploads a single dataset .zip archive for a given resource id.

**Arguments**

An ELRC-SHARE resource id.

**Options**

`-d` or `--data`: The full path to the .zip archive to be uploaded.

**Examples**
    
    # Upload the specified .zip archive to resource with id 100 (replaces existing dataset)
    upload 100 --data /path/to/zipped/archive.zip
