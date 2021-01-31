from netCDF4 import Dataset
from wrf import getvar, geo_bounds
from os import path, makedirs, listdir
from datetime import timedelta
import rasterio
from config import get_config
from zipfile import ZipFile


def read_vars(netcdf_file_path, var_name):
    output_dir = get_config('temp_dir')
    v = getvar(Dataset(netcdf_file_path), var_name)

    bounds = geo_bounds(v)
    bottom_left = bounds.bottom_left
    top_right = bounds.top_right

    east = top_right.lon
    west = bottom_left.lon
    north = top_right.lat
    south = bottom_left.lat

    width = v.shape[1]
    height = v.shape[0]

    transform = rasterio.transform.from_bounds(west, south, east, north, width, height)

    try:
        makedirs(output_dir)
    except:
        pass

    with rasterio.open(
            path.join(output_dir, f'{path.basename(netcdf_file_path)}.tif'),
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=v.dtype,
            crs=4326,
            transform=transform
    ) as dst:
        dst.write(v.values[::-1], 1)


def get_file_names(netcdf_base_path, start_date, end_date, domain, time_interval=timedelta(hours=3)):
    current_date = start_date
    files = []

    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y-%m-%d_%H:%M:%S')
        files.append(
            path.join(netcdf_base_path, f'wrfout_{domain}_{formatted_date}')
        )
        current_date = current_date + time_interval

    return files


def extract_tiff_from_var(start_date, end_date, var_name, domain):
    """
    Set on temp_dir the tiff representations of the variable for the range of time in specified domain
    :param start_date: Start date of reading files
    :param end_date: End date of reading files
    :param var_name: Name of a variable to extract its data inside a netcdf file
    :param domain: Name of a domain run, as specified on the netcdf files
    """
    netcdf_base_path = get_config('data_dir')

    file_names = get_file_names(
        path.join(path.join(netcdf_base_path, domain), domain),
        start_date, end_date, domain
    )

    for file in file_names:
        read_vars(file, var_name)
    return file_names


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


def update_geoserver_layer(start_date, end_date, var_name, domain, geoserver):
    workspace_name = get_config('geoserver.workspace')
    output_dir = get_config('temp_dir')
    store_name = f'{var_name}_{domain}'
    layer_name = f'{store_name}_WMS'
    zip_path = path.join(output_dir, 'zip/data.zip')
    makedirs(path.dirname(zip_path))

    store = geoserver.get_store(store_name, workspace_name)

    tiff_names = extract_tiff_from_var(start_date, end_date, var_name, domain)
    # tiff_names = ['/media/manuel/Data/insmet/temp/A20171130_calcite.tif']

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
        store = geoserver.create_imagemosaic(store_name, zip_path, workspace=workspace_name)
        geoserver.reload()
        layer = geoserver.create_wmslayer(workspace_name, store, layer_name)
    else:
        geoserver.add_granule(zip_path, store_name, workspace_name)
