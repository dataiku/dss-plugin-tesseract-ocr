import logging
import dataiku
from dataiku.customrecipe import *


def get_input_output_folder():
    input_names = get_input_names_for_role('input_folder')[0]
    output_names = get_output_names_for_role('output_folder')[0]
    input_folder = dataiku.Folder(input_names)
    output_folder = dataiku.Folder(output_names)
    return input_folder, output_folder

def get_input_output_dataset():
    input_names = get_input_names_for_role('input_folder')[0]
    output_names = get_output_names_for_role('output_dataset')[0]
    input_folder = dataiku.Folder(input_names)
    output_dataset = dataiku.Dataset(output_names)
    return input_folder, output_dataset


def get_input_output_type():
    input_names = get_input_names_for_role('input_folder')[0]
    output_names = get_output_names_for_role('output_type')[0]
    input_folder = dataiku.Folder(input_names)
    is_folder, output = output_type(output_names)
    return input_folder, is_folder, output


def output_type(output_names):
    """ check if output is a folder or a dataset """
    output_folder = dataiku.Folder(output_names)
    output_dataset = dataiku.Dataset(output_names)

    is_folder = False
    try:
        output_folder.get_info()
    except:
        try:
            output_dataset.get_location_info()
        except:
            raise NameError("output is neither a folder neither a dataset")
    else:
        is_folder = True

    output = output_folder if is_folder else output_dataset

    return is_folder, output


def text_extraction_parameters(recipe_config):
    def _p(param_name, default=None):
        return recipe_config.get(param_name, default)

    params = {}
    params['advanced'] = _p('advanced_parameters', default=False)
    params['deskew'] = _p('deskew', default=False)
    params['language'] = _p('language', default='eng')
    params['remove_special_characters'] = _p('remove_special_characters', default=False)

    return params
