from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotAllowed, HttpResponseBadRequest
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages

from google.appengine.api.labs import taskqueue

from eventsite import get_site, site_required

from forms import SubscribeForm



import logging

@site_required
def new_subscription(request):
    if request.method== 'POST':
        form=SubscribeForm(request.POST)
        if form.is_valid():
            chimp=request.site.chimp
            taskqueue.add(url='/subscriptions/subscribe_email/',
                           params={'apikey': chimp.apikey,
                           'list_id': chimp.listid,
                           'email': form.cleaned_data['email']})
            messages.add_message(request, messages.INFO, "Thank you for subscribing! Please check your email for a confirmation link.")
            return HttpResponseRedirect(reverse('front-page'))

            
    else:
        form=SubscribeForm()
    return(render_to_response('subscriptions/new.html', locals(), context_instance=RequestContext(request)))
    
@site_required
def manage_subscription(request, code=None):
    subscription=request.site.subscription_set.filter('manage_code =', code).get()
    if not subscription: raise Http404
    unsubscribe_form=UnsubscribeForm(initial={'manage_code': code})
    unsubscribe_action=reverse('unsubscribe')

    
    if request.method=='POST':
        form=ManageForm(request.POST)
        if form.is_valid():
            subscription.subscribes_weekly=form.cleaned_data['subscribes_weekly']
            subscription.subscribes_news=form.cleaned_data['subscribes_news']
            subscription.put()
            messages.add_message(request, messages.INFO,'Your subscription has been saved!')
            return HttpResponseRedirect(reverse('front-page'))
            
        else:
             return(render_to_response('subscriptions/manage.html', locals(), context_instance=RequestContext(request)))
    
    else:
        initial_data={'email':subscription.email,
        }

        return(render_to_response('subscriptions/manage.html', locals(), context_instance=RequestContext(request)))

@site_required
def unsubscribe(request):
    if request.method=='POST':
        form=UnsubscribeForm(request.POST)
        if form.is_valid():
            code=form.cleaned_data['manage_code']
            if form.cleaned_data['are_you_sure']== False:
                messages.add_message(request, messages.INFO,"""You didn't check the "Are you sure you want to unsubscribe?" box. """)
                return HttpResponseRedirect(reverse('manage_subscription',kwargs={'code':code }))
            subscription=request.site.subscription_set.filter('manage_code =', code).get()
            subscription.delete()
            messages.add_message(request, messages.INFO,'You have been unsubscribed')
            return HttpResponseRedirect(reverse('front-page'))
            
        else: 
            messages.add_message(request, messages.INFO,"""You didn't check the "Are you sure you want to unsubscribe?" box. """)
            return HttpResponseRedirect(reverse('manage_subscription',kwargs={'code':request.POST.get('manage_code', '') }))
            
    else:
        return HttpResponseNotAllowed(['POST',])
    



@site_required
def verify_subscription(request, code=None):
    subscription=request.site.subscription_set.filter('verify_code =', code).get()
    if not subscription: raise Http404
    if not subscription.verified_at:subscription.verify()
    messages.add_message(request, messages.INFO, "Thank you for verifying your subscription!")
    return HttpResponseRedirect(reverse('front-page'))
    
@site_required
def recover(request):
    
    if request.method=='POST':
        form = RecoveryForm(request.POST)
        if form.is_valid():
            
            subscription = request.site.subscription_set.filter('email =', form.cleaned_data['email']).get()
            subscription.send_manage_or_verify_link()
            messages.add_message(request, messages.INFO, "We've re-sent your verification or management link")
            return HttpResponseRedirect(reverse('front-page'))
        
    else:
        session=request.environ['beaker.session']
        if 'prepopulate_email' in session:
            form=RecoveryForm({'email':session['prepopulate_email']})
        else:
            form=RecoveryForm()
        
    return(render_to_response('subscriptions/recover.html', locals(), context_instance=RequestContext(request)))   
            
            

