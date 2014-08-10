#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# classif_asso.py
#
# Copyright © 2014 Mathieu Gaborit (matael) <mathieu@matael.org>
#
#
# Distributed under WTFPL terms
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

"""

"""

import sys
import os

import json
import codecs

def read_json(in_file):

    with codecs.open(in_file, encoding="iso-8859-15") as f:
        data = json.load(f)

    return data


def create_tree(json_data, top_level_limit=3):

    root_children = {}
    top_level_count = 0

    sa1_list = []
    # loop over every line
    for record in json_data:
        # extract sa1 2 & 3
        r_sa1 = record['fields'].get('sa_secteur_d_activit_1')
        r_sa2 = record['fields'].get('sa_secteur_d_activit_2')
        r_sa3 = record['fields'].get('sa_secteur_d_activit_3')

        try:
            asso_name = record['fields']['pr_nom_statutaire']
        except KeyError:
            continue

        if r_sa1 not in sa1_list:
            if top_level_count < top_level_limit:
                root_children[r_sa1] = {'name': r_sa1, 'children': [], 'list_children': {}}
                sa1_list.append(r_sa1)
                top_level_count += 1

            else: continue

        if not r_sa2:

            root_children[r_sa1]['children'].append({'name': asso_name})

        else:

            if r_sa2 not in root_children[r_sa1]['list_children'].keys():
                root_children[r_sa1]['list_children'][r_sa2] = {'name': r_sa2, 'children': [], 'list_children': {}}

            if not r_sa3:

                root_children[r_sa1]['list_children'][r_sa2]['children'].append({'name': asso_name})

            else:

                if r_sa3 not in root_children[r_sa1]['list_children'][r_sa2]['list_children'].keys():
                    root_children[r_sa1]['list_children'][r_sa2]['list_children'][r_sa3] = {'name': r_sa3, 'children': []}


                root_children[r_sa1]['list_children'][r_sa2]['list_children'][r_sa3]['children'].append({'name': asso_name})

    return root_children


def reparse_all(tree):
    children = []
    for c in tree['children']:
        newc = {'name': c['name']}
        if c.get('children'): newc['children'] = reparse_all(c)
        if not c['name'] in [_['name'] for _ in children]:
            children.append(newc)
    return children


def unnest(nested_tree):

    for i in nested_tree['list_children'].values():
        if i.get('list_children'):
            i = unnest(i)
            nested_tree['children'].append(i)
            # i.pop('list_children', None)
        else:
            nested_tree['children'].append(i)

    return nested_tree

def output_json(nested_tree):

    valid_data = unnest({
        'name': 'root',
        'children': [],
        'list_children': nested_tree
    })

    valid_data = {
        'name': 'root',
        'children': reparse_all(valid_data)
    }

    with codecs.open('out.json', encoding='iso-8859-15', mode='w') as f:
        f.write(json.dumps(valid_data))

def main():

    json_data = read_json(sys.argv[1])
    nested_tree = create_tree(json_data, 78)
    output_json(nested_tree)

if __name__=='__main__': main()
