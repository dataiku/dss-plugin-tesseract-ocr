import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role


def get_input_output(input_type='dataset', output_type='dataset'):
    if input_type == 'folder':
        input_names = get_input_names_for_role('input_folder')[0]
        input_obj = dataiku.Folder(input_names)
    else:
        input_names = get_input_names_for_role('input_dataset')[0]
        input_obj = dataiku.Dataset(input_names)

    if output_type == 'folder':
        output_names = get_output_names_for_role('output_folder')[0]
        output_obj = dataiku.Folder(output_names)
    else:
        output_names = get_output_names_for_role('output_dataset')[0]
        output_obj = dataiku.Dataset(output_names)

    return input_obj, output_obj


def text_extraction_parameters(recipe_config):
    def _p(param_name, default=None):
        return recipe_config.get(param_name, default)

    params = {}
    params['recombine_pdf'] = _p('recombine_pdf', default=False)
    params['advanced'] = _p('advanced_parameters', default=False)
    params['language'] = _p('language', default='eng')
    params['remove_special_characters'] = _p('remove_special_characters', default=False)

    return params