from flask import Flask, jsonify, request, abort, url_for, redirect
from flask_httpauth import HTTPBasicAuth 
from gestorMontura import gestorMontura
import time
from threading import Thread, Timer
from gestorColas import gestorColas

# Url del servidor
url = '/api/mount/montegancedo/'

#app.config["JSON_SORT_KEYS"] = False
gm = gestorMontura()
app = Flask(__name__)
gm.revisarTareas()

#Iniciar la cola
cola = gestorColas()
cola.setMontura(gm.m)
thCola = Thread(target=cola.iniciarCola)
thCola.start()

gm.m.setCola(cola)

auth = HTTPBasicAuth()
@auth.get_password
def get_password(username):
    if username == 'montura':
        return 'meade'
    return None

@app.route('/')
def pag_principal():
	return redirect(url, code = 302)

@app.route(url)
def pag_principal2():
    return 'Pagina principal de la montura del telescopio'


@app.route(url+'estado', methods = ['GET'])
@auth.login_required
def get_status():
        return jsonify(gm.getStatus()),201

@app.route(url+'tasks', methods = ['GET'])
@auth.login_required
def get_tasks():
	return jsonify(gm.getTareas()), 201

@app.route(url+'tasks', methods = ['POST'])
@auth.login_required
def create_tasks():
	#if not request.json or not 'orden' in request.json:
	#	abort(400)
	tasks = gm.getTareas()
	task = {
                'orden' : request.json['orden'],
		'done' : False
	}
	task['id'] = tasks[-1]['id']+1 if len(tasks)>0 else 1

	task['fechaInicio'] = time.strftime("%d/%m/%y")
        task['horaInicio'] = time.strftime("%H:%M:%S")
	gm.insertTarea(task)
	gm.revisarTareas()
	return jsonify({'task': task}), 201	

@app.route(url+'tasks/<int:task_id>', methods = ['GET'])
@auth.login_required
def get_task(task_id):
	task = gm.getTarea(task_id)
	if len(task) == 0:
		abort(404)
	return jsonify({'task': task[0]})


if __name__ == '__main__':
    app.run(host = 'localhost', debug = True, use_reloader=False)
