#!/usr/bin/env python3
import argparse
import sys
import os
import yaml
import fileinput

def mkdir_by_path(parent_tree, path_part):
    parent_tree_copy = list(parent_tree)

    parent_tree_copy.append(str(path_part))

    try:
        os.mkdir(os.path.join(".","/".join(parent_tree_copy)))
    except OSError as exc:
        pass

def create_recursive_directories(directory_description, parent_tree):
    if isinstance(directory_description, dict):
        for path_part in directory_description:
            inside_directory = directory_description[path_part]

            if isinstance(inside_directory, list):

                for sub_path_part in inside_directory:
                    mkdir_by_path(parent_tree, path_part)

                    new_sub_path = list(parent_tree)

                    new_sub_path.append(path_part)

                    create_recursive_directories(sub_path_part, new_sub_path)
            else:
                mkdir_by_path(parent_tree, path_part)
    else:
        mkdir_by_path(parent_tree, directory_description)

def dir_to_dict(path):
    ''' Reads a dir into an YAML file
    '''
    directory = {}

    for dirname, dirnames, filenames in os.walk(path):
        dirbasename = os.path.basename(dirname)
        directory[dirbasename] = []

        if dirnames:
            for drctory in dirnames:
                directory[dirbasename].append(dir_to_dict(path=os.path.join(path,
                                                                            drctory)))
        directotory = { k: None if not v else v for k, v in directory.items() }
        return directory

class RecordTemplateStore(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError('nargs not allowed')
        super(RecordTemplateStore, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if not os.path.exists(values):
            print(values)
            print('The path provided does not exist')
            sys.exit()
        with open('{}.yaml'.format(os.path.basename(values)), 'w') as file:
            yaml.safe_dump(dir_to_dict(path=values), file,
                           default_flow_style=False,
                           explicit_start=True)

        with fileinput.FileInput(os.path.basename(values + '.yaml'), inplace=True) as file:
            for line in file:
                print(line.replace('[]', ''))
        print('Dictionary written to {}.yaml in the current directory\
              '.format(os.path.basename(values)))

MY_PARSER = argparse.ArgumentParser()
MY_PARSER.add_argument('-r',
                       '--record_template',
                       metavar='path',
                       action=RecordTemplateStore,
                       type=str,
                       help='Record a template YAML file from a directory')
MY_PARSER.add_argument('-s',
                       '--set_template',
                       metavar='path',
                       action='store',
                       dest='template_path',
                       type=str,
                       help='Set template file to be used for scaffoldig')
MY_PARSER.add_argument('-p',
                       '--project_folder',
                       metavar='path',
                       action='store',
                       dest='project_path',
                       type=str,
                       help='Set project folder')

if __name__ == '__main__':
    ARGS = MY_PARSER.parse_args()

    # Sometimes, the user just wants to record the scaffold of a project
    if ARGS.record_template is not None:
        sys.exit()
    # Create scaffold for a project
    else:
        if ARGS.project_path is None:
            print('You must provide a project path to indicate where the' +
                  ' scaffold should be created')
        else:
            if not os.path.exists(ARGS.project_path):
                os.makedirs(ARGS.project_path)

            if ARGS.template_path is None:
                yaml_template = {'data': None, 'documentation': None,
                                 'reports': None, 'scripts': ['outputs']}
                print('Using default template...')
                os.chdir(ARGS.project_path)
                create_recursive_directories(yaml_template, [])

            else:
                template_path = ARGS.template_path
                with open(os.path.abspath(template_path), 'r') as config_file_stream:
                    try:
                        config_file_dictionary = yaml.load(config_file_stream,
                                                           Loader=yaml.FullLoader)

                        os.chdir(ARGS.project_path)
                        create_recursive_directories(config_file_dictionary, [])


                    except yaml.YAMLError as exc:
                        print(exc)
