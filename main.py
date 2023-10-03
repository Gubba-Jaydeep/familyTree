import numpy as np
from flask import Flask, redirect, url_for, render_template, request, flash

import os
from os.path import join, dirname
import pandas as pd

app = Flask(__name__)
source_data = '/Users/gubba.jaydeep/Documents/Project/famTree/static/data.csv'

img_str1 = '''
<div class="card" id={card_id} style="{style_data}">
        <div class="left">
            <img class="profile_img" src="/static/images/{id}.jpg" onerror="this.onerror=null; this.src='/static/images/default.jpg'" alt="">
        </div>
        <div class="right">
            <h2 class="name">{name}</h2>
            <p class="title">{description}</p>
            <p class="interests_title">Navigate: </p>
            <a href="/parent/{id}" class="pure-material-button-contained">Parents</a>
            <a href="/children/{id}" class="pure-material-button-contained">Children</a>
            <a href="/spouse/{id}" class="pure-material-button-contained">Spouse</a>
            <a href="/siblings/{id}" class="pure-material-button-contained">Siblings</a>
            </div>
    </div>
'''

html_str2 = '''
<form class="card" method="post">
    <div class="right">
        <h2 class="name">Add More {title}</h2>
        <div class="form-wrap">
            <div class="input">
                <label>Full Name</label>
                <input name="new_name" autocomplete="off">
            </div>
            <svg class="line">
            </svg>
        </div>
    </div>
</form>
'''


# def get_family_map():
#     fam_map = {}
#     with open('/Users/gubba.jaydeep/Documents/Project/famTree/static/data.csv', 'r') as fp:
#         lines = fp.readlines()
#         for line in lines[1:]:
#             id_from_file, name, parent, spouse = line.strip().split(',')
#             fam_map[id_from_file] = {'name': name, 'parent': parent, 'spouse': spouse}
#     return fam_map


@app.route('/')
def index(df_res=None, title=None, requestor = None, error_message = ''):
    if df_res is None:
        id_list = [(0, 'Jaydeep Gubba', 'Developer')]
    else:
        id_list = df_res[['id', 'name', 'description']].to_dict('split')['data']
    if title is None:
        title = 'Developer'
    res = ''
    if len(id_list) == 0:
        if error_message:
            res = error_message
        else:
            res = '<h1>NO DATA</h1>'
    else:
        counter = 1
        for i in id_list:
            res += img_str1.format(id=i[0], name=i[1], description=i[2], card_id = f"card_{counter}", style_data="")
            counter +=1
        # if requestor is not None:
        #     req_data = requestor[['id', 'name', 'description', 'style']].to_dict('split')['data'][0]
        #     res += img_str1.format(id=req_data[0], name=req_data[1], description=req_data[2], card_id = f"card_requestor", style_data=req_data[3])
    return render_template('index.html', result=res, title=title, form_data = html_str2.format(title = title) if title!='Developer' else '')


@app.route('/parent/<id>')
def go_to_parent(id):
    id = int(id)
    df = pd.read_csv(source_data)
    requestor = df[df['id'] == id]
    requestor['style'] = 'position: absolute;right: 50px;top: 155.8px;'
    requestor['description'] = ''
    main_name = list(requestor['name'])[0]
    req_title = f'Parents of {main_name}'
    description = f'Parent of {main_name}'
    parent_id = int(df[df['id'] == id]['parent'])
    if parent_id == -1:
        return index(pd.DataFrame(columns=['id', 'name', 'parent', 'spouse','description']), req_title, error_message=f'No Parent data available for {main_name}')
    spouse_id_of_parent = int(df[df['id'] == parent_id]['spouse'])
    spouse_id_of_parent = -2 if spouse_id_of_parent == -1 else spouse_id_of_parent
    df_res = df[(df['id'] == parent_id) | (df['id']==spouse_id_of_parent)]
    df_res['description'] = description
    return index(df_res, req_title, requestor = requestor)


@app.route('/children/<id>')
def go_to_children(id):
    id=int(id)
    df = pd.read_csv(source_data)
    requestor = df[df['id'] == id]
    requestor['style'] = 'position: absolute;left: 50px;top: 155.8px;'
    requestor['description'] = ''
    main_name = list(requestor['name'])[0]
    req_title = f'Children of {main_name}'
    description = f'Child of {main_name}'
    spouse_id = int(df[df['id'] == id]['spouse'])
    spouse_id = -2 if spouse_id==-1 else spouse_id
    df_res = df[(df['parent'] == id) | (df['parent'] == spouse_id)]
    df_res['description'] = description
    return index(df_res, req_title, requestor = requestor)


