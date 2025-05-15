import numpy as np
from flask import Flask, redirect, url_for, render_template, request, flash

import os
from os.path import join, dirname
import pandas as pd

app = Flask(__name__)
project_path = app.root_path
source_data = project_path + '/static/data.csv'
print(source_data)


card_data_str = '''
<div class="node-card"  id={card_id}>
        <div onclick="openModal('update', {{ name: '{name}', phone: '{phone_number}', id: '{id}' }})">
            <img src="/static/images/{id}.jpg" onerror="this.onerror=null; this.src='/static/images/default.jpg'" alt="Photo"
                 style="width: 200px;height: 200px;border-radius: 100%;object-fit: cover;">
            <div class="node-name">{name}</div>
            <div class="node-relation">{description}</div>
            <div class="node-phone" style="{style_data}">📞 {phone_number}</div>
        </div>
        <div class="node-links">
            <a href="/parent/{id}">Parents</a>
            <a href="/children/{id}">Children</a>
            <a href="/spouse/{id}">Spouse</a>
            <a href="/siblings/{id}">Siblings</a>
        </div>
    </div>
'''

add_more_html = '''
<div class="add-node-btn">
    <button onclick="openModal('create')">+ Add More {title}</button>
</div>
'''



@app.route('/')
def index(df_res=None, title=None, requestor=None, error_message=''):
    add_data = ''
    style_data = ''
    if df_res is None:
        id_list = [[0, 'Jaydeep Gubba', 'Developer', '9052838857']]
    else:
        id_list = df_res[['id', 'name', 'description', 'phone']].to_dict('split')['data']
    if title is None:
        title = 'Developer'
    res = ''
    if len(id_list) >= 2 and (('parents' in title.lower()) or ('spouse' in title.lower())):
        add_data = ''
    else:
        add_data = add_more_html.format(title=title)
    if len(id_list) == 0:
        if error_message:
            res = '<h1>' + error_message + '</h1>'
        else:
            res = '<h1>NO DATA</h1>'
        res += """
                <br>
                <div class="add-node-btn">
                    <button onclick="history.back()">Go Back</button>
                </div>
            """
    else:
        counter = 1
        for i in id_list:
            if i[3] == '-':
                style_data='visibility: hidden;'

            res += card_data_str.format(id=i[0], name=i[1], description=i[2], card_id=f"card_{counter}", style_data=style_data,
                                        phone_number=i[3])
            counter += 1
        # if requestor is not None:
        #     req_data = requestor[['id', 'name', 'description', 'style']].to_dict('split')['data'][0]
        #     res += img_str1.format(id=req_data[0], name=req_data[1], description=req_data[2], card_id = f"card_requestor", style_data=req_data[3])


        if not (
                'parent' in title.lower() or 'spouse' in title.lower() or 'siblings' in title.lower() or 'children' in title.lower()):
            add_data = ''
    df = pd.read_csv(source_data)
    suggestions = df[['id', 'name']].to_dict('records')
    return render_template('index.html', result=res, title=title, add_more_html=add_data, suggestions=suggestions)


@app.route('/<id>')
def go_to_id(id):
    df = pd.read_csv(source_data)
    df_res = df.loc[df['id'] == int(id)]
    df_res['description'] = 'Self'
    return index(df_res, list(df_res['name'])[0], requestor=None)

