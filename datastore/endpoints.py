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
    """
    Function generates random code with parameter size (length of code) and 
    chars (string of characters to randomly select from).
    """
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
        content["observations_list"] = []

        new_project = datastore.entity.Entity(key=client.key("projects"))
        new_project.update(content)

        try:
            client.put(new_project)
            return content, 201
        except Exception as e:

            return jsonify({"Error": "Not able to create new project"}), 400

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
        return 'Method not recognized', 405


@datastore_bp.route("/projects/<code>", methods=["GET"])
def projects_get_code(code):
    """
    Get , Post a project
    """
    # Convert code to all uppercase.
    if code:
        code = code.upper()

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


@datastore_bp.route("/projects/<code>/observations/<student_id>", methods=["GET", "POST", "PUT"])
def observations_get_post(code,student_id):
    """
    GET , POST , PUT Data
    """
    
    # Convert code to all uppercase.
    if code:
        code = code.upper()

    if request.method == 'POST':

        # Add new observation entity
        content = request.get_json()
        new_observation = datastore.entity.Entity(key=client.key("observations"))
        observation_content = {
            "code": code,
            "time_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "observation": content["observation"],
            "student_id": student_id
        }
        new_observation.update(observation_content)
        client.put(new_observation)
        new_observation_id = str(new_observation.key.id)
        observation_content["id"] = new_observation_id

        # Update Project entity with new data.
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)
        results = list(query.fetch())
        project = results[0]
        project["observations_list"].append(observation_content)
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
    
    elif request.method == 'PUT':
        
        # get json from request
        content = request.get_json()
        datastore_id = content["id"]

        # obtain observation Key

        observation_key = client.key("observations", int(datastore_id))
        observation = client.get(key = observation_key)
        
        if observation == None:
            return jsonify({"error": "Invalid datastore ID"}), 404
        
        # change contents from datastore
        observation["observation"] = content["observation"]

        # update datastore
        client.put(observation)
        
        observation["id"] = datastore_id
        return jsonify(observation), 200
    else:
        return jsonify({"error": "Only POST, PUT, and GET requests are allowed for this endpoint"}), 405
    

@datastore_bp.route("/projects/<code>/observations", methods=["GET"])
def observations_get(code):
    """
    GET Data
    """
    # Convert code to all uppercase.
    if code:
        code = code.upper()

    if request.method == 'GET':

        # filter for projects created by user
        query = client.query(kind="observations")
        query.add_filter("code", "=", code)

        results = list(query.fetch())

        # append id to results
        for e in results:
            e["id"] = e.key.id

        return jsonify(results), 200
    else:
        return jsonify({"error": "Only GET requests are allowed for this endpoint"}), 405
    
##################################################################################################
@datastore_bp.route("/projects", methods=["DELETE"])
def observations_delete():
    """
    For Postman use only, DELETE Data
    """
    userinfo = session.get('user').get("userinfo")
    user = userinfo.get("sub")

    if request.method == 'DELETE':

        # filter for projects created by user
        
        query = client.query(kind="projects")
        query.add_filter("user", "=", user)

        results = list(query.fetch())

        # append id to results
        for e in results:
            if len(e["observations_list"]) > 0:
                observations_list = e["observations_list"]
                for observation in observations_list:
                    observation_id = observation["id"]
                    observation_key = client.key("observations", int(observation_id))
                    observation = client.get(key = observation_key)
                    client.delete(observation)
            project_key = e.key
            project = client.get(project_key)
            client.delete(project)

        return "Deleted", 200