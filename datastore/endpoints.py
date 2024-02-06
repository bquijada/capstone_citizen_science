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
    for i in range(0, size):
        rand_char = random.choice(chars)
        code.append(rand_char)
    return ''.join(code)


@datastore_bp.route("/projects", methods=["GET", "POST"])
def projects_get_post():
    """
    Get , Post a project
    """
    userinfo = session.get('user').get("userinfo")
    user = userinfo.get("sub")

    if request.method == 'POST':
        code = code_generator(5, string.ascii_uppercase + string.digits)

        # check if code generated is already in the database
        query = client.query(kind="projects")
        results = list(query.fetch())
        if results:  # handles cases when project table is empty
            query.add_filter("code", "=", code)
            result = list(query.fetch())
            while result:
                code = code_generator(5, string.ascii_uppercase + string.digits)
                query.add_filter("code", "=", code)
                result = list(query.fetch())

        # Access form data using request.form (because form content-type is not json)
        userinfo = session.get('user').get("userinfo")
        sub = userinfo.get("sub")
        content = request.get_json()
        content["user"] = sub
        content["code"] = code

        new_project = datastore.entity.Entity(key=client.key("projects"))
        new_project.update(content)

        try:
            client.put(new_project)
            return render_template('project.html', project_name=content["title"], instructions=content["description"])
        except Exception as e:

            return jsonify({"Error": "Not able to create new project"})

    elif request.method == 'GET':

        # obtain sub of logged in user
        userinfo = session.get('user').get("userinfo")
        user = userinfo.get("sub")

        # filter for projects created by user
        query = client.query(kind="projects")
        query.add_filter("user", "=", user)
        results = list(query.fetch())

        # append id to results
        for e in results:
            e["id"] = e.key.id

        return jsonify(results), 200
    else:
        return 'Method not recognized'


@datastore_bp.route("/projects/<code>", methods=["GET"])
def projects_get_code(code):
    """
    Get , Post a project
    """

    if request.method == 'GET':

        # filter for projects created by project code
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)
        results = list(query.fetch())

        # append id to results
        for e in results:
            e["id"] = e.key.id

        return jsonify(results), 200
    else:
        return jsonify({"error": "Only POST and GET requests are allowed for this endpoint"}), 405


@datastore_bp.route("/projects/<code>/observations", methods=["GET", "POST"])
def observations_get_post(code):
    """
    GET , POST Data
    """

    if request.method == 'POST':

        # Add new observation entity
        content = request.get_json()
        new_observation = datastore.entity.Entity(key=client.key("observations"))
        observation_content = {
            "code": code,
            "time_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "observation": content["observation"],
            "student_id": content["student_id"]
        }
        new_observation.update(observation_content)
        client.put(new_observation)
        new_data_id = str(new_observation.key.id)
        observation_content["id"] = new_data_id

        # Update Project entity with new data.
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)
        results = list(query.fetch())
        project = results[0]
        project["observation_list"].append(observation_content)
        client.put(project)
        return observation_content, 201
    elif request.method == 'GET':

        # filter for projects created by user
        query = client.query(kind="observations")
        query.add_filter("code", "=", code)
        results = list(query.fetch())

        # append id to results
        for e in results:
            e["id"] = e.key.id

        return jsonify(results), 200
    else:
        return 'Method not recognized'