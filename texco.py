from ip_address import getIpAddress
from tinydb import TinyDB, where
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime
from threading import Thread
from os.path import exists
import requests
import queue
import time
import os

load_dotenv()


class Texco:

	def __init__(self):

		self.apiToken = os.getenv('API_TOKEN')
		self.accountSID = os.getenv('ACCOUNT_SID')
		self.authToken = os.getenv('AUTH_TOKEN')

		self.client = Client(self.accountSID, self.authToken)
		self.header = {'Authorization': self.apiToken}
		self.clientIdQueue = queue.Queue()

		self.filteredMembers = []
		self.filteredJobs = []
		self.requests = requests.Session()

		self.clientIdDb = TinyDB('./Database/clientId.json')
		self.membersDb = TinyDB('./Database/members.json')
		self.pdfDb = TinyDB('./Database/pdf.json')
		try:
			os.remove('./Database/filteredMembers.json')
			os.remove('./Database/filteredJobs.json')
		except:
			pass
		self.filteredMembersDb = TinyDB('./Database/filteredMembers.json')
		self.filteredJobsDb = TinyDB('./Database/filteredJobs.json')

		self.JobListLink = 'https://livebackend.texco.in/api/job/list'
		self.JobClientId = 'https://livebackend.texco.in/api/job/jobposting/detail?jobpostingdetailid={}'
		self.JobApplyLink = 'https://livebackend.texco.in/api/job/jobactivityapply'

	def init(self):
		Thread(target=self.process_job_list).start()
		for i in range(10):
			Thread(target=self.get_job_list, args=('From Thread => {}'.format(i),)).start()
			time.sleep(6)

	def get_client_id(self, job, member, queue):

		# 'jobpostingdetailid': job['jobpostingdetailid'],
		date = datetime.now()
		data = {
			'memberid': member['memberId'],
			'projectid': job['projectid'],
			'code': member['code'],
			'currentvacancies': job['totalvacancies'],
			'texcono': member['texSerNo'],
			'ipaddress': getIpAddress(),
			'ocxetd': date.strftime("%Y/%m/%d %H:%M:%S")
		}

		# try:
		# 	response = self.clientIdDb.get(where('projectno') == job['projectno'])
		# 	data['clientid'] = response['clientid']
		# 	data['jobpostingdetailid'] = response['jobpostingdetailid']
		# 	return queue.put(data)
		# except:
		# 	pass

		while True:
			try:
				response = self.requests.get(self.JobClientId.format(job['jobpostingdetailid']), headers=self.header).json()
				data['clientid'] = response['clientid']
				data['jobpostingdetailid'] = response['jobpostingdetailid']
				# try:
				# 	self.clientIdDb.insert(response)
				# except:
				# 	pass
				return queue.put(data)
			except:
				continue

	def process_job_list(self):

		while True:
			if exists('./Database/jobs.json'):
				break

		jobs_db = TinyDB('./Database/jobs.json')
		for member in self.membersDb.all():
			member_job = jobs_db.search(
				(where(member['applyBy']) == member['applyTo']) & (where('code') == member['code']))
			if len(member_job) != 0:
				self.filteredMembers.append(member)
				for jobs in member_job:
					if jobs not in self.filteredJobs:
						self.filteredJobs.append(jobs)

		self.filteredMembersDb.insert_multiple(self.filteredMembers)
		self.filteredJobsDb.insert_multiple(self.filteredJobs)

		for member in self.filteredMembersDb.all():
			jobs = self.filteredJobsDb.search(
				(where(member['applyBy']) == member['applyTo']) & (where('code') == member['code']) & (where('numberofvacancies') != 0))
			for job in jobs:
				if job[member["applyBy"]] == member["applyTo"] and self.is_job_applicable(job, member) and job[
					'numberofvacancies'] != 0:
					print("{} => Applying Job".format(member["texSerNo"]))
					Thread(target=self.apply_job, args=(job, member,)).start()
					self.filteredJobsDb.update({'numberofvacancies': int(job['numberofvacancies']) - 1},
					                           where('jobpostingdetailid') == job['jobpostingdetailid'])
					break

	@staticmethod
	def is_job_applicable(job, member):
		# print(member)
		if member["notApply"]:
			not_apply_to = job[member["notApplyBy"]]
			if member["notApplyTo"] == not_apply_to:
				return False
			else:
				return True
		else:
			return True

	def get_job_list(self, thread_name):

		iteration = 0
		while True:

			iteration += 1
			if exists('./Database/jobs.json'):
				break

			print("{} => {}".format(thread_name, iteration))

			try:
				response = self.requests.get(self.JobListLink, headers=self.header).json()
				print(len(response))
				if len(response) > 0:
					print(
						'JobList Loaded From the Server of Length => {}'.format(
							len(response)
						)
					)
					if not exists('./Database/jobs.json'):
						jobs = []
						for project in response:
							for job in project['jobs']:
								if job['numberofvacancies'] != 0:
									job['jobpostingid'] = project['jobpostingid']
									job['totalvacancies'] = job['numberofvacancies']
									job['projectid'] = project['projectid']
									job['wagetype'] = project['wagetype']
									job['projectno'] = project['projectno']
									job['projectname'] = project['projectname']
									job['districtid'] = project['districtid']
									job['district'] = project['district']
									job['regionid'] = project['regionid']
									job['region'] = project['region']
									jobs.append(job)
						TinyDB('./Database/jobs.json').insert_multiple(jobs)
					break
			except:
				continue

	def apply_job(self, job, member):

		Thread(target=self.get_client_id,
		       args=(job, member, self.clientIdQueue)).start()
		payload = self.clientIdQueue.get()
		response = self.requests.post(self.JobApplyLink, data=payload, headers=self.header)

		if response.status_code == 200:
			try:
				print(member)
				print(response.json())
				message_body = "Name :- {}\nTexco Number :- {}\nPDF Link :- https://www.texco.in/member/printjob?jobactivityid={}&memberid={}".format(
					member["name"], member["texSerNo"], response.json()[0]["jobactivityid"], member["memberId"])
				print(message_body)
				try:
					message = self.client.messages.create(
						from_='whatsapp:+14155238886',
						body=message_body,
						to='whatsapp:+919629799459'
					)
					self.pdfDb.insert({payload["texcono"]: message_body})
				except:
					pass
			except:
				print("{} => You're Successfully applied the Job.".format(
					payload["texcono"]))
				pass

		elif response.status_code == 400:
			try:
				print("{} => {}".format(payload["texcono"], response.text))
			except:
				print("{} => You already applied the job.".format(
					payload["texcono"]))
				pass

		else:
			try:
				print("{} => {}".format(payload["texcono"], response.text))
			except:
				print("{} => Some Error occured in applying Job.".format(
					payload["texcono"]))
				pass
			self.apply_job(payload, member)
