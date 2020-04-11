import logging
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from esi.decorators import token_required
from allianceauth.authentication.decorators import permissions_required
from allianceauth.eveonline.providers import provider
from allianceauth.notifications import notify
from allianceauth.srp.form import SrpFleetMainForm
from allianceauth.srp.form import SrpFleetMainUpdateForm
from allianceauth.srp.form import SrpFleetUserRequestForm
from allianceauth.srp.models import SrpFleetMain
from allianceauth.srp.models import SrpUserRequest
from allianceauth.srp.managers import SRPManager
from .models import SrpPaymentToken
logger = logging.getLogger(__name__)

from . import providers

@login_required
@permission_required('srp.access_srp')
def srp_fleet_view(request, fleet_id):
    logger.debug("srp_fleet_view called by user %s for fleet id %s" % (request.user, fleet_id))
    try:
        fleet_main = SrpFleetMain.objects.get(id=fleet_id)
    except SrpFleetMain.DoesNotExist:
        raise Http404
    context = {"fleet_id": fleet_id, "fleet_status": fleet_main.fleet_srp_status,
               "srpfleetrequests": fleet_main.srpuserrequest_set.select_related('character').order_by('srp_ship_name'),
               "totalcost": fleet_main.total_cost}

    return render(request, 'srpmod/data.html', context=context)


@login_required
@permission_required('auth.srp_management')
@token_required(['esi-ui.open_window.v1', 'esi-location.read_online.v1'])
def srp_set_payment_character(request, token, fleet_id=None):
    if token:
        srp_link = False
        try:
            srp_link = SrpPaymentToken.objects.get(user=request.user)
        except:
            pass
        if srp_link:
            srp_link.token = token
            srp_link.save()
        else:
            SrpPaymentToken.objects.create(user=request.user, token=token)
    messages.success(request,
                    _("Linked SRP Payments Character: {}".format(token.character_name)))
    if fleet_id:
        return redirect("srp:fleet", fleet_id)
    else:
        return redirect("srp:management")


@login_required
@permission_required('auth.srp_management')
def srp_open_info(request, id=None):
    try:
        if id:
            linked = request.user.srp_character
            if linked:
                online = providers.provider.client.Location.get_characters_character_id_online(character_id=linked.token.character_id, _request_options=providers.get_operation_auth_headers(linked.token)).result()
                if online.get('online', False):
                    providers.provider.client.User_Interface.post_ui_openwindow_information(target_id=id, _request_options=providers.get_operation_auth_headers(linked.token)).result()

        return HttpResponse("Success!")
    except:
        return HttpResponse("Failed!")


@login_required
@permission_required('srp.access_srp')
def srp_management(request, all=False):
    logger.debug("srp_management called by user %s" % request.user)
    fleets = SrpFleetMain.objects.select_related('fleet_commander').prefetch_related('srpuserrequest_set').all()
    if not all:
        fleets = fleets.filter(fleet_srp_status="")
    else:
        logger.debug("Returning all SRP requests")
    totalcost = fleets.aggregate(total_cost=Sum('srpuserrequest__srp_total_amount')).get('total_cost', 0)
    context = {"srpfleets": fleets, "totalcost": totalcost}
    return render(request, 'srpmod/management.html', context=context)
