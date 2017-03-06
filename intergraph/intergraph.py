from flask import jsonify
from random import shuffle,randint


def random_member_response(username=None,arguments=None):
    data = {"text": ''.join(x for x in rosie(str(random_team_member(username,arguments))) if x not in "[],'\""), "response_type": "in_channel","parse":"full","link_names":1}
    resp = jsonify(data)
    return resp


def random_team_member(username,arguments):
    members = generate_member_list_minus_requester(username)
    if len(str(arguments)) == 0:
        return members[0]
    return remove_requested_members_from_pool(arguments, members)


def remove_requested_members_from_pool(arguments, members):
    for arguments in str(arguments).split(' '):
        for name in members:
            if arguments in name:
                members.remove(name)
    try:
        test = int(str(arguments).split(' ')[0])
        return members[:test]
    except Exception as e:
        return members[0]


def generate_member_list_minus_requester(username):
    members = [":colosi: @colosicm ", ":roberto: @perez ", ":nathan: @nwplotts ", ":rosa: @wrosa ",
               ":duke: @kevinduke ", ":sean: @sean "]
    if str(username) == 'perez':
        members.remove(":roberto: @perez ")
    if str(username) == 'colosicm':
        members.remove(":colosi: @colosicm ")
    if str(username) == 'kevinduke':
        members.remove(":duke: @kevinduke ")
    if str(username) == 'nwplotts':
        members.remove(":nathan: @nwplotts ")
    if str(username) == 'sean':
        members.remove(":sean: @sean ")
    if str(username) == 'wrosa':
        members.remove(":rosa: @wrosa ")
    shuffle(members)
    return members


def rosie(input: str):
    choice = randint(0,2)
    if choice == 0:
        input = input.replace(":rosa:",":rosie:")
    if choice == 1:
        input = input.replace(":rosa:",":will:")
    return input