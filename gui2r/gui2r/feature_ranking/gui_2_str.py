import ast
import copy
import uuid
from typing import Text, Generator, Tuple, List, Optional, Dict, Set
import pandas as pd
import numpy as np
from ast import literal_eval
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os
import json
import re


class GUI2Str():

    FEAT_METHOD_TEXT_ONLY = 'feat_method_text_only'
    FEAT_METHOD_TEXT_COMP_TYPE = 'feat_method_text_comp_type'
    FEAT_METHOD_TEXT_COMP_TYPE_RES_ID = 'feat_method_text_comp_type_res_id'
    FEAT_METHOD_HTML = 'feat_method_html'

    STRUCT_METHOD_SIMPLE_BULLETS = 'struct_method_simple_bullets'
    STRUCT_METHOD_SIMPLE_BULLETS_SORTED = 'struct_method_simple_bullets_sorted'
    STRUCT_METHOD_TWO_LEVEL_BULLETS = 'struct_method_two_level_bullets'
    STRUCT_METHOD_TWO_LEVEL_HTML = 'struct_method_two_level_html'

    STYLE_SIZE = 'style_size'
    STYLE_BACK_COLOR = 'style_back_color'
    STYLE_FONT_COLOR = 'style_font_color'
    STYLE_FONT_SIZE = 'style_font_size'

    stop_words_r_ids = {'main', 'content', 'navigation', 'bar', 'background', 'status',
                        'checkbox', 'widget', 'frame', 'container', 'action', 'btn', 'menu',
                        'label', 'root', 'toolbar', 'view', 'button', 'activity', 'layout',
                        'drawer', 'actionbar', 'icon', 'text', 'banner'}

    html_comp_mapping = {'Web View': ('<div', '</div>'),
                         'Icon': ('<i class="material-icons"', '</i>'),
                         'Button': ('<button type="button"', '</button>'),
                         'Label': ('<p', '</p>'),
                         'Video': ('<video ', '</video> '),
                         'Image': ('<img src="example.jpg"', ''),
                         'Background Image': ('<img src="example.jpg"', ''),
                         'Text': ('<p>', '</p>'),
                         'Checkbox': ('<input type="checkbox"', '</input>'),
                         'Switch': ('<input type="checkbox"', '</input>'),
                         'Text Input': ('<input type="text"', '</input>'),
                         'Input': ('<input type="text"', '</input>'),
                         'Advertisement': ('<div', '</div>'),
                         'Slider': ('<input type="range" min="1" max="100"', '</input>'),
                         'Radio Button': ('<input type="radio"', '</input>'),
                         'Pager Indicator': ('<div', '</div>'),
                         'Map View': ('<div', '</div>')}

    html_comp_group_mapping = {
        'List Item': ('<li', '</li>'),
        'Card': ('<div', '</div>'),
        'Modal': ('<div class="modal"', '</div>'),
        'Map View': ('<div class="map"', '</div>'),
        'Toolbar': ('<menu', '</menu>'),
        'Multi-Tab': ('<div class="tab"', '</div>'),
        'Layout': ('<div class="layout"', '</div>')
    }

    def __init__(self, path_data):
        self.all_guis_with_comps = pd.read_csv(path_data+"/all_guis.csv")
        self.all_guis_with_comps['data'] = self.all_guis_with_comps['data'].apply(literal_eval)

    @staticmethod
    def normalize_resource_id(resource_id: Text, filter_tokens: Optional[Set[Text]] = None,
                              tokenize: Optional[bool] = False) -> List[Text]:
        stopwords = filter_tokens if filter_tokens else GUI2Str.stop_words_r_ids
        name_split = resource_id.split('/')
        name = name_split[len(name_split) - 1]
        norm_name = [token for token in GUI2Str.snake_camel_case_split(name) if token.lower() not in stopwords]
        return norm_name if tokenize else ' '.join(norm_name)

    @staticmethod
    def camel_case_split(identifier: Text) -> List[Text]:
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]

    @staticmethod
    def snake_case_split(identifier: Text) -> List[Text]:
        return identifier.split('_')

    @staticmethod
    def snake_camel_case_split(identifier: Text) -> List[Text]:
        snake_cases = GUI2Str.snake_case_split(identifier)
        splits = [cc for sc in snake_cases
                  for cc in GUI2Str.camel_case_split(sc)]
        return splits

    @staticmethod
    def get_refined_comp_type(comp):
        if comp['componentLabel'] == 'On/Off Switch':
            return 'Switch'
        if comp['componentLabel'] == 'Input':
            clazz_name = comp['class'].lower()
            if 'edittext' in clazz_name:
                # return 'Edit Text'
                return 'Text Input'
            elif 'checkbox' in clazz_name:
                return 'Checkbox'
            elif 'switch' in clazz_name:
                return 'Switch'
            else:
                return 'Input'
        if comp['componentLabel'] == 'Text Button':
            clazz_name = comp['class'].lower()
            if 'checkbox' in clazz_name:
                return 'Checkbox'
            else:
                return 'Button'
        if comp['componentLabel'] == 'Text':
            return 'Label'
        return comp['componentLabel']

    @staticmethod
    def feat_method_text_only(gui, n, m, to_lower, quote, style):
        features = [(ui_comp['id'], ' '.join(ui_comp['text'].split(' ')[:m]))
                    for ui_comp in gui['ui_comps'] if ui_comp.get('text')][:n]
        if to_lower:
            features = [(feat[0], feat[1].lower()) for feat in features]
        if quote:
            features = [(feat[0], '"' + feat[1] + '"') for feat in features]
        return {feat[0]: feat[1] for feat in features}

    @staticmethod
    def feat_method_text_comp_type(gui, n, m, to_lower, quote, style):
        features = []
        for ui_comp in gui['ui_comps']:
            uic_text = ui_comp.get('text').strip() if ui_comp.get('text') else ui_comp.get('text_updated').strip() if ui_comp.get('text_updated') else ''
            uic_text = '"' + uic_text + '"' if quote else uic_text
            feat_str = ''
            if ui_comp.get('componentLabel') == 'Icon':
                icon_text = ' '.join(ui_comp.get('iconClass').split('_')).strip()
                icon_text = '"' + icon_text + '"' if quote else icon_text
                feat_str = icon_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
            elif ui_comp.get('componentLabel') == 'Text Button':
                if ui_comp.get('buttonClass'):
                    button_text = ' '.join(ui_comp.get('buttonClass').split('_')).strip()
                    button_text = '"' + button_text + '"' if quote else button_text
                    feat_str = button_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                elif ui_comp.get('textButtonClass'):
                    button_text = ' '.join(ui_comp.get('textButtonClass').split('_')).strip()
                    button_text = '"' + button_text + '"' if quote else button_text
                    feat_str = button_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                else:
                    feat_str = uic_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
            elif ui_comp.get('componentLabel') == 'Input':
                if ui_comp.get('text'):
                    input_text = '"' + uic_text + '"' if quote else button_text
                    feat_str = input_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                elif ui_comp.get('text_updated'):
                    input_text = '"' + ui_comp.get('text_updated').strip().replace('\n', '').replace('\f', '') + '"' \
                        if quote else ui_comp.get('text_updated').strip().replace('\n', '').replace('\f', '')
                    feat_str = input_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                else:
                    feat_str = '(' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
            else:
                if ui_comp.get('text'):
                    feat_str = uic_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                else:
                    feat_str = '(' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
            if to_lower:
                feat_str = feat_str.lower()
            features.append((ui_comp.get('id'), feat_str, ui_comp.get('bounds')))
        return {feat[0]: (feat[1], feat[2]) for feat in features}

    @staticmethod
    def feat_method_text_comp_type_res_id(gui, n, m, to_lower, quote, style):
        features = []
        for ui_comp in gui['ui_comps']:
            uic_text = ui_comp.get('text').strip() if ui_comp.get('text') else ui_comp.get('text_updated').strip() if ui_comp.get('text_updated') else ''
            uic_text = '"' + uic_text + '"' if quote else uic_text
            feat_str = ''
            if ui_comp.get('componentLabel') == 'Icon':
                icon_text = ' '.join(ui_comp.get('iconClass').split('_')).strip()
                icon_text = '"' + icon_text + '"' if quote else icon_text
                feat_str = icon_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
            elif ui_comp.get('componentLabel') == 'Text Button':
                if ui_comp.get('buttonClass'):
                    button_text = ' '.join(ui_comp.get('buttonClass').split('_')).strip()
                    button_text = '"' + button_text + '"' if quote else button_text
                    feat_str = button_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                elif ui_comp.get('textButtonClass'):
                    button_text = ' '.join(ui_comp.get('textButtonClass').split('_')).strip()
                    button_text = '"' + button_text + '"' if quote else button_text
                    feat_str = button_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                else:
                    feat_str = uic_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
            elif ui_comp.get('componentLabel') == 'Input':
                if ui_comp.get('text'):
                    input_text = '"' + uic_text + '"' if quote else button_text
                    feat_str = input_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                elif ui_comp.get('text_updated'):
                    input_text = '"' + ui_comp.get('text_updated').strip().replace('\n', '').replace('\f', '') + '"' \
                        if quote else ui_comp.get('text_updated').strip().replace('\n', '').replace('\f', '')
                    feat_str = input_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                else:
                    feat_str = '(' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
            else:
                if ui_comp.get('text'):
                    feat_str = uic_text + ' (' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
                else:
                    feat_str = '(' + GUI2Str.get_refined_comp_type(ui_comp) + ')'
            feat_str += ' (' + GUI2Str.normalize_resource_id(ui_comp.get('resource-id')) + ')' if ui_comp.get(
                'resource-id') else ''
            style_attrs = []
            if style.get(GUI2Str.STYLE_SIZE):
                bounds = ui_comp['bounds']
                width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
                style_attrs.append('width:' + str(width))
                style_attrs.append('height:' + str(height))
            if style.get(GUI2Str.STYLE_BACK_COLOR) and ui_comp.get('bg_color'):
                style_attrs.append('bg_color:' + ui_comp.get('bg_color'))
            if style.get(GUI2Str.STYLE_FONT_COLOR) and ui_comp.get('text_color'):
                style_attrs.append('text_color:' + ui_comp.get('text_color'))
            if style.get(GUI2Str.STYLE_FONT_SIZE) and ui_comp.get('font_size'):
                style_attrs.append('font_size:' + str(int(ui_comp.get('font_size'))))
            if style_attrs:
                feat_str = feat_str + ' (' + ';'.join(style_attrs) + ')'
            if to_lower:
                feat_str = feat_str.lower()
            features.append((ui_comp.get('id'), feat_str, ui_comp.get('bounds')))
        return {feat[0]: (feat[1], feat[2]) for feat in features}

    @staticmethod
    def feat_method_html(gui, n, m, to_lower, quote, style):
        features = []
        for ui_comp in gui['ui_comps']:
            uic_text = ui_comp.get('text').strip() if ui_comp.get('text') else ui_comp.get('text_updated').strip() if ui_comp.get('text_updated') else ''
            html_comp = GUI2Str.html_comp_mapping.get(GUI2Str.get_refined_comp_type(ui_comp))
            feat_str = html_comp[0]
            if ui_comp.get('resource-id'):
                feat_str += ' id="' + '-'.join(GUI2Str.normalize_resource_id(ui_comp.get('resource-id')).split(' ')) + '"'
            style_attrs = []
            if style.get(GUI2Str.STYLE_SIZE):
                bounds = ui_comp['bounds']
                width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
                style_attrs.append('width:' + str(width))
                style_attrs.append('height:' + str(height))
            if style.get(GUI2Str.STYLE_BACK_COLOR) and ui_comp.get('bg_color'):
                style_attrs.append('bg_color:' + ui_comp.get('bg_color'))
            if style.get(GUI2Str.STYLE_FONT_COLOR) and ui_comp.get('text_color'):
                style_attrs.append('text_color:' + ui_comp.get('text_color'))
            if style.get(GUI2Str.STYLE_FONT_SIZE) and ui_comp.get('font_size'):
                style_attrs.append('font_size:' + str(int(ui_comp.get('font_size'))))
            if style_attrs:
                feat_str = feat_str + ' style="' + ';'.join(style_attrs) + '"'
            feat_str += '>'
            if ui_comp.get('componentLabel') == 'Icon':
                icon_text = ' '.join(ui_comp.get('iconClass').split('_')).strip()
                feat_str += icon_text
            elif ui_comp.get('componentLabel') == 'Text Button':
                if ui_comp.get('buttonClass'):
                    button_text = ' '.join(ui_comp.get('buttonClass').split('_')).strip()
                    feat_str += button_text
                elif ui_comp.get('textButtonClass'):
                    button_text = ' '.join(ui_comp.get('textButtonClass').split('_')).strip()
                    feat_str += button_text
                else:
                    feat_str += uic_text
            else:
                if ui_comp.get('text'):
                    feat_str += uic_text
            feat_str += html_comp[1]
            features.append((ui_comp.get('id'), feat_str))
        if to_lower:
            feat_str = feat_str.lower()
        return {feat[0]: feat[1] for feat in features}

    @staticmethod
    def features_to_str(gui, feat_method, n, m, to_lower, quote, style):
        if feat_method == GUI2Str.FEAT_METHOD_TEXT_ONLY:
            return GUI2Str.feat_method_text_only(gui, n, m, to_lower, quote, style)
        elif feat_method == GUI2Str.FEAT_METHOD_TEXT_COMP_TYPE:
            return GUI2Str.feat_method_text_comp_type(gui, n, m, to_lower, quote, style)
        elif feat_method == GUI2Str.FEAT_METHOD_TEXT_COMP_TYPE_RES_ID:
            return GUI2Str.feat_method_text_comp_type_res_id(gui, n, m, to_lower, quote, style)
        elif feat_method == GUI2Str.FEAT_METHOD_HTML:
            return GUI2Str.feat_method_html(gui, n, m, to_lower, quote, style)

    @staticmethod
    def filter_uic_groups(uic_groups):
        filtered_uic_groups = []
        # Sort ui comp group based on number of ui comps
        uic_groups_sorted = sorted(uic_groups, key=lambda x: len(x['ui_comp_ids']), reverse=True)
        for i, uic_group_1 in enumerate(uic_groups_sorted, 0):
            subset_count = 0
            for uic_group_2 in uic_groups_sorted[(i + 1):]:
                if uic_group_1['id'] != uic_group_2['id']:
                    if set(uic_group_2['ui_comp_ids']).issubset(uic_group_1['ui_comp_ids']):
                        subset_count += 1
            if subset_count == 0:
                filtered_uic_groups.append(uic_group_1)
        return filtered_uic_groups

    @staticmethod
    def comp_in_uic(ui_comp_id, ui_comp_groups):
        for uic in ui_comp_groups:
            if ui_comp_id in uic.get('ui_comp_ids'):
                return True
        return False

    @staticmethod
    def structure_to_str(gui, feat_mappings, struct_method, style):
        gui_cpy = copy.deepcopy(gui)
        gui_mapping = {elem['id']: elem for elem in gui['ui_comps']}
        if struct_method == GUI2Str.STRUCT_METHOD_SIMPLE_BULLETS:
            return '\n- ' + '\n- '.join([elem for elem in feat_mappings.values()])
        elif struct_method == GUI2Str.STRUCT_METHOD_SIMPLE_BULLETS_SORTED:
            uic_bounds = [(key, val, gui_mapping[key]['bounds']) for key, val in feat_mappings.items()]
            uic_sorted = sorted(uic_bounds, key=lambda x: (x[2][1], x[2][0]))
            return '\n- ' + '\n- '.join([elem[1] for elem in uic_sorted])
        elif struct_method == GUI2Str.STRUCT_METHOD_TWO_LEVEL_BULLETS or struct_method == GUI2Str.STRUCT_METHOD_TWO_LEVEL_HTML:
            uic_groups = gui_cpy['ui_comp_groups']
            uic_groups = gui_cpy['ui_comp_groups']
            single_ui_comps = [(ui_comp_id, vals[1]) for ui_comp_id, vals in feat_mappings.items()
                               if not GUI2Str.comp_in_uic(ui_comp_id, uic_groups)]
            for elem in single_ui_comps:
                uic_groups.append({
                    "componentLabel": "Layout",
                    "bounds": elem[1],
                    "class": "android.widget.LinearLayout",
                    "bg_color": "#FFFFFF",
                    "ui_comp_ids": [elem[0]],
                    'id': str(uuid.uuid4())
                })
            filtered_uic_groups = GUI2Str.filter_uic_groups(uic_groups)
            # Find remaining ui comp ids and add them again
            filtered_ui_comp_ids = []
            for fuic in filtered_uic_groups:
                filtered_ui_comp_ids.extend(fuic['ui_comp_ids'])
            filtered_ui_comp_ids = set(filtered_ui_comp_ids)
            all_ui_comp_ids = set([elem['id'] for elem in gui_cpy['ui_comps']])
            missing_ui_comp_ids = all_ui_comp_ids.difference(filtered_ui_comp_ids)
            # For the missing ui comp ids, find the smallest ui comp group
            uic_groups_sorted_len = sorted(uic_groups, key=lambda x: len(x['ui_comp_ids']), reverse=False)
            matched_ui_comp_groups = {}
            for miss_ui_comp_id in missing_ui_comp_ids:
                for uic_group_len in uic_groups_sorted_len:
                    if miss_ui_comp_id in uic_group_len['ui_comp_ids']:
                        if uic_group_len['id'] in matched_ui_comp_groups:
                            matched_ui_comp_groups[uic_group_len['id']]['ui_comp_ids'].append(miss_ui_comp_id)
                            break
                        else:
                            matched_ui_comp_groups[uic_group_len['id']] = {
                                "componentLabel": "Layout",
                                "bounds": uic_group_len['bounds'],
                                "class": "android.widget.LinearLayout",
                                "bg_color": "#FFFFFF",
                                "ui_comp_ids": [miss_ui_comp_id],
                                'id': str(uuid.uuid4())
                            }
                            break
            filtered_uic_groups.extend([val for key, val in matched_ui_comp_groups.items()])
            uic_groups_sorted = sorted(filtered_uic_groups, key=lambda x: (x['bounds'][1], x['bounds'][0]))
            feat_str = ''
            for uic_group in uic_groups_sorted:
                uic_group['ui_comp_ids'] = [(feat_mappings.get(idd)[0], gui_mapping.get(idd)) for idd in
                                            uic_group['ui_comp_ids']]
                uic_group['ui_comp_ids'] = sorted(uic_group['ui_comp_ids'],
                                                  key=lambda x: (x[1]['bounds'][1], x[1]['bounds'][0]))
                if struct_method == GUI2Str.STRUCT_METHOD_TWO_LEVEL_BULLETS:
                    feat_str += '- ' + uic_group.get('componentLabel')
                    feat_str += '\n\t- ' + '\n\t- '.join([elem[0] for elem in uic_group['ui_comp_ids']]) + '\n'
                elif struct_method == GUI2Str.STRUCT_METHOD_TWO_LEVEL_HTML:
                    html_mapping = GUI2Str.html_comp_group_mapping.get(uic_group.get('componentLabel'))
                    feat_str += html_mapping[0]
                    style_attrs = []
                    feat_str += '>'
                    feat_str += '\n\t' + '\n\t'.join([elem[0] for elem in uic_group['ui_comp_ids']]) + '\n'
                    feat_str += html_mapping[1] + '\n'
            return feat_str

    def get_str_repr_gui(self, gui, n, m, to_lower, quote, style, feat_method, struct_method):
        gui = self.all_guis_with_comps[self.all_guis_with_comps['id'] == int(gui)]['data'].values.tolist()[0]
        feat_mappings = GUI2Str.features_to_str(gui, feat_method, n, m, to_lower, quote, style)
        final_str = GUI2Str.structure_to_str(gui, feat_mappings, struct_method, style)
        return final_str