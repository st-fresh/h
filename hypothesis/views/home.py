from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from .. assets import site_styles
from .. models.auth import LoginForm, RegisterForm

import json

@view_config(route_name='home', renderer='home.jinja2')
def home_view(request):
    site_styles.need()

    if request.user is None:
        action = request.params.get('action', 'login')
        print action

        form = None
        form_kwargs = {
            'action': '/auth/' + action,
            'template': 'apex:templates/forms/fieldsetform.mako'
        }

        if action == 'login':
            form = LoginForm().render(submit_text='Sign In', **form_kwargs)
        elif action == 'register':
            print 'yep'
            form = RegisterForm().render(submit_text='Register', **form_kwargs)
        print form
        return {
            'action': action,
            'form': form
        }
    else:
        return {}
