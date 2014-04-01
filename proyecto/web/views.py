
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import Context
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.shortcuts import render
from django import forms
from datetime import datetime
from django.template import Template, Context

import models
import MySQLdb
import json
import django.utils.simplejson as json




class ProjectForm(forms.Form):

	db = forms.CharField()
	host = forms.CharField()
	user = forms.CharField()
	password = forms.CharField()
	
	


def consultas(query):

	bd= MySQLdb.connect("localhost","root","root","geditdb")
	cursor = bd.cursor()
	cursor.execute(query)
	data = cursor.fetchall()	

	return data





def principal(request):
	
	flag = True
	project = ProjectForm()

	if(request.method == "GET"):
		comment = ""
	elif(request.method == "POST"):
		project = ProjectForm(request.POST)
		if project.is_valid():
			flag = False
			print "Is valid"
			db = project.cleaned_data['db']
			host = project.cleaned_data['host']
			user = project.cleaned_data['user']
			password = project.cleaned_data['password']
			datos = [host, user, password, db]
			return render_to_response('principal.html',
						{'flag':flag,'name_proj':db},
						context_instance=RequestContext(request))
		else:
			comment= "Debe rellenar todos los campos"			

	return render_to_response('principal.html',
						{'flag':flag,'project':project,'comment':comment},
						context_instance=RequestContext(request))





def people(request):

	if(request.method == "GET"):
		lista = ""
		personas = consultas("SELECT * FROM people")
		for registro in personas:
			ident = registro[0]
			nombre = registro[1]
			email = registro[2]
			lista+= '<p><a href="http://localhost:1234/'+nombre+'/'+str(ident)+'/">'+nombre+'</a><br>'
			pers = '<h4><a href="http://localhost:1234/'+nombre+'/'+str(ident)+'/">'+nombre+'</a>'+'&nbsp;&nbsp;'+email+'</h4>'
			lista += email+'</p>'+'<br>'

		lista = lista.decode('ascii','ignore')
		return render_to_response('people.html',
						{'info':lista},
						context_instance=RequestContext(request))
	


def person(request,nombre, ident):

	if(request.method == "GET"):
		info = ""
		numcommits = 0
		ident = ident.split("/")[0]
		data = consultas("SELECT date, message FROM scmlog WHERE author_id=" + str(ident))
		info += '<thead><tr><th>Date</th><th>Message</th></tr></thead><tbody>'
		for registro in data:
			numcommits += 1
			date = registro[0]
			x = date.strftime('%m/%d/%Y')
			if (numcommits%2 == 0):	
				info += '<tr><td>'+x+'</td><td>'+registro[1]+'</td></tr>'
			else:
				info += '<tr class="alt"><td>'+ x+'</td><td>'+registro[1]+'</td></tr>'
		info += '<tr><th>Commits:</th><td>'+str(numcommits)+'</td></tr></tbody>'


		return render_to_response('person.html',
						{'info':info,'nombre':nombre},
						context_instance=RequestContext(request))


def stats(request):

	if(request.method == "GET"):
		tabla = ""
		estadistica =""
		top_iden = "No hay commits"
		top_commits = 0

		total_commits = consultas("SELECT COUNT(*) FROM scmlog")[0][0]
		data = consultas("SELECT author_id, COUNT(*) FROM scmlog group by author_id")
		dif = consultas("SELECT COUNT(*) FROM scmlog WHERE author_id=committer_id")[0][0]

		tabla += '<thead><tr><th>Author name</th><th>Commits</th></tr></thead><tbody>'
		for registro in data:
			nombre = consultas("SELECT name FROM people WHERE id="+str(registro[0]))
			for x in nombre:
				name = x[0]
			tabla += '<tr><td>'+name+'</td><td>'+str(registro[1])+'</td></tr>'
			if(registro[1]>top_commits):
				top_commits = registro[1]
				top_iden = name
		
		cuenta = round((top_commits/float(total_commits))*100,2)
		authors = round((dif/float(total_commits))*100,2)

		estadistica += '<tbody>'
		estadistica += '<tr><td>Top Commiter</td><td>'+top_iden+"  ("+str(top_commits)+')</td></tr>'
		estadistica += '<tr><td>Porcentaje commits en el proyecto</td><td>'+str(cuenta)+'%</td></tr>'
		estadistica += '<tr><td>% Commiters que sean autores</td><td>'+str(authors)+'</td></tr>'
		tabla = tabla.decode('ascii','ignore')

		
		
		return render_to_response('stats.html',
						{'info':tabla,'stats':estadistica},
						context_instance=RequestContext(request))



def graphs(request):

	lista = []
	data = consultas("SELECT date FROM scmlog")

	for registro in data:
			date = registro[0]
			x = date.strftime('%Y/%m/%d')
			lista.append(x)
	lista.sort()
	
	meses = graphmonth(lista)
	anios = graphyears(lista)
	
	return render_to_response('/home/almudena/pfc/proyecto/proyecto/templates/graphs.html',meses)



def graphmonth(lista):

	datos = {'dates':[],'values':[]}	

	dia_aux= lista[0][0:7]
	datos['dates'].append(dia_aux)
	n = 0
	numcommits = 0
	for fecha in lista:
		fecha = fecha[0:7]
		if (fecha != dia_aux):
			datos['values'].append(numcommits)
			numcommits = 0
			datos['dates'].append(fecha)
			dia_aux = fecha
			
		numcommits +=1
	
	return datos

def graphyears(lista):

	datos = {'dates':[],'values':[]}	

	dia_aux= lista[0][0:4]
	datos['dates'].append(dia_aux)
	n = 0
	numcommits = 0
	for fecha in lista:
		fecha = fecha[0:4]
		if (fecha != dia_aux):
			datos['values'].append(numcommits)
			numcommits = 0
			datos['dates'].append(fecha)
			dia_aux = fecha
			
		numcommits +=1
	
	return datos


	
