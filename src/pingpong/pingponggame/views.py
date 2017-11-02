from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, Http404
from django.http import HttpResponse
#Import model for application
from pingponggame.models import *
#Import Django forms
from pingponggame.forms import *

# Registration Page
@transaction.atomic
def registration(request):
	context = {}

	#If get request, just display web page
	if request.method != 'POST':
		context['user_form'] = UserForm()
		context['password_form'] = PasswordForm()
		context['player_form'] = PlayerForm()
		return render(request, 'Registration.html', context)

	user_form = UserForm(request.POST)
	password_form = PasswordForm(request.POST)
	
	context['user_form'] = user_form
	context['password_form'] = password_form
	context['player_form'] = PlayerForm()

	if not user_form.is_valid() or \
		not password_form.is_valid():
		print (request.POST)
		return render(request, 'Registration.html', context)

	newuser = User.objects.create_user(username=request.POST['username'],
									   password=request.POST['password'],
									   first_name=request.POST['first_name'],
									   last_name=request.POST['last_name'])
	
	player_form = PlayerForm(request.POST, instance = newuser)
	player_form.save()

	return redirect('/pingpong/main')


# Render the usermainpage
@transaction.atomic
# @login_requireds
def usermainpage(request):
	context = {}
	return render(request, 'UserMainPage.html', context)

# Render the gameroom
def gameRoom(request):
	return render(request, 'GameRoom.html', {})
