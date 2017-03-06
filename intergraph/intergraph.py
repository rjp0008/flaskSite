from flask import jsonify
from random import random


def random_member_response(request):
    data = {"text": rosie(str(random_team_member(request)).replace('[','').replace(']','').replace("'",'').replace(',','')), "response_type": "in_channel","parse":"full","link_names":1}
    resp = jsonify(data)
    return resp


def random_team_member(request):
    members = [":colosi: @colosicm ",":roberto: @perez ", ":nathan: @nwplotts ",":rosa: @wrosa ",":duke: @kevinduke ",":sean: @sean "]
    if str(request.form['user_name']) == 'perez':
        members.remove(":roberto: @perez ")
    if str(request.form['user_name']) == 'colosicm':
        members.remove(":colosi: @colosicm ")
    if str(request.form['user_name']) == 'kevinduke':
        members.remove(":duke: @kevinduke ")
    if str(request.form['user_name']) == 'nwplotts':
        members.remove(":nathan: @nwplotts ")
    if str(request.form['user_name']) == 'sean':
        members.remove(":sean: @sean ")
    if str(request.form['user_name']) == 'wrosa':
        members.remove(":rosa: @wrosa ")
    random.shuffle(members)
    if len(str(request.form['text'])) == 0:
        return members[0]
    for arguments in str(request.form['text']).split(' '):
        for name in members:
            if arguments in name:
                members.remove(name)
    try:
        test = int(str(request.form['text']).split(' ')[0])
        return members[:test]
    except Exception as e:
        return members[0]

def rosie(input: str):
    choice = random.randint(0,2)
    if choice == 0:
        input = input.replace(":rosa:",":rosie:")
    if choice == 1:
        input = input.replace(":rosa:",":will:")
    return input