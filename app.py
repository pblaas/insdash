from steam import game_servers as gs
from flask import Flask, jsonify, request, render_template, url_for, flash, redirect, make_response
from flask_session import Session
from flask_session_captcha import FlaskSessionCaptcha
from urllib2 import Request
import valve.rcon
import sys
import errno
import os
import random
import socket
import time
import uuid
import logging


# import the flask extension
from flask_caching import Cache

__author__ = "Patrick Blaas <patrick@kite4fun.nl>"
__version__ = "1.0.9"

if "SERVERIP" not in os.environ:
    os.environ["SERVERIP"] = "83.96.176.30"

app = Flask(__name__)
app.secret_key = 'sakdfjasldfkj38sfkjasdaskdf'
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "insdash.db"))

app.config["SECRET_KEY"] = uuid.uuid4()
app.config['CAPTCHA_ENABLE'] = True
app.config['CAPTCHA_NUMERIC_DIGITS'] = 5
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)
captcha = FlaskSessionCaptcha(app)


def randomQuote():
    list = (
        "Don't be a buddy fucker, don't stop in doorways.",
        "Use V to speak to your team with your microphone.",
        "Quit gagglefucking and spread the fuck out!",
        "That thing gave me a fucking haircut.",
        "YAH I FUCKIN SHANKED EM.",
        "I JUST GUTTED THE FUCKER!",
        "We must have killed half the country by now!",
        "Fuck no!",
        "Hej, I'M RELOADING.",
        "Fuck fuck fuck!",
        "Capture this, blow up that, it's all the same...",
        "Die you bastard!",
        "EAT THIS!",
        "Perfect!, I'm low on ammo.",
        "Assholes!",
        "Fuck that!",
        "Burn you fucks!",
        "This is bullshit!",
        "ENOUGH WITH THE RPG'S ALRIGHT!",
        "Yeah I just pissed myself.",
        "I'M PINNED!",
        "I'M BEING SUPPRESSED!",
        "Yeah he's fucking dead!"
    )
    index = random.randint(0, len(list) - 1)
    return list[index].upper()

# MapList
mapList = (
    "Scenario_Crossing_Checkpoint_Insurgents",
    "Scenario_Crossing_Checkpoint_Security",
    "Scenario_Crossing_Firefight_West",
    "Scenario_Crossing_Push_Insurgents",
    "Scenario_Crossing_Push_Security",
    "Scenario_Crossing_Skirmish",
    "Scenario_Crossing_Team_Deathmatch",
    "Scenario_Farmhouse_Checkpoint_Insurgents",
    "Scenario_Farmhouse_Checkpoint_Security",
    "Scenario_Farmhouse_Firefight_East",
    "Scenario_Farmhouse_Firefight_West",
    "Scenario_Farmhouse_Push_Insurgents",
    "Scenario_Farmhouse_Push_Security",
    "Scenario_Farmhouse_Skirmish",
    "Scenario_Farmhouse_Team_Deathmatch",
    "Scenario_Summit_Checkpoint_Insurgents",
    "Scenario_Summit_Checkpoint_Security",
    "Scenario_Summit_Firefight_East",
    "Scenario_Summit_Firefight_West",
    "Scenario_Summit_Push_Insurgents",
    "Scenario_Summit_Push_Security",
    "Scenario_Summit_Skirmish",
    "Scenario_Summit_Team_Deathmatch",
    "Scenario_Refinery_Checkpoint_Insurgents",
    "Scenario_Refinery_Checkpoint_Security",
    "Scenario_Refinery_Firefight_West",
    "Scenario_Refinery_Push_Insurgents",
    "Scenario_Refinery_Push_Security",
    "Scenario_Refinery_Skirmish",
    "Scenario_Refinery_Team_Deathmatch",
    "Scenario_Precinct_Checkpoint_Insurgents",
    "Scenario_Precinct_Checkpoint_Security",
    "Scenario_Precinct_Firefight_East",
    "Scenario_Precinct_Firefight_West",
    "Scenario_Precinct_Push_Insurgents",
    "Scenario_Precinct_Push_Security",
    "Scenario_Precinct_Skirmish",
    "Scenario_Precinct_Team_Deathmatch",
    "Scenario_Hideout_Checkpoint_Insurgents",
    "Scenario_Hideout_Checkpoint_Security",
    "Scenario_Hideout_Firefight_East",
    "Scenario_Hideout_Firefight_West",
    "Scenario_Hideout_Push_Insurgents",
    "Scenario_Hideout_Push_Security",
    "Scenario_Hideout_Skirmish",
    "Scenario_Hideout_Team_Deathmatch",
    "Scenario_Outskirts_Checkpoint_Security",
    "Scenario_Outskirts_Checkpoint_Insurgents",
    "Scenario_Outskirts_Firefight_East",
    "Scenario_Outskirts_Firefight_West",
    "Scenario_Outskirts_Push_Insurgents",
    "Scenario_Outskirts_Push_Security",
    "Scenario_Outskirts_Skirmish",
    "Scenario_Outskirts_Team_Deathmatch",
    "Scenario_Ministry_Checkpoint_Security",
    "Scenario_Ministry_Checkpoint_Insurgents",
    "Scenario_Ministry_Firefight_A",
    "Scenario_Ministry_Skirmish",
    "Scenario_Ministry_Team_Deathmatch",
    "Scenario_Hillside_Checkpoint_Security",
    "Scenario_Hillside_Checkpoint_Insurgents",
    "Scenario_Hillside_Firefight_East",
    "Scenario_Hillside_Firefight_West",
    "Scenario_Hillside_Push_Insurgents",
    "Scenario_Hillside_Push_Security",
    "Scenario_Hillside_Skirmish",
    "Scenario_Hillside_Team_Deathmatch"
)


