import os
import firebase_admin
from firebase_admin import db
from flask import Flask, jsonify
from threading import Thread
from os.path import exists
from tinydb import TinyDB
from texco import Texco

app = Flask(__name__)
cred = firebase_admin.credentials.Certificate('./Config/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
	'databaseURL': 'https://texco-93c52-default-rtdb.firebaseio.com/'
})


@app.route('/apply', methods=['GET'])
def apply_job():
	try:
		Thread(target=Texco().init).start()

	except:
		return {'message': 'Error'}

	return {'message': 'Successful'}


@app.route('/file/<file_name>')
def get_job(file_name):
	try:
		return jsonify(TinyDB('./Database/{}.json'.format(file_name)).all())
	except:
		return jsonify([])


@app.route('/add', methods=['GET'])
def add_apply_data():

	applyData = TinyDB('./Database/members.json')
	try:
		ref = db.reference("/ApplyData")
		# data = ref.order_by_child("applyTo").get()
		data = ref.get()
		for key, value in data.items():
			applyData.insert(value)
	except:
		return {'message': 'Error'}

	return {'message': 'Successful'}


@app.route('/clear', methods=['GET'])
def clear_old_job():
	try:
		if exists('./Database/pdf.json'):
			os.remove('./Database/pdf.json')
		if exists('./Database/jobs.json'):
			os.remove('./Database/jobs.json')
		if exists('./Database/filteredJobs.json'):
			os.remove('./Database/filteredJobs.json')
		if exists('./Database/filteredMembers.json'):
			os.remove('./Database/filteredMembers.json')
		if exists('./Database/clientId.json'):
			os.remove('./Database/clientId.json')
		if exists('./Database/members.json'):
			os.remove('./Database/members.json')

	except:
		return {'message': 'Error Occurred'}

	return {'message': 'Successful'}


if __name__ == '__main__':
	# clear_old_job()
	# add_apply_data()
	# apply_job()
	app.run(port=5000)
# be87f6001d4e5d87320a4b5c76ad4f33