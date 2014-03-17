from django.db import models

class TurboMillLocation(models.Model):
    description = models.CharField(max_length=100)
    install_id = models.CharField(max_length=200)

    def __unicode__(self):
        return self.description

class TurboMillSample(models.Model):
    location = models.ForeignKey(TurboMillLocation, related_name='samples')
    time_stamp = models.DateTimeField()
    joules = models.FloatField()
    watts_avg = models.FloatField()
    volts_avg = models.FloatField()
    volts_peak = models.FloatField()
    volts_min = models.FloatField()
    amps_avg = models.FloatField()
    amps_peak = models.FloatField()
    speed_avg = models.FloatField()
    speed_peak = models.FloatField()
    dir_mag = models.FloatField()
    dir_ang = models.FloatField()
    dir_cos = models.FloatField()

    class Meta:
        ordering = [ '-time_stamp' ]

    def __unicode__(self):
        return str(self.time_stamp)
