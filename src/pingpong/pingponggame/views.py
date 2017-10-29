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

	return render(request, 'Registration.html', context)