@app.route('/')
def home():
    try:
        server_addr = next(gs.query_master(r'\appid\581320\gameaddr\%s' % os.environ["SERVERIP"]))
        serverInfo = gs.a2s_info(server_addr)
        serverRules = gs.a2s_rules(server_addr)
        serverPlayers = gs.a2s_players(server_addr)
        return render_template('home.html', addr=server_addr, ip=os.environ["SERVERIP"], data=serverInfo, players=serverPlayers, rules=serverRules, quote=randomQuote())
    except StopIteration as e:
        e = "Unable to resolve server ip."
        return render_template('error.html', error=e)
    except socket.timeout as e:
        e = "Unable to resolve server ip."
        return render_template('error.html', error=e)
    except:
        e = "Unknown error."
        return render_template('error.html', error=e)


@app.route('/r/<string:ip>')
def remote(ip):
    try:
        server_addr = next(gs.query_master(r'\appid\581320\gameaddr\%s' % ip))
        serverInfo = gs.a2s_info(server_addr)
        serverRules = gs.a2s_rules(server_addr)
        serverPlayers = gs.a2s_players(server_addr)
        return render_template('remote.html', addr=server_addr, ip=ip, data=serverInfo, players=serverPlayers, rules=serverRules, quote=randomQuote())
    except StopIteration as e:
        e = "Unable to resolve server ip."
        return render_template('error.html', error=e)
    except socket.timeout as e:
        e = "Unable to resolve server ip."
        return render_template('error.html', error=e)
    except:
        e = "Unknown error."
        return render_template('error.html', error=e)


@app.route('/w/<string:ip>')
def widget(ip):
    try:
        server_addr = next(gs.query_master(r'\appid\581320\gameaddr\%s' % ip))
        serverInfo = gs.a2s_info(server_addr)
        serverRules = gs.a2s_rules(server_addr)
        serverPlayers = gs.a2s_players(server_addr)
        return render_template('widget.html', addr=server_addr, ip=ip, data=serverInfo, rules=serverRules, players=serverPlayers)
    except:
        e = "Unknown error."
        return render_template('widgeterror.html', error=e)


@app.route('/b/<string:ip>')
def banner(ip):
    try:
        server_addr = next(gs.query_master(r'\appid\581320\gameaddr\%s' % ip))
        serverInfo = gs.a2s_info(server_addr)
        serverRules = gs.a2s_rules(server_addr)
        serverPlayers = gs.a2s_players(server_addr)
        return render_template('banner.html', addr=server_addr, ip=ip, data=serverInfo, rules=serverRules, players=serverPlayers)
    except:
        e = "Unknown error."
        return render_template('bannererror.html', error=e)


@app.route('/rcon')
def rconinfo():
    try:
        return render_template('rcon.html', version=__version__)
    except StopIteration as e:
        return render_template('error.html', error=e)


