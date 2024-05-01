from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Question, Choice, Material, Topic
from django_summernote.widgets import SummernoteWidget

class CreateQuizForm(forms.Form):
    quiz_name = forms.CharField(max_length=50, label="Название", widget=forms.TextInput(attrs={'class': 'form-input form-control item'}))
    quiz_description = forms.CharField(max_length=50, label="Описание (необязательно)", widget=forms.TextInput(attrs={'class': 'form-input form-control item'}))
    material = forms.ModelChoiceField(label="Материалы", queryset=Material.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-input form-control item'}))
    topic = forms.ModelChoiceField(label="Тема", queryset=Topic.objects.all().order_by("topic_name"), widget=forms.Select(attrs={'class': 'form-input form-control item'}))

class SingleQuestionForm(forms.Form):
    def __init__(self, q_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = {}
        question_id = q_id
        choises = Question.objects.get(id=question_id).choice_set.all()
        for i, choise in enumerate(choises):
            self.fields[f"choise_{i+1}"] = forms.BooleanField(required=False, label=choise.text, widget=forms.CheckboxInput(attrs={'class': 'form-check', "id": f"choise_{i+1}"}))
            self.fields[f"choise_{i+1}"].label = choise.text
    def checkbox_label(self, checkbox):
        return self.fields[checkbox].text

class CreateQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['timeout', 'question_text']
        widgets = {'question_text': SummernoteWidget(attrs={'class': 'form-control item'}), "name": forms.TextInput(attrs={'class': 'form-input form-control item', 'width': 'auto', 'height': 'auto'})}

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'text']
        widgets = {'text': SummernoteWidget(attrs={'class': 'form-control item'}), "name": forms.TextInput(attrs={'class': 'form-input form-control item', 'width': 'auto', 'height': 'auto', 'min': 0})}