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
                {'option': 'Option 1', 'number': 1, 'votes': 5},
                {'option': 'Option 2', 'number': 2, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'votes': 3},
                {'option': 'Option 4', 'number': 4, 'votes': 2},
                {'option': 'Option 5', 'number': 5, 'votes': 5},
                {'option': 'Option 6', 'number': 6, 'votes': 1},
            ]
        }

        expected_result = [
            {'option': 'Option 1', 'number': 1, 'votes': 5, 'postproc': 5},
            {'option': 'Option 5', 'number': 5, 'votes': 5, 'postproc': 5},
            {'option': 'Option 3', 'number': 3, 'votes': 3, 'postproc': 3},
            {'option': 'Option 4', 'number': 4, 'votes': 2, 'postproc': 2},
            {'option': 'Option 6', 'number': 6, 'votes': 1, 'postproc': 1},
            {'option': 'Option 2', 'number': 2, 'votes': 0, 'postproc': 0},
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def testNoParidad(self):
        """
            * Definicion: Test negativo para verificar que no acepta una votacion que no cumple paridad
            * Entrada: Votacion
                - Option: Nombre del partido
                - Number: Id de la opcion
                - Votes: Numero de votos de esa votacion
                - PostProc: Numero de personas que van a ir en la lista una vez aplicada la paridad
                - Candidatos: Sexo e ID de los candidatos
            * Salida: Codigo 200 con mensaje de que no se cumple la paridad
        """
        data = {
            'type': 'PARIDAD',
            'options': [
                {'option': 'Partido rojo', 'number': 1, 'votes': 120, 'postproc': 4, 'candidatos': [
                 {'sexo': 'hombre', 'id': '1'}, {'sexo': 'hombre', 'id': '2'}, {
                     'sexo': 'hombre', 'id': '3'}, {'sexo': 'hombre', 'id': '4'}
                 ]},
                {'option': 'Partido azul', 'number': 2, 'votes': 89, 'postproc': 3, 'candidatos': [
                 {'sexo': 'hombre', 'id': '1'}, {'sexo': 'mujer', 'id': '2'}, {
                     'sexo': 'mujer', 'id': '3'}, {'sexo': 'mujer', 'id': '4'}
                 ]},
                {'option': 'Partido naranja', 'number': 3, 'votes': 10, 'postproc': 2, 'candidatos': [
                 {'sexo': 'hombre', 'id': '1'}, {'sexo': 'mujer', 'id': '2'}, {
                     'sexo': 'hombre', 'id': '3'}, {'sexo': 'mujer', 'id': '4'}
                 ]},
                {'option': 'Partido morado', 'number': 4, 'votes': 26, 'postproc': 1, 'candidatos': [
                 {'sexo': 'hombre', 'id': '1'}, {'sexo': 'mujer', 'id': '2'}, {
                     'sexo': 'hombre', 'id': '3'}, {'sexo': 'mujer', 'id': '4'}
                 ]},
            ]
        }

        expected_result = {
            'message': 'No se cumplen los ratios de paridad 60%-40%'}

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def testParidadFalla(self):
        """
            * Definicion: Test negativo por poner mal la URL
            * Entrada: Votacion (Json)
                - Option: Nombre del partido
                - Number: Id de la opcion
                - Votes: Numero de votos de esa votacion
                - PostProc: Numero de personas que van a ir en la lista una vez aplicada la paridad
                - Candidatos: Sexo e ID de los candidatos
            * Salida: Codigo 404
        """
        data = {
            'type': 'PARIDAD',
            'options': [
                {'option': 'Partido Unico', 'number': 1, 'votes': 5, 'postproc': 5, 'candidatos': [
                 {'sexo': 'hombre', 'id': '1'}, {'sexo': 'mujer', 'id': '2'}, {
                     'sexo': 'hombre', 'id': '3'}, {'sexo': 'mujer', 'id': '4'}, {'sexo': 'mujer', 'id': '5'}
                 ]}
            ]
        }

        response = self.client.post('/postproci/', data, format='json')
        self.assertEqual(response.status_code, 404)

    def testParidadBien(self):
        """
            * Definicion: Test positivo para una votacion que cumple la paridad
            * Entrada: Votacion (Json)
                - Option: Nombre del partido
                - Number: Id de la opcion
                - Votes: Numero de votos de esa votacion
                - PostProc: Numero de personas que van a ir en la lista una vez aplicada la paridad
                - Candidatos: Sexo e ID de los candidatos
            * Salida: Codigo 200 y json de la paridad
        """
        data = {
            'type': 'PARIDAD',
            'options': [
                {'option': 'Partido Unico', 'number': 1, 'votes': 5, 'postproc': 5, 'candidatos': [
                 {'sexo': 'hombre', 'id': '1'}, {'sexo': 'mujer', 'id': '2'}, {
                     'sexo': 'hombre', 'id': '3'}, {'sexo': 'mujer', 'id': '4'}, {'sexo': 'mujer', 'id': '5'}
                 ]}

            ]
        }

        expected_result = [
            {'option': 'Partido Unico', 'number': 1, 'votes': 5, 'postproc': 5, 'candidatos': [
                {'sexo': 'hombre', 'id': '1'}, {'sexo': 'mujer', 'id': '2'}, {
                    'sexo': 'hombre', 'id': '3'}, {'sexo': 'mujer', 'id': '4'}, {'sexo': 'mujer', 'id': '5'}
            ],
                'paridad': [
                {'sexo': 'mujer', 'id': '2'}, {'sexo': 'hombre', 'id': '1'}, {
                    'sexo': 'mujer', 'id': '4'}, {'sexo': 'hombre', 'id': '3'}, {'sexo': 'mujer', 'id': '5'}
            ]}
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def testParidad1Elemento(self):
        """
            * Definicion: Test positivo con solo un candidato de todos los posibles
            * Entrada: Votacion (Json)
                - Option: Nombre del partido
                - Number: Id de la opcion
                - Votes: Numero de votos de esa votacion
                - PostProc: Numero de personas que van a ir en la lista una vez aplicada la paridad
                - Candidatos: Sexo e ID de los candidatos
            * Salida: Codigo 200 y json de la paridad
        """
        data = {
            'type': 'PARIDAD',
            'options': [
                {'option': 'Partido Unico', 'number': 1, 'votes': 5, 'postproc': 1, 'candidatos': [
                 {'sexo': 'hombre', 'id': '1'}, {'sexo': 'mujer', 'id': '2'}, {
                     'sexo': 'hombre', 'id': '3'}, {'sexo': 'mujer', 'id': '4'}, {'sexo': 'mujer', 'id': '5'}
                 ]}
            ]
        }

        expected_result = [
            {'option': 'Partido Unico', 'number': 1, 'votes': 5, 'postproc': 1, 'candidatos': [
                {'sexo': 'hombre', 'id': '1'}, {'sexo': 'mujer', 'id': '2'}, {
                    'sexo': 'hombre', 'id': '3'}, {'sexo': 'mujer', 'id': '4'}, {'sexo': 'mujer', 'id': '5'}
            ],
                'paridad': [
                {'sexo': 'mujer', 'id': '2'}
            ]}
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_SainteLague1(self):
        data = {
            'type': 'SAINTE',
            'seats': 12,
            'options': [
                {'option': 'Partido 1', 'number': 1, 'votes': 50},
                {'option': 'Partido 2', 'number': 2, 'votes': 10},
                {'option': 'Partido 3', 'number': 3, 'votes': 34},
                {'option': 'Partido 4', 'number': 4, 'votes': 25},
                {'option': 'Partido 5', 'number': 5, 'votes': 56},
                {'option': 'Partido 6', 'number': 6, 'votes': 170},
            ]
        }

        expected_result = [
            {'option': 'Partido 6', 'number': 6, 'votes': 170, 'postproc': 9},
            {'option': 'Partido 5', 'number': 5, 'votes': 56, 'postproc': 2},
            {'option': 'Partido 1', 'number': 1, 'votes': 50, 'postproc': 1},
            {'option': 'Partido 3', 'number': 3, 'votes': 34, 'postproc': 0},
            {'option': 'Partido 4', 'number': 4, 'votes': 25, 'postproc': 0},
            {'option': 'Partido 2', 'number': 2, 'votes': 10, 'postproc': 0},
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_SainteLague2(self):
        data = {
            'type': 'SAINTE',
            'seats': 15,
            'options': [
                {'option': 'Partido 1', 'number': 1, 'votes': 50},
                {'option': 'Partido 2', 'number': 2, 'votes': 10},
                {'option': 'Partido 3', 'number': 3, 'votes': 34},
                {'option': 'Partido 4', 'number': 4, 'votes': 25},
                {'option': 'Partido 5', 'number': 5, 'votes': 56},
                {'option': 'Partido 6', 'number': 6, 'votes': 170},
                {'option': 'Partido 7', 'number': 7, 'votes': 90},
            ]
        }

        expected_result = [
            {'option': 'Partido 6', 'number': 6, 'votes': 170, 'postproc': 9},
            {'option': 'Partido 7', 'number': 7, 'votes': 90, 'postproc': 4},
            {'option': 'Partido 5', 'number': 5, 'votes': 56, 'postproc': 1},
            {'option': 'Partido 1', 'number': 1, 'votes': 50, 'postproc': 1},
            {'option': 'Partido 3', 'number': 3, 'votes': 34, 'postproc': 0},
            {'option': 'Partido 4', 'number': 4, 'votes': 25, 'postproc': 0},
            {'option': 'Partido 2', 'number': 2, 'votes': 10, 'postproc': 0},
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
