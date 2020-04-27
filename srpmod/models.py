from django.db import models
from django.contrib.auth.models import User
from esi.models import Token

class SrpPaymentToken(models.Model):
    user = models.OneToOneField(User,
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='srp_character')
    token = models.ForeignKey(Token, on_delete=models.CASCADE)

    class Meta:
        permissions = (('view_global_srp_stats', 'Can View All SRP Stats'),
                       ('view_own_srp_stats', 'Can View Personal SRP Stats'))
