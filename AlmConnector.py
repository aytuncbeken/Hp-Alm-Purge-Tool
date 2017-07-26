#!/usr/bin/env python3
"""
    This Project is a Python based HP ALM Purge Wizard.
    This is the Api file which includes rest communication functions with HP Alm
    For detailed informatin please visit
    https://github.com/aytuncbeken/Hp-Alm-Purge-Tool

    Author:Aytunc BEKEN
    Python Version:3.6
    License:GPL
"""

import requests

almHost = None
almPort = None
almDomain = None
almProject = None
requester = requests.Session()


def generate_url_for_alm(_url):
    global almHost
    global almPort
    generated_url = "http://" + almHost + ":" + almPort + _url
    return generated_url


def connect_alm(_alm_host, _alm_port, _alm_user, _alm_pass, _alm_domain,_alm_project):
    global almHost
    global almPort
    global almDomain
    global almProject
    global requester
    almHost = _alm_host
    almPort = _alm_port
    almDomain = _alm_domain
    almProject = _alm_project
    auth_xml = "<alm-authentication><user>"+_alm_user+"</user><password>"+_alm_pass+"</password></alm-authentication>"
    url = "/qcbin/authentication-point/alm-authenticate"
    try:
        response = requester.post(generate_url_for_alm(url), auth_xml)
        response.close()
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False
    except:
        return False


def check_authentication():
    global requester
    url = "/qcbin/rest/is-authenticated"
    try:
        response = requester.get(generate_url_for_alm(url))
        response.close()
        if response.status_code == requests.codes.ok:
            return True
        return False
    except:
        return False


def get_session():
    global requester
    url = "/qcbin/rest/site-session"
    try:
        response = requester.post(generate_url_for_alm(url))
        response.close()
        if response.status_code == requests.codes.created:
            return True
        return False
    except:
        return False


def get_run_list():
    global almDomain
    global almProject
    global requester
    url = "/qcbin/rest/domains/"+almDomain+"/projects/"+almProject+"/runs?limit=0"
    try:
        response = requester.get(generate_url_for_alm(url), headers={"accept": "application/json"})
        response.close()
        return response.text
    except:
        return None


def get_test_list_with_only_id(limit, offset):
    global almDomain
    global almProject
    global requester
    if limit is None or offset is None:
        url = "/qcbin/rest/domains/" + almDomain + "/projects/" + almProject + "/tests?order-by=+id"
    else:
        url = "/qcbin/rest/domains/"+almDomain+"/projects/"+almProject+"/tests?limit="+str(limit)+"&offset=" + str(offset) + "&fields=id&order-by=+id"
    try:
        response = requester.get(generate_url_for_alm(url), headers={"accept": "application/json"})
        response.close()
        if response.status_code == requests.codes.ok:
            return response.text
        return None
    except:
        return None


def get_testset_list_with_only_id(limit, offset):
    global almDomain
    global almProject
    global requester
    if limit is None or offset is None:
        url = "/qcbin/rest/domains/" + almDomain + "/projects/" + almProject + "/test-sets?order-by=-id&fields=id,name"
    else:
        url = "/qcbin/rest/domains/"+almDomain+"/projects/"+almProject+"/test-sets?limit="+str(limit)+"&offset=" + str(offset) + "&fields=id,name&order-by=+id"
    try:
        response = requester.get(generate_url_for_alm(url), headers={"accept": "application/json"})
        response.close()
        if response.status_code == requests.codes.ok:
            return response.text
        return None
    except:
        return None

def get_testcycl_list_by_test_set(testset_id):
    global almDomain
    global almProject
    global requester
    if testset_id is None:
        return None
    url = "/qcbin/rest/domains/" + almDomain + "/projects/" + almProject + "/runs?query={cycle-id["+testset_id+"]}&fields=testcycl-id,id,testcycl-name&order-by=-id"
    try:
        response = requester.get(generate_url_for_alm(url), headers={"accept": "application/json"})
        response.close()
        if response.status_code == requests.codes.ok:
            return response.text
        return None
    except:
        return None

def get_run_by_testcycl(testcycl_id):
    global almDomain
    global almProject
    global requester
    if testcycl_id is None:
        return None
    url = "/qcbin/rest/domains/" + almDomain + "/projects/" + almProject + "/runs?query={testcycl-id["+testcycl_id+"]}&fields=id,execution-date&order-by=+id"
    try:
        response = requester.get(generate_url_for_alm(url), headers={"accept": "application/json"})
        response.close()
        if response.status_code == requests.codes.ok:
            return response.text
        return None
    except:
        return None

def get_test_runs(test_id):
    global almDomain
    global almProject
    global requester
    if test_id is None:
        return None
    url = "/qcbin/rest/domains/" + almDomain + "/projects/" + almProject + "/runs?query={test-id["+test_id+"]}&fields=id,execution-date&order-by=+id"
    try:
        response = requester.get(generate_url_for_alm(url), headers={"accept": "application/json"})
        response.close()
        if response.status_code == requests.codes.ok:
            return response.text
        return None
    except:
        return None


def delete_run(run_id):
    global almDomain
    global almProject
    global requester
    if run_id is None:
        return None
    url = "/qcbin/rest/domains/" + almDomain + "/projects/" + almProject + "/runs/" + str(run_id)
    try:
        response = requester.delete(generate_url_for_alm(url))
        response.close()
        if response.status_code == requests.codes.ok:
            return True
        return False
    except:
        return False