@app.route('/<id>', methods=['POST'])
def update_id(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        current_id = request.form['current_id']
        full_name = request.form['new_name']
        new_phone = request.form['new_phone']
        file = request.files['new_photo']
        df = pd.read_csv(source_data)
        if not current_id:
            print("should never each here,..")
        else:
            if full_name:
                df.loc[df['id'] == int(current_id), 'name'] = full_name
            if new_phone and new_phone != '-':
                df.loc[df['id'] == int(current_id), 'phone'] = new_phone
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{current_id}.jpg')
    return go_to_id(id)


@app.route('/parent/<id>')
def go_to_parent(id):
    id = int(id)
    df = pd.read_csv(source_data)
    requestor = df[df['id'] == id]
    # requestor['style'] = 'position: absolute;right: 50px;top: 155.8px;'
    requestor['description'] = ''
    main_name = list(requestor['name'])[0]
    req_title = f'Parents of {main_name}'
    description = f'Parent of {main_name}'
    parent_id = int(df[df['id'] == id]['parent'])
    if parent_id == -1:
        return index(pd.DataFrame(columns=['id', 'name', 'parent', 'spouse', 'description', 'phone']), req_title,
                     error_message=f'No Parent data available for {main_name}')
    spouse_id_of_parent = int(df[df['id'] == parent_id]['spouse'])
    spouse_id_of_parent = -2 if spouse_id_of_parent == -1 else spouse_id_of_parent
    df_res = df[(df['id'] == parent_id) | (df['id'] == spouse_id_of_parent)]
    df_res['description'] = description
    return index(df_res, req_title, requestor=requestor)


@app.route('/children/<id>')
def go_to_children(id):
    id = int(id)
    df = pd.read_csv(source_data)
    requestor = df[df['id'] == id]
    # requestor['style'] = 'position: absolute;left: 50px;top: 155.8px;'
    requestor['description'] = ''
    main_name = list(requestor['name'])[0]
    req_title = f'Children of {main_name}'
    description = f'Child of {main_name}'
    spouse_id = int(df[df['id'] == id]['spouse'])
    spouse_id = -2 if spouse_id == -1 else spouse_id
    df_res = df[(df['parent'] == id) | (df['parent'] == spouse_id)]
    df_res['description'] = description
    return index(df_res, req_title, requestor=requestor)


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
    df_res['description'] = df_res.apply(lambda a: req_title if a['id'] != id else 'Self', axis=1)
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
    df_res['description'] = df_res.apply(lambda a: req_title if a['id'] != id else 'Self', axis=1)
    return index(df_res, req_title)


@app.route('/children/<id>', methods=['POST'])
def update_child_of(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        current_id = request.form['current_id']
        full_name = request.form['new_name']
        new_phone = request.form['new_phone']
        file = request.files['new_photo']
        df = pd.read_csv(source_data)
        if not current_id:
            if str(new_phone).strip().lower() in ['','nan','none','-']:
                new_phone = '-'
            last_id = max(df['id'])
            new_df = pd.DataFrame([[last_id + 1, full_name, id, -1, new_phone]], columns=df.columns)
            df = pd.concat([df, new_df])
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{last_id + 1}.jpg')
        else:
            if full_name:
                df.loc[df['id'] == int(current_id), 'name'] = full_name
            if new_phone and new_phone != '-':
                df.loc[df['id'] == int(current_id), 'phone'] = new_phone
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{current_id}.jpg')
    return go_to_children(id)


@app.route('/parent/<id>', methods=['POST'])
def add_parent_of(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        current_id = request.form['current_id']
        full_name = request.form['new_name']
        new_phone = request.form['new_phone']
        file = request.files['new_photo']
        df = pd.read_csv(source_data)
        if not current_id:
            if str(new_phone).strip().lower() in ['','nan','none','-']:
                new_phone = '-'
            last_id = max(df['id'])
            new_parent_id = last_id + 1
            # updating the parent of child
            if df.at[df[df['id'] == id].index[0], 'parent'] == -1:
                df.at[df[df['id'] == id].index[0], 'parent'] = new_parent_id
                new_df = pd.DataFrame([[new_parent_id, full_name, -1, -1, new_phone]], columns=df.columns)
            else:
                existing_parent_id = df.at[df[df['id'] == id].index[0], 'parent']
                df.at[df[df['id'] == existing_parent_id].index[0], 'spouse'] = new_parent_id
                new_df = pd.DataFrame([[new_parent_id, full_name, -1, existing_parent_id, new_phone]], columns=df.columns)
            df = pd.concat([df, new_df])
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{last_id + 1}.jpg')
        else:
            if full_name:
                df.loc[df['id'] == int(current_id), 'name'] = full_name
            if new_phone and new_phone != '-':
                df.loc[df['id'] == int(current_id), 'phone'] = new_phone
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{current_id}.jpg')
    return go_to_parent(id)


@app.route('/spouse/<id>', methods=['POST'])
def add_spouse_of(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        current_id = request.form['current_id']
        full_name = request.form['new_name']
        new_phone = request.form['new_phone']
        file = request.files['new_photo']
        df = pd.read_csv(source_data)
        if not current_id:
            if str(new_phone).strip().lower() in ['','nan','none','-']:
                new_phone = '-'
            last_id = max(df['id'])
            new_spouse_id = last_id + 1
            # adding spouse of id as full_name
            df.at[df[df['id'] == id].index[0], 'spouse'] = new_spouse_id
            # adding new entry
            new_df = pd.DataFrame([[new_spouse_id, full_name, -1, id, new_phone]], columns=df.columns)
            df = pd.concat([df, new_df])
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{last_id + 1}.jpg')
        else:
            if full_name:
                df.loc[df['id'] == int(current_id), 'name'] = full_name
            if new_phone and new_phone != '-':
                df.loc[df['id'] == int(current_id), 'phone'] = new_phone
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{current_id}.jpg')
    return go_to_spouse(id)


@app.route('/siblings/<id>', methods=['POST'])
def add_siblings(id):
    id = int(id)
    if request.method == 'POST':
        print('got post data')
        current_id = request.form['current_id']
        full_name = request.form['new_name']
        new_phone = request.form['new_phone']
        file = request.files['new_photo']
        df = pd.read_csv(source_data)
        if not current_id:
            if str(new_phone).strip().lower() in ['','nan','none','-']:
                new_phone = '-'
            last_id = max(df['id'])
            new_sibling_id = last_id + 1
            main_name = list(df[df['id'] == id]['name'])[0]
            req_title = f'Siblings of {main_name}'
            parent_id = int(df[df['id'] == id]['parent'])
            if parent_id == -1:
                return index(pd.DataFrame(columns=['id', 'name', 'parent', 'spouse', 'description', 'phone']),
                             req_title,
                             error_message=f'No Parent data available for {main_name}')
            new_df = pd.DataFrame([[new_sibling_id, full_name, parent_id, -1, new_phone]], columns=df.columns)
            df = pd.concat([df, new_df])
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{last_id + 1}.jpg')
        else:
            if full_name:
                df.loc[df['id'] == int(current_id), 'name'] = full_name
            if new_phone and new_phone != '-':
                df.loc[df['id'] == int(current_id), 'phone'] = new_phone
            df.to_csv(source_data, index=False)
            if file:
                file.save(f'{project_path}/static/images/{current_id}.jpg')
    return go_to_sibling(id)


app.run()
