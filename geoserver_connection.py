from config import get_config
from geoserver.catalog import Catalog

geoserver = Catalog(
    get_config('geoserver.restUrl'),
    get_config('geoserver.user'),
    get_config('geoserver.password'),
)


# create workspace if not exists, a workspace is mandatory to work with geoserver
workspace_name = get_config('geoserver.workspace')
workspace = geoserver.get_workspace(workspace_name)
if workspace is None:
    geoserver.create_workspace(
        workspace_name,
        get_config('geoserver.hostUrl') + workspace_name
    )
    geoserver.reload()


geoserver_connection = geoserver
workspace_obj = workspace