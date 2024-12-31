from django.test import TestCase,Client
from django.urls import resolve,reverse
from budget.models import Project,Category,Expense
import json


class TestView(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.list_url = reverse('list')
        self.detail_url = reverse('detail',args=['project1'])
        self.detail_url1  = reverse('detail',args=['project3'])
        self.add_url = reverse('add')
        self.project1 = Project.objects.create(
            name = 'project1',
            budget = 10000
        )
        
        self.project3 = Project.objects.create(
            name = 'project3',
            budget = 8000
        )
    
    def test_project_list_GET(self):
        
        response = self.client.get(self.list_url)
        
        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response,'budget/project-list.html')
        
    def test_project_detail_GET(self):
        response = self.client.get(self.detail_url)
        
        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response,'budget/project-detail.html')
        
    
    def test_project_detail_POST_adds_new_expense(self):
        Category.objects.create(
            project=self.project1,
            name ='design'
        )
        Category.objects.create(
            project=self.project1,
            name ='development'
        )
        
        response = self.client.post(self.detail_url,{
            "title":"expense1",
            "amount":1000,
            "category":"design"
        }
        )
        
        response2 = self.client.post(self.detail_url,{
            "title":"expense2",
            "amount":1000,
            "category":"development"
        }
        )
        
        Category.objects.create(
            project = self.project3,
            name = 'management'
        )
        
        response1 = self.client.post(self.detail_url1,{
            "title":"expense1",
            "amount":1000,
            "category":"management"
            })
        
        self.assertEquals(response.status_code,302)
        self.assertEquals(self.project1.expenses.first().title,'expense1')
        self.assertEquals(response2.status_code,302)
        self.assertEquals(self.project1.expenses.all()[1].title,'expense2')
        self.assertEquals(response1.status_code,302)
        self.assertEquals(self.project3.expenses.first().title,'expense1')
    
    def test_project_detail_POST_no_data(self):
        response = self.client.post(self.detail_url)
        
        self.assertEquals(response.status_code,302)
        self.assertEquals(self.project1.expenses.count(),0)
        
    def test_project_detail_DELETE_deletes_expenses(self):
        category1 = Category.objects.create(
            project = self.project1,
            name = 'development'
        )
        
        Expense.objects.create(
            project=self.project1,
            title = 'expense1',
            amount = 1000,
            category = category1
        )
        
        category2 = Category.objects.create(
            project = self.project3,
            name = 'development'
        )
        
        Expense.objects.create(
            project=self.project3,
            title = 'expense2',
            amount = 500,
            category = category2
        )
        
        response = self.client.delete(self.detail_url,json.dumps({
            "id" : 1
        }))
        
        response = self.client.delete(self.detail_url1,json.dumps({
            "id" : 2
        }))
        
        self.assertEquals(response.status_code,204)
        self.assertEquals(self.project1.expenses.count(),0)
        self.assertEquals(self.project3.expenses.count(),0)
    
    def test_project_detail_DELETE_no_id(self):
        category1 = Category.objects.create(
            project = self.project1,
            name = 'development'
        )
        
        Expense.objects.create(
            project=self.project1,
            title = 'expense1',
            amount = 1000,
            category = category1
        )
        
        response = self.client.delete(self.detail_url)
        
        self.assertEquals(response.status_code,404)
        self.assertEquals(self.project1.expenses.count(),1)
        
    def test_project_create_POST(self):
        response = self.client.post(self.add_url,{
            'name':'project2',
            'budget' : 10000,
            'categoriesString' : 'design,development' 
        })
        
        project2 = Project.objects.get(id=3)
        self.assertEquals(project2.name,'project2')
        first_category = Category.objects.get(id=1)
        self.assertEquals(first_category.project,project2)
        self.assertEquals(first_category.name , 'design')
        second_category = Category.objects.get(id=2)
        self.assertEquals(second_category.project, project2)
        self.assertEquals(second_category.name , 'development')
        