@app.route('/rcon/<string:ip>')
def rcon(ip):
    try:
        if not request.cookies.get('rconpwd'):
            res = make_response("")
            res.set_cookie('rconpwd', 'NotSet', max_age=60 * 60)
        else:
            res = make_response("{}".format(request.cookies.get('rconpwd')))

        server_addr = next(gs.query_master(r'\appid\581320\gameaddr\%s' % ip))
        serverInfo = gs.a2s_info(server_addr)
        serverRules = gs.a2s_rules(server_addr)
        serverPlayers = gs.a2s_players(server_addr)
        return render_template('rcon.html', addr=server_addr[0], ip=ip, data=serverInfo, players=serverPlayers, rules=serverRules, quote=randomQuote(), maplist=mapList)
    except StopIteration as e:
        e = "Unable to resolve server ip."
        return render_template('error.html', error=e)
    except socket.timeout as e:
        e = "Unable to resolve server ip."
        return render_template('error.html', error=e)
    except:
        e = "Unknown error."
        return render_template('error.html', error=e)


@app.route('/rconengine', methods=['GET', 'POST'])
def rconengine():

    if request.method == 'POST':
        res = make_response("")
        if captcha.validate():
            # print(request.form)
            if request.form.get('rconpassword') or request.form.get('rconport'):
                res.set_cookie("rconpwd", request.form.get('rconpassword'), 60 * 60)
                res.set_cookie("rconport", request.form.get('rconport'), 60 * 60)
                flash(u'Updated rcon password.', 'success')
            if request.form.get('mapname'):
                try:
                    address = (request.form.get('ip'), int(request.cookies.get('rconport')))
                    password = request.cookies.get('rconpwd')
                    with valve.rcon.RCON(address, password) as rcon:
                        rcon.execute("say Switching scenario to " + request.form.get('mapname'), block=False, timeout=5)
                        time.sleep(5)
                        rcon.execute("travelscenario " + request.form.get('mapname'), block=False, timeout=5)
                        flash(u'Switching map to: ' + request.form.get('mapname'), 'success')
                except:
                    e = "Wrong password"
                    return render_template('error.html', error=e)
            if request.form.get('adminchat'):
                try:
                    address = (request.form.get('ip'), int(request.cookies.get('rconport')))
                    password = request.cookies.get('rconpwd')
                    with valve.rcon.RCON(address, password) as rcon:
                        rcon.execute("say " + request.form.get('adminchat'), block=False, timeout=5)
                        flash(u'Message send: ' + request.form.get('adminchat'), 'success')
                except:
                    e = "Wrong password"
                    return render_template('error.html', error=e)
            if request.form.get('gridRadios'):
                try:
                    address = (request.form.get('ip'), int(request.cookies.get('rconport')))
                    password = request.cookies.get('rconpwd')
                    with valve.rcon.RCON(address, password) as rcon:
                        if "kick" in request.form.get('gridRadios'):
                            rcon.execute("kick " + request.form.get('username') + " " + request.form.get('bkreason'), block=False, timeout=5)
                            flash(u'kicked ' + request.form.get('username'), 'success')
                        if "ban" in request.form.get('gridRadios'):
                            duration = request.form.get('gridRadios').split('ban')
                            rcon.execute("ban " + request.form.get('username') + " " + duration[1] + " " + request.form.get('bkreason'), block=False, timeout=5)
                            flash(u'Banned ' + request.form.get('username') + " for " + duration[1] + " minutes.", 'success')
                        if "PERMBAN" in request.form.get('gridRadios'):
                            rcon.execute("permban " + request.form.get('username') + " " + request.form.get('bkreason'), block=False, timeout=5)
                            flash(u'Permanently banned ' + request.form.get('username'), 'success')
                            # rcon.execute("say user " + request.form.get('username') + " will be " + request.form.get('gridRadios'), block=False, timeout=5)
                except:
                    e = "Wrong password"
                    return render_template('error.html', error=e)
            res.headers['location'] = url_for('rcon', ip=request.form['ip'])
            return res, 302
        else:
            flash(u'Wrong Captcha code', 'danger')
            res.headers['location'] = url_for('rcon', ip=request.form['ip'])
            return res, 302
    return render_template('rcon.html')


@app.route('/about')
def about():
    try:
        return render_template('about.html', version=__version__)
    except StopIteration as e:
        return render_template('error.html', error=e)

if __name__ == '__main__':
    app.run(debug=False, threaded=True, host='0.0.0.0', port=5000)
