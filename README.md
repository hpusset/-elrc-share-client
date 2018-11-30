Overview
--------

**elrc-share-client** is an interactive command-line tool for retrieving and updating ELRC-SHARE resources.

## User Authentication
Users that intend to use the elrc-share-client must have an active account on ELRC-SHARE repository.
#### Available Commands
- `login <username> <password>`
- `logout`
## Metadata and Data Retrieval
#### Available Commands
- `getj`
- `gex`

### `getj`
Returns a json representation of a resource or a list of resources (as seperate json strings). If no resources are
specified, the command will return all the resources that a certain user has access to, based on their
permissions, in a single json object. In addition to the metadata, the result also contains information about
the publication status of the resource and it's download location (if no dataset has been uploaded this location
will be an empty directory).

**User group permissions**

- *Administrators*: all resources
- *ELRC Reviewers*: all resources
- *EC members*: all published, ingested and own resources
- *Simple editors*: own resources
- *Contributors*: no resources

e.g `getj 100` # Get a json representation of the resource with id 100.

e.g `getj 10 11 23` # Get json representations of the resources with id 10, 11, and 23.

e.g `getj` # Get a json representation of all the resources that the currently logged in user has access to.