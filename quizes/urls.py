from django.urls import path

from . import views


app_name = 'quiz'
urlpatterns = [
    path('', views.index, name='index'),

    path('search', views.search, name='search'),
    
    path('<int:quiz_id>/', views.single_quiz, name='single_quiz'),

    path('<int:quiz_id>/<int:question_id>/', views.single_question, name='single_question'),

    path('<int:quiz_id>/results/', views.results, name='results'),

    path('create/', views.create_quiz, name='create_quiz'),

    path('create/<int:quiz_id>/<int:question_id>/', views.create_question, name='create_question'),

    path('edit/<int:quiz_id>/<int:question_id>/', views.edit_question, name='edit_question'),
    
    path('delete/<int:quiz_id>/<int:question_id>/', views.delete_question, name='delete_question'),

    path("material/create", views.create_material, name="create_material"),

    path('material/<int:mat_id>/', views.single_material, name='single_material'),
]