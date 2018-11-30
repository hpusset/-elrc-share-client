Overview
--------

**elrc-share-client** is an interactive command-line tool for retrieving and updating ELRC-SHARE resources.

## User Authentication
Users that intend to use the elrc-share-client must have an active account on ELRC-SHARE repository.
#### Available Commands
- `login <username> <password>`
- `logout`
## Resource Retrieval
#### Available Commands
- `getj`
- `gex`
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

e.g `getj 100` # Get a json representation of the resource with id 100.

e.g `getj 100 --pretty` # Get a formatted json representation of the
resource with id 100.

e.g `getj 10 11 23` # Get json representations of the resources with ids
10, 11, and 23.

e.g `getj` # Get a json representation of all the resources that the
currently logged in user has access to.

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

### `download`
Returns an XML representation of a resource or a list of resources
(as seperate xml strings) that a logged in user has access to.

**Options**

`-d` or `--dest`: The location where the zip archive is to be saved. If
no destination is specified, the archive will be saved in the default
directory.

e.g `download 100 110` # download the datasets of the resources with ids
100 and 110.

e.g `download 100 110 --dest /home/my_dir` # download the datasets of the resources with ids
100 and 110 into the specified destination.

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
batch creation)

**Options**

`-z` or `--data`: The full path to the .zip archive to be uploaded along
with the new resource (not used for batch creation).

### `update`

### `upload`