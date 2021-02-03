from os import path, makedirs, listdir
import rasterio
from config import get_config
from zipfile import ZipFile
from initializations.geoserver_connection import geoserver_connection


def write_var(data, bounds, date, projection):
    output_dir = get_config('temp_dir')

    width = len(data[0])
    height = len(data)

    transform = rasterio.transform.from_bounds(
        bounds['west'], bounds['south'], bounds['east'], bounds['north'], width, height
    )

    try:
        makedirs(output_dir)
    except:
        pass

    with rasterio.open(
            path.join(output_dir, f'{path.basename(date)}.tif'),
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=rasterio.float64,
            crs=projection,
            transform=transform
    ) as dst:
        dst.write(data, 1)


def write_property_file(file_name, configs, base_dir):
    with open(path.join(base_dir, file_name), 'w') as file:
        for key, value in configs.items():
            file.write(f'{key}={value}\n')


def zip_directory(directory, zip_path):
    zip_obj = ZipFile(zip_path, 'w')
    files = [f for f in listdir(directory) if path.isfile(path.join(directory, f))]

    for file in files:
        zip_obj.write(path.join(directory, file), arcname=f'{path.basename(file)}')

    zip_obj.close()


def update_geoserver_layer(var_name, data, bounds, date, projection, domain):
    workspace_name = get_config('geoserver.workspace')
    output_dir = get_config('temp_dir')
    store_name = f'{var_name}_{domain}'
    zip_path = path.join(output_dir, 'zip/data.zip')
    makedirs(path.dirname(zip_path))

    store = geoserver_connection.get_store(store_name, workspace_name)

    write_var(data, bounds, date, projection)

    if store is None:
        # create imageMosaic store and wms layer as described here
        # https://docs.geoserver.org/latest/en/user/tutorials/imagemosaic_timeseries/imagemosaic_timeseries.html
        datastore_properties = get_config('geoserver.datastore')
        indexer_properties = get_config('geoserver.indexer')
        timeregex_properties = get_config('geoserver.timeregex')

        datastore_file_name = 'datastore.properties'
        indexer_file_name = 'indexer.properties'
        timeregex_file_name = 'timeregex.properties'

        write_property_file(datastore_file_name, datastore_properties, output_dir)
        write_property_file(indexer_file_name, indexer_properties, output_dir)
        write_property_file(timeregex_file_name, timeregex_properties, output_dir)

    zip_directory(output_dir, zip_path)

    if store is None:
        store = geoserver_connection.create_imagemosaic(store_name, zip_path, workspace=workspace_name)
        geoserver_connection.reload()
        # TODO:configure store
    else:
        geoserver_connection.add_granule(zip_path, store_name, workspace_name)
