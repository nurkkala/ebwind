from django.contrib import admin

from .models import *

class TurboMillSampleAdmin(admin.ModelAdmin):
    model = TurboMillSample
    list_filter = ( 'location', )

admin.site.register(TurboMillSample, TurboMillSampleAdmin)
admin.site.register(TurboMillLocation)
