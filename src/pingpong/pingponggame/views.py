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
	if request.method == 'GET':
		context['registration_form'] = RegistrationForm()
		context['user_form'] = UserForm()
		context['password_form'] = PasswordForm()
		return render(request, 'Registration.html', context)

	print ('111111111111')
	user_form = UserForm(request.POST)
	context['user_form'] = user_form

	if not user_form.is_valid():
		context['user_form'] = UserForm()
		context['password_form'] = PasswordForm()
		context['registration_form'] = RegistrationForm()
		return render(request, 'Registration.html', context)

	password_form = PasswordForm(request.POST)
	context['password_form'] = password_form
	print ('aaaaaaaaaaaaaaa')
	if not password_form.is_valid():
		context['password_form'] = PasswordForm()
		context['registration_form'] = RegistrationForm()
		context['user_form'] = UserForm()
		return render(request, 'Registration.html', context)

	#If user form is valid, create new user
	newuser = user_form.save()
	newuser.set_password(request.POST['password'])
	print (request.POST['password'])
	newuser.save()

	print ('2222222222222')
	registration_form = RegistrationForm(request.POST)
	context['registration_form'] = registration_form
	if not registration_form.is_valid():
		context['registration_form'] = RegistrationForm()
		context['user_form'] = UserForm()
		context['password_form'] = PasswordForm()
		return render(request, 'Registration.html', context)
	registration = registration_form.save()
	print ('3333333333333')
	#Get player object and give user to it
	# playerobj = get_object_or_404(Player, )
	print (registration.id)
	print (newuser.username)
	registration.user = newuser
	registration.save()
	print ('444444444444')

	# return render(request, 'Registration.html', context)
	return redirect('/pingpong/main')


# Render the usermainpage
@transaction.atomic
@login_required
def usermainpage(request):
	context = {}
	return render(request, 'UserMainPage.html', context)

# Render the gameroom
def gameRoom(request):
	return render(request, 'GameRoom.html', {})
