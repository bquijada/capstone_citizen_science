from authlib.integrations.flask_client import OAuth
from auth.decorators import requires_auth
from flask import Flask, render_template, request, Blueprint, redirect, session, url_for, current_app, jsonify, flash
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
    try:
        userinfo = session.get('user').get("userinfo")
        user = userinfo.get("sub")
    except:
        return redirect('/login',code = 302)

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
        content = request.get_json()
        content["user"] = user
        content["code"] = code
        content["observations_list"] = []

        for param in content["parameters"]:

            if param["observation_type"] == "Dropdown":
                if (len(param["options"])  == 1) & (param["options"][0] == ''):
                    return jsonify({"error": "Options for Dropdown required"}), 400

            if param["observation_type"] == "Checklist":
                if (len(param["options"])  == 1) & (param["options"][0] == ''):
                    return jsonify({"error": "Options for Checklist required"}), 400

        new_project = datastore.entity.Entity(key=client.key("projects"))
        new_project.update(content)

        try:
            client.put(new_project)
            return content, 201
        except Exception as e:

            return jsonify({"error": "Not able to create new project"}), 400

    elif request.method == 'GET':

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
    Get a project by code identifier
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
        return jsonify({"error": "Only GET requests are allowed for this endpoint"}), 405


@datastore_bp.route("/projects/<code>/observations/<student_id>", methods=["GET", "POST", "PUT"])
def observations_get_post(code, student_id):
    """
    GET , POST , PUT a student's observations
    """
    
    # Convert code to all uppercase.
    if code:
        code = code.upper()

    if request.method == 'POST':
        content = request.get_json()

        # Check for observation_parameters property in received body.
        if content.get("observation_parameters") == None:
            return jsonify({"error": "Missing observation_parameters property in body"}), 400

        # Add new observation entity
        new_observation = datastore.entity.Entity(key=client.key("observations"))

        # Get project for data validation
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)
        result = list(query.fetch())

        # Check for project
        if len(result) == 0:
            return jsonify({"error": "No projects found with code (" + code + ")"}), 404

        parameters = result[0]['parameters']
        project_prompt = []
        for param in parameters:
            project_prompt.append(param["prompt"])

        # Validate total prompts submitted in body
        project_prompt_len = len(project_prompt)
        observation_parameters_len = len(content["observation_parameters"])
        if observation_parameters_len != project_prompt_len:
            return jsonify({"error": "Number of prompts submitted in body does not match number of prompts in project"}), 400
            
        # Validate data entry
        for obs in content["observation_parameters"]: 

            # Check for prompt, observation_type, and value for each item.
            if len(obs) != 3:
                return jsonify({"error": "Total properties in (" + obs["prompt"] + ") does not equal to 3"}), 400
                
            if "prompt" not in obs or "observation_type" not in obs or "value" not in obs:
                return jsonify({"error": "Missing prompt, observation_type, or value"}), 400

            # Validate numerical entry
            if obs["observation_type"] == "Numerical":

                # Validate prompt
                if obs["prompt"] not in project_prompt:
                        return jsonify({"error": "Numerical prompt (" + obs["prompt"] + ") is not part of project"}), 400

                # Validate value
                if type(obs["value"]) != int:
                    if obs["value"].isdigit() == False:
                        return  jsonify({"error": "Numerical entry is not integer type or string type integer"}), 400
                elif type(obs["value"]) == int:
                    obs["value"] = str(obs["value"])
                    

            # Validate dropdown entry
            if obs["observation_type"] == "Dropdown":
                selected_dropdown = obs["value"]
                for param in parameters:
                    # Validate prompt
                    if obs["prompt"] not in project_prompt:
                        return jsonify({"error": "Dropdown prompt (" + obs["prompt"] + ") is not part of project"}), 400

                    # Validate value
                    if param["prompt"] == obs["prompt"]:
                        if selected_dropdown not in param["options"]:
                            return  jsonify({"error": "Selected dropdown is not an option"}), 400

            # Validate checklist entry
            if obs["observation_type"] == "Checklist":
                selected_checklist = obs["value"]
                for param in parameters:
                    # Validate Prompt
                    if obs["prompt"] not in project_prompt:
                        return jsonify({"error": "Checklist prompt (" + obs["prompt"] + ") is not part of project"}), 400

                    # Validate value
                    if param["prompt"] == obs["prompt"]:
                        if selected_checklist not in param["options"]:
                            return  jsonify({"error": "Selected checklist option is not an option"}), 400

        observation_content = {
            "code": code,
            "time_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "observation_parameters": content["observation_parameters"],
            "student_id": student_id
        }
        new_observation.update(observation_content)
        client.put(new_observation)
        new_observation_id = str(new_observation.key.id)
        observation_content["id"] = new_observation_id
        
        # Make a copy of observation_content to remove code property to append to observation_list in Project entity
        observation_content_copy = observation_content.copy()
        del observation_content_copy['code']
        # Update Project entity with new data.
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)
        results = list(query.fetch())
        project = results[0]
        project["observations_list"].append(observation_content_copy)
        client.put(project)
        return observation_content, 201
    elif request.method == 'GET':
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)

        results = list(query.fetch())

        if results:
            # Get project details
            query = client.query(kind="projects")
            query.add_filter("code", "=", code)
            project_results = list(query.fetch())
            parameters = project_results[0]['parameters']
            prompt_options = {}
            project_prompt = []
            for param in parameters:
                prompt_options[param["prompt"]] = param["options"]

        

            project = results[0]

            observations_list = project.get("observations_list", [])

            student_observations = [
                observation
                for observation in observations_list
                if observation.get("student_id") == student_id
            ]

            for observation in student_observations:
                for question in observation['observation_parameters']:
                    question["options"] = prompt_options[question["prompt"]]
                    
            project_results[0]["observations_list"].clear()
            project_results[0]["observations_list"] = student_observations

            return jsonify(project_results), 200
        else:
            return jsonify({"error": "Project not found"}), 404
    elif request.method == 'PUT':

        # get json from request
        content = request.get_json()

        # Check for id property in received body.
        if content.get("id") == None:
            return jsonify({"error": "Missing id property in body"}), 400
        
        datastore_id = content["id"]

        # Check for observation_parameters property in received body.
        if content.get("observation_parameters") == None:
            return jsonify({"error": "Missing observation_parameters property in body"}), 400
        
        # obtain observation Key
        observation_key = client.key("observations", int(datastore_id))
        observation = client.get(key=observation_key)

        if observation is None:
            return jsonify({"error": "Invalid datastore ID"}), 404

        # Get project for data validation
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)
        result = list(query.fetch())
        parameters = result[0]['parameters']
        project_prompt = []
        for param in parameters:
            project_prompt.append(param["prompt"])

        # Validate total prompts submitted in body
        project_prompt_len = len(project_prompt)
        observation_parameters_len = len(content["observation_parameters"])
        if observation_parameters_len != project_prompt_len:
            return jsonify({"error": "Number of prompts submitted in body does not match number of prompts in project"}), 400
            
        # Validate data entry
        for obs in content["observation_parameters"]: 
            
            # Check for prompt, observation_type, and value for each item.
            if len(obs) != 3:
                return jsonify({"error": "Total properties in (" + obs["prompt"] + ") does not equal to 3"}), 400
                
            if "prompt" not in obs or "observation_type" not in obs or "value" not in obs:
                return jsonify({"error": "Missing prompt, observation_type, or value"}), 400

            # Validate numerical entry
            if obs["observation_type"] == "Numerical":

                # Validate prompt
                if obs["prompt"] not in project_prompt:
                        return jsonify({"error": "Numerical prompt (" + obs["prompt"] + ") is not part of project"}), 400

                # Validate value
                if type(obs["value"]) != int:
                    if obs["value"].isdigit() == False:
                        return  jsonify({"error": "Numerical entry is not integer type or string type integer"}), 400
                elif type(obs["value"]) == int:
                    obs["value"] = str(obs["value"])
                    

            # Validate dropdown entry
            if obs["observation_type"] == "Dropdown":
                selected_dropdown = obs["value"]
                for param in parameters:
                    # Validate prompt
                    if obs["prompt"] not in project_prompt:
                        return jsonify({"error": "Dropdown prompt (" + obs["prompt"] + ") is not part of project"}), 400

                    # Validate value
                    if param["prompt"] == obs["prompt"]:
                        if selected_dropdown not in param["options"]:
                            return  jsonify({"error": "Selected dropdown is not an option"}), 400

            # Validate checklist entry
            if obs["observation_type"] == "Checklist":
                selected_checklist = obs["value"]
                for param in parameters:
                    # Validate Prompt
                    if obs["prompt"] not in project_prompt:
                        return jsonify({"error": "Checklist prompt (" + obs["prompt"] + ") is not part of project"}), 400

                    # Validate value
                    if param["prompt"] == obs["prompt"]:
                        if selected_checklist not in param["options"]:
                            return  jsonify({"error": "Selected checklist option is not an option"}), 400

        # change contents from datastore
        observation["observation_parameters"] = content["observation_parameters"]

        # update datastore
        client.put(observation)
        observation["id"] = datastore_id

        # Remove and update observation_list in Project entity with edited observation
        query = client.query(kind="projects")
        query.add_filter("code", "=", code)
        results = list(query.fetch())
        project = results[0]

        for project_observation in project["observations_list"]:
            if project_observation["id"] == str(datastore_id):
                # Remove old observation
                project["observations_list"].remove(project_observation)
                # Append edited observaiton
                project["observations_list"].append(observation)
        client.put(project)

        return jsonify(observation), 200
    else:
        return jsonify({"error": "Only POST, PUT, and GET requests are allowed for this endpoint"}), 405


@datastore_bp.route("/users/projects/<user_id>", methods=["GET"])
def get_all_projects(user_id):
    """
    GET all projects for a user
    """
    if request.method == 'GET':
        # filter for projects created by user
        query = client.query(kind="projects")
        query.add_filter("user", "=", user_id)
        results = list(query.fetch())

        # append id to results
        for e in results:
            e["id"] = e.key.id

        return jsonify(results), 200
    else:
        return 'Method not recognized', 405


@datastore_bp.route("/projects/<code>/observations", methods=["GET"])
def observations_get(code):
    """
    GET all observations for a project
    """
    # Convert code to all uppercase.
    if code:
        code = code.upper()

    if request.method == 'GET':

        query = client.query(kind="observations")
        query.add_filter("code", "=", code)

        # append id to results
        for e in results:
            e["id"] = e.key.id

        results = list(query.fetch())

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
