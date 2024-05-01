from django.db import models
from jsonfield import JSONField

class Topic(models.Model):
    topic_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.topic_name

class Quiz(models.Model):
    quiz_title = models.CharField(max_length=300)
    quiz_description = models.CharField(null=True, blank=True, max_length=3000, verbose_name="quiz_description")
    user_creator = JSONField(max_length=2000, verbose_name="user_creator")
    num_questions = models.IntegerField(default=0, blank=True, null=True)
    material = models.IntegerField(null=True, blank=True)
    topic = models.CharField(max_length=150)

    def __str__(self):
        return self.quiz_title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    question_text = models.CharField(max_length=30000000)
    timeout = models.IntegerField(default=0)
    question_num = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(blank=False, max_length=500)
    correct_choise = models.BooleanField(default=False)

class Material(models.Model):
    name = models.CharField(blank=False, max_length=300000)
    text = models.CharField(null=True, blank=True, max_length=300000)

    def __str__(self):
        return self.name