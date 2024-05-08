from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django_filters import CharFilter, BooleanFilter

from faker import Faker
from model_bakery import baker

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.serializers import ErrorDetail, ValidationError

from todo_api.models import Todo
from todo_api.filters import TodoFilter
from todo_api.serializers import TodoSerializer, TodoDeSerializer
from todo_api.views import TodoViewSet


User = get_user_model()
faker = Faker()

def init_baker(user, text=faker.text(), is_completed=True):
    return baker.make(
        Todo, 
        user=user,
        title=text,
        description=faker.paragraph(),
        is_completed=is_completed,
    )


class TestApi(APITestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client.force_authenticate(self.user)
        self.todo = baker.make("Todo", user=self.user)
    
    
    def test_list(self):
        url = '/todo_api/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    
    def test_create(self):
        url = '/todo_api/'
        data = {
            "title": faker.texts(),
            "description": faker.paragraph()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
    def test_update(self):
        url = f'/todo_api/{self.todo.id}/'
        data = {
            "title": faker.texts(),
            "description": faker.paragraph()
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_delete(self):
        url = f'/todo_api/{self.todo.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestView(APITestCase):
    def setUp(self):
        self.view = TodoViewSet
        self.factory = APIRequestFactory()
        self.user = baker.make(User)
        self.todo1 = init_baker(self.user, is_completed=True)
        self.todo2 = init_baker(self.user, is_completed=False)
        self.todo3 = init_baker(self.user, is_completed=True)
    
    
    def test_serializer(self):
        view = self.view()
        view.action = 'list'
        self.assertEqual(view.get_serializer_class(), TodoSerializer)
    
    
    def test_deserializer(self):
        view = self.view()
        view.action = 'post'
        self.assertEqual(view.get_serializer_class(), TodoDeSerializer)
    
    
    def test_queryset(self):
        view = self.view()
        request = self.factory.get('/')
        request.user = self.user
        view.request = request
        expected = [self.todo1.id, self.todo2.id, self.todo3.id]
        actual = view.get_queryset()
        
        self.assertQuerysetEqual(actual, expected, lambda item: item.id, ordered=False)
        
    
    def test_list(self):
        view = self.view.as_view({'get': 'list'})
        request = self.factory.get(reverse('todo_api-list'))
        force_authenticate(request, self.user)
        view.request = request
        response = view(request)
        
        self.assertEqual(len(response.data), 3)
        self.assertEqual(
            [self.todo1.id, self.todo2.id, self.todo3.id],
            [todo['id'] for todo in response.data]
        )
        
    
    def test_get(self):
        view = self.view.as_view({'get': 'retrieve'})
        request = self.factory.get(reverse('todo_api-detail', kwargs={'pk': self.todo1.pk}))
        force_authenticate(request, self.user)
        response = view(request, pk=self.todo1.pk)
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.data['id'], self.todo1.pk)


    def test_create(self):
        view = self.view.as_view({'post': 'create'})
        data = {
            "title": faker.text(),
            "description": faker.paragraph(),
            "is_completed": faker.boolean(),
        }
        
        request = self.factory.post(reverse('todo_api-list'), data=data)
        force_authenticate(request, self.user)
        view.request = request
        response = view(request)
        
        self.assertEqual(response.data['title'], data['title'])
        
    
    def test_update(self):
        _title = faker.text()
        _description = faker.paragraph()
        _status = faker.boolean()
        data = {
            "title": _title,
            "description": _description,
            "is_completed": _status,
        }
        view = self.view.as_view({'put': 'update'})
        request = self.factory.put(reverse('todo_api-detail', kwargs={'pk': self.todo1.pk}), data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.todo1.pk)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], _title)
        self.assertEqual(response.data['description'], _description)
        self.assertEqual(response.data['is_completed'], _status)
        

        def test_delete(self):
            view = self.view.as_view({'delete': 'destroy'})
            request = self.factory.delete(reverse('todo_api-detail', kwargs={'pk': self.todo1.pk}))
            force_authenticate(request, self.user)
            response = view(request, pk=self.todo1.pk)
            
            self.assertEqual(response.status_code, 204) 


class TestSerializer(APITestCase):
    def setUp(self):
        self.view = TodoViewSet
        self.factory = APIRequestFactory()
        self.user = baker.make(User)
        self.todo1 = init_baker(self.user, 'test 1', True)
        
        
    def test_serialize(self):
        expected_data = {
            'id': self.todo1.id,
            'title': self.todo1.title,
            'description': self.todo1.description,
            'is_completed': self.todo1.is_completed,
            'created_at': self.todo1.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'updated_at': self.todo1.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'user': self.todo1.user_id,
        }
        actual_data = TodoSerializer(instance=self.todo1).data
        self.assertDictEqual(expected_data, actual_data)
    
    
class TestDeserializer(APITestCase):
    def setUp(self):
        self.view = TodoViewSet
        self.factory = APIRequestFactory()
        self.user = baker.make(User)
        self.todo1 = init_baker(self.user, 'test 1', False)
        self.maxDiff = None
    
    
    def test_deserialize(self):
        title = faker.text()
        description = faker.paragraph()
        payload = {
            'user': self.user,
            'title': title,
            'description': description,
        }
        request = self.factory.post('/', payload)
        request.user = self.user
        context = {'request': request}
        deserialize = TodoDeSerializer(data=payload, context=context)
        
        try:
            deserialize.is_valid(raise_exception=True)
        except ValidationError:
            self.fail('Deserialization test failed')
        
        instance = deserialize.save()
        self.assertTrue(instance.id is not None)
        self.assertEqual(instance.title, title)
        self.assertEqual(instance.description, description)
        self.assertEqual(instance.is_completed, False)
        
    
    def test_validation(self):
        request = self.factory.post("/", {})
        request.user = self.user
        context = {'request': request}
        deserialize = TodoDeSerializer(data={}, context=context)
        with self.assertRaises(ValidationError) as validator:
            deserialize.is_valid(raise_exception=True)

        expected = validator.exception.detail
        actual = {
            'title': [ErrorDetail(string='This field is required.', code='required')]
        }
        self.assertEqual(expected, actual)


class TestFilterTodo(TestCase):
    def test_filter(self):
        self.user = baker.make(User)
        self.todo1 = init_baker(self.user, 'test 1', True)
        self.todo2 = init_baker(self.user, 'unteost 2', False)
        self.todo3 = init_baker(self.user, 'test 3', True)
        
        filter_data = {'title': 'test', 'is_completed': True}
        filter_set = TodoFilter(data=filter_data, queryset=Todo.objects.all())
        
        self.assertTrue(filter_set.is_valid())
        self.assertIsInstance(filter_set.filters['title'], CharFilter)
        self.assertIsInstance(filter_set.filters['is_completed'], BooleanFilter)
        self.assertEqual(filter_set.qs.count(), 2)