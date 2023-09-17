from django.db import models


# Create your models here.
class Conversation(models.Model):
    date_started = models.DateField()
    title = models.CharField()

    def __str__(self):
        return self.title

    def __len__(self):
        return self.message_set.count()


class Message(models.Model):
    text = models.TextField()
    time_sent = models.DateTimeField()
    role = models.CharField()
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def __len__(self):
        return len(self.text)
