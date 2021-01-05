from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods


class PostProcTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)

    def tearDown(self):
        self.client = None

    def test_identity(self):
        data = {
            'type': 'IDENTITY',
            'options': [
                { 'option': 'Option 1', 'number': 1, 'votes': 5 },
                { 'option': 'Option 2', 'number': 2, 'votes': 0 },
                { 'option': 'Option 3', 'number': 3, 'votes': 3 },
                { 'option': 'Option 4', 'number': 4, 'votes': 2 },
                { 'option': 'Option 5', 'number': 5, 'votes': 5 },
                { 'option': 'Option 6', 'number': 6, 'votes': 1 },
            ]
        }

        expected_result = [
            { 'option': 'Option 1', 'number': 1, 'votes': 5, 'postproc': 5 },
            { 'option': 'Option 5', 'number': 5, 'votes': 5, 'postproc': 5 },
            { 'option': 'Option 3', 'number': 3, 'votes': 3, 'postproc': 3 },
            { 'option': 'Option 4', 'number': 4, 'votes': 2, 'postproc': 2 },
            { 'option': 'Option 6', 'number': 6, 'votes': 1, 'postproc': 1 },
            { 'option': 'Option 2', 'number': 2, 'votes': 0, 'postproc': 0 },
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def testNoParidad(self):
        data = {
            'type': 'PARIDAD',
            'options': [
                { 'option': 'Partido rojo', 'number': 1, 'votes': 120 , 'postproc': 4, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'hombre','id':'4'}
                ]},
                { 'option': 'Partido azul', 'number': 2, 'votes': 89, 'postproc': 3, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'mujer','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ]},
                { 'option': 'Partido naranja', 'number': 3, 'votes': 10, 'postproc': 2, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ]},
                { 'option': 'Partido morado', 'number': 5, 'votes': 26, 'postproc': 1, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ]},
            ]
        }

        expected_result = {'message' : 'No se cumplen los ratios de paridad 60%-40%'}

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)