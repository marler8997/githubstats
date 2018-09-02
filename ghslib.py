import os
import sys
import string
import re
import requests
import json
import hashlib

script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(script_dir, "data")
github_graphql_server = "api.github.com"

def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return None
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))

def parse_repo(repo):
    parts = repo.split('/')
    if len(parts) == 2:
        return (parts[0], parts[1])
    else:
        sys.exit("a repo must be of the form owner/repo, but got '%s'" % repo)

def get_auth_prop(auth_file, auth, prop):
    if prop not in auth:
        sys.exit("Error: auth file '%s' is missing the '%s' property" % (auth_file, prop))
    return auth[prop]

def read_auth_token(server):
    auth_file = os.path.join(data_dir, "auth.json")
    if not os.path.exists(auth_file):
        sys.exit("Error: authentication has not been setup, need to create '%s'" % auth_file)
    with open(auth_file) as file:
        auth = json.load(file)
    if "servers" in auth:
        servers = auth["servers"]
        if server in servers:
            server_node = servers[server]
            return get_auth_prop(auth_file, server_node, 'token')
    return get_auth_prop(auth_file, auth, 'token')


def setup_server_cache_dir(server):
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    server_dir = os.path.join(data_dir, server)
    if not os.path.isdir(server_dir):
        os.mkdir(server_dir)
    return server_dir

def do_query(server, auth_token, query):
    request = requests.post('https://' + server + '/graphql', json={'query':query},
        headers = {"Authorization" : "Bearer " + auth_token})
    if request.status_code != 200:
        sys.exit("Error: HTTP request failed (status=%s), response:\n%s" % (request.status_code, request.text))
    response = request.json()
    if "errors" in response:
        errors = response["errors"]
        print("------------------------------------------------")
        print("Query failed:\n%s" % query)
        print("These are the errors:\n%s" % errors)
        sys.exit("query failed")
    return response["data"]


def get_ancestor(obj, path):
    parts = path.split('.')
    for part in parts:
        obj = obj[part]
    return obj


# Perform the graphql request and save it in the cache
def get_graphql(query, **kwargs):
    no_cache = kwargs.pop("no_cache", False)
    server = kwargs.pop("server", github_graphql_server)
    paginate = kwargs.pop("paginate", False)

    server_dir = setup_server_cache_dir(server)
    request_hash = hashlib.sha1(query.encode())
    request_hash_file = os.path.join(server_dir, request_hash.hexdigest())

    if no_cache or not os.path.isfile(request_hash_file):
        auth_token = read_auth_token(server)
        print("getting query from server...")

        if not paginate:
            jsonData = do_query(server, auth_token, query)
        else:
            print("paginate! query template is: %s" % query)
            node = paginate["node"]
            max_request_count = 1000
            chunk_size = 100
            next_paginate_arg = "first:" + str(chunk_size)
            all_edges = []
            request_count = 0
            while request_count < max_request_count:
                print("request %s: paginate arg is %s" % (request_count, next_paginate_arg))
                jsonData = do_query(server, auth_token, query % next_paginate_arg)
                request_count += 1

                page = get_ancestor(jsonData, node)
                edges = page["edges"]
                if len(edges) == 0:
                    print("no edges, I think we're done")
                    break;
                all_edges += edges
                # todo: print a nice error message if there is no cursor field
                last_cursor = edges[-1]["cursor"]
                next_paginate_arg = 'first:%s, after:"%s"' % (chunk_size, last_cursor)

            mod_point = get_ancestor(jsonData, node)
            mod_point["edges"] = all_edges

        with open(request_hash_file, "w") as file:
            json.dump(jsonData, file)
    else:
        print("getting query from cache '%s'..." % request_hash_file)

    with open(request_hash_file, "r") as file:
        return json.load(file)


    


