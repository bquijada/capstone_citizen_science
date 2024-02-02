from authlib.integrations.flask_client import OAuth
from auth.decorators import requires_auth
from flask import Flask, render_template, request, Blueprint, redirect, session, url_for, current_app, jsonify
import os
from google.cloud import datastore
import requests
import string
import random
import json, sys
from datetime import datetime

client = datastore.Client()
datastore_bp = Blueprint('datastore', __name__)

def code_generator(size, chars):
    code = []
    for i in range(0,size):
        rand_char = random.choice(chars)
        code.append(rand_char)
    return ''.join(code)

@datastore_bp.route("/projects", methods=["GET", "POST"])
def projects_get_post():
    """
    Get , Post a project
    """
    print('outside', file=sys.stderr)
    if request.method == 'POST':
        code = code_generator(5,string.ascii_uppercase+string.digits)

        # check if code generated is already in the database
        query = client.query(kind="projects")
        query.add_filter("projects", "=", code)
        result = list(query.fetch())
        while result:
            code = code_generator(5,string.ascii_uppercase+string.digits)
            result = list(query.fetch())

        # Access form data using request.form
        sub = request.form.get("sub")
        project_name = request.form.get("project_name")
        data_type = request.form.get("data_type")
        data_parameters = request.form.get("data_parameters")

        new_project = datastore.entity.Entity(key=client.key("projects"))
        new_project.update({
            "sub": sub,
            "project_name": project_name,
            "code": code,
            "data_type": data_type,
            "data_parameters": data_parameters,
            "data_list": [],
            })

        client.put(new_project)
        return jsonify({"message": "Project created successfully"}), 201

    elif request.method == 'GET':

        #obtain sub of logged in user
        userinfo = session.get('user').get("userinfo")
        sub = userinfo.get("sub")

        #filter for projects created by user
        query = client.query(kind="projects")
        query.add_filter("sub", "=", sub)
        results = list(query.fetch())

        #append id to results
        for e in results:
            e["id"] = e.key.id

        return jsonify(results)
    else:
        return jsonify({"error": "Only POST and GET requests are allowed for this endpoint"}), 405

@datastore_bp.route("/data/<code>", methods=["GET", "POST"])
def data_get_post(code):
    """
    GET , POST Data
    """

    if request.method == 'POST':

        #Add new data entity
        content = request.get_json()
        new_data = datastore.entity.Entity(key=client.key("data"))
        data_content = {

            "code": code,
            "time_date":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data":content["data"],
            }
        new_data.update(data_content)
        client.put(new_data)
        new_data_id = str(new_data.key.id)
        data_content["id"] = new_data_id

        #Update Project entity with new data.
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)
        results = list(query.fetch())
        project = results[0]
        project["data_list"].append(data_content)
        client.put(project)
        return data_content
    elif request.method == 'GET':

        #filter for projects created by user
        query = client.query(kind="data")
        query.add_filter("code", "=", code)
        results = list(query.fetch())

        #append id to results
        for e in results:
            e["id"] = e.key.id

        return jsonify(results)
    else:
        return 'Method not recognized'