@app.route('/spouse/<id>')
def go_to_spouse(id):
    id = int(id)
    df = pd.read_csv(source_data)
    requestor = df[df['id'] == id]
    requestor['style'] = ''
    requestor['description'] = ''
    main_name = list(requestor['name'])[0]
    req_title = f'Spouse of {main_name}'
    df_res = df[(df['id'] == id) | (df['spouse'] == id)]
    df_res['description'] = df_res.apply(lambda a: req_title if a['id']!=id else 'Self', axis=1)
    return index(df_res, req_title)

@app.route('/siblings/<id>')
def go_to_sibling(id):
    id = int(id)
    df = pd.read_csv(source_data)
    main_name = list(df[df['id'] == id]['name'])[0]
    req_title = f'Siblings of {main_name}'
    parent_id = int(df[df['id'] == id]['parent'])
    if parent_id == -1:
        df_res = df[df['id'] == id]
        df_res['description'] = 'Self'
        return index(df_res, req_title)
    spouse_id_of_parent = int(df[df['id'] == parent_id]['spouse'])
    spouse_id_of_parent = -2 if spouse_id_of_parent == -1 else spouse_id_of_parent
    df_res = df[(df['parent'] == parent_id) | (df['parent'] == spouse_id_of_parent)]
    df_res['description'] = df_res.apply(lambda a: req_title if a['id']!=id else 'Self', axis=1)
    return index(df_res, req_title)


@app.route('/children/<id>', methods=['POST'])
def update_child_of(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        full_name = request.form['new_name']
        df = pd.read_csv(source_data)
        last_id = max(df['id'])
        new_df = pd.DataFrame([[last_id+1, full_name, id, -1]],columns=df.columns)
        df = pd.concat([df, new_df])
        df.to_csv(source_data, index=False)
    return go_to_children(id)


@app.route('/parent/<id>', methods=['POST'])
def add_parent_of(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        full_name = request.form['new_name']
        df = pd.read_csv(source_data)
        last_id = max(df['id'])
        new_parent_id = last_id + 1
        #updating the parent of child
        if df.at[df[df['id'] == id].index[0], 'parent'] == -1:
            df.at[df[df['id'] == id].index[0], 'parent'] = new_parent_id
            new_df = pd.DataFrame([[new_parent_id, full_name, -1, -1]], columns=df.columns)
        else:
            existing_parent_id = df.at[df[df['id'] == id].index[0], 'parent']
            df.at[df[df['id'] == existing_parent_id].index[0], 'spouse'] = new_parent_id
            new_df = pd.DataFrame([[new_parent_id, full_name, -1, existing_parent_id]], columns=df.columns)
        df = pd.concat([df, new_df])
        df.to_csv(source_data, index=False)
    return go_to_parent(id)

@app.route('/spouse/<id>', methods=['POST'])
def add_spouse_of(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        full_name = request.form['new_name']
        df = pd.read_csv(source_data)
        last_id = max(df['id'])
        new_spouse_id = last_id + 1
        #adding spouse of id as full_name
        df.at[df[df['id'] == id].index[0], 'spouse'] = new_spouse_id
        #adding new entry
        new_df = pd.DataFrame([[new_spouse_id, full_name, -1, id]], columns=df.columns)
        df = pd.concat([df, new_df])
        df.to_csv(source_data, index=False)
    return go_to_spouse(id)

@app.route('/siblings/<id>', methods=['POST'])
def add_siblings(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        full_name = request.form['new_name']
        df = pd.read_csv(source_data)
        last_id = max(df['id'])
        new_sibling_id = last_id + 1
        main_name = list(df[df['id'] == id]['name'])[0]
        req_title = f'Siblings of {main_name}'
        parent_id = int(df[df['id'] == id]['parent'])
        if parent_id == -1:
            return index(pd.DataFrame(columns=['id', 'name', 'parent', 'spouse', 'description']), req_title, error_message=f'No Parent data available for {main_name}')
        new_df = pd.DataFrame([[new_sibling_id, full_name, parent_id, -1]], columns=df.columns)
        df = pd.concat([df, new_df])
        df.to_csv(source_data, index=False)
    return go_to_sibling(id)
