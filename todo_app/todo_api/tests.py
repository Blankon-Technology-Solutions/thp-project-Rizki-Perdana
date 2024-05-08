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

def init_baker(user, text, is_completed):
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