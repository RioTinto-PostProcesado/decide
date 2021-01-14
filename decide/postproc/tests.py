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

    
    def test_dhondt(self):
        
        data = {
            "type": "DHONDT",
            "escanio": "8",
            "options": [
                { "option": "Option 1", "number": 1, "votes": 5 },
                { "option": "Option 2", "number": 2, "votes": 0 },
                { "option": "Option 3", "number": 3, "votes": 3 },
                { "option": "Option 4", "number": 4, "votes": 2 },
                { "option": "Option 5", "number": 5, "votes": 5 },
                { "option": "Option 6", "number": 6, "votes": 1 },
            ]
        }
        
        expected_result = [
            { "option": "Option 1", "number": 1, "votes": 5, "escanio": 3 },
            { "option": "Option 5", "number": 5, "votes": 5, "escanio": 3 },
            { "option": "Option 3", "number": 3, "votes": 3, "escanio": 1 },
            { "option": "Option 4", "number": 4, "votes": 2, "escanio": 1 },
            { "option": "Option 2", "number": 2, "votes": 0, "escanio": 0 },
            { "option": "Option 6", "number": 6, "votes": 1, "escanio": 0 },
        ]


        data = {
            "type": "DHONDT",
            "escanio": 10,
            "options": [
                { "option": "Option 1", "number": 1, "votes": 20 },
                { "option": "Option 2", "number": 2, "votes": 11 },
                { "option": "Option 3", "number": 3, "votes": 0 },
                { "option": "Option 4", "number": 4, "votes": 10 },
                { "option": "Option 5", "number": 5, "votes": 5 },
            ]
        }
        
        expected_result = [
            { "option": "Option 1", "number": 1, "votes": 20, "escanio": 5 },
            { "option": "Option 2", "number": 2, "votes": 11, "escanio": 2 },
            { "option": "Option 4", "number": 4, "votes": 10, "escanio": 2 },
            { "option": "Option 5", "number": 5, "votes": 5, "escanio": 1 },
            { "option": "Option 3", "number": 3, "votes": 0, "escanio": 0 },
        ]
   
       

        response = self.client.post("/postproc/", data, format="json")
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
    
    def test_dhondt_error(self):
        """
            * Definicion: Test negativo que no recibe escaños
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
            * Salida: Codigo 200 con mensaje de que no hay escaños suficientes para repartir
        """ 

        data = {
            "type": "DHONDT",
            "escanio": 0,
            "options": [
                { "option": "Option 1", "number": 1, "votes": 10 },
                { "option": "Option 2", "number": 2, "votes": 0 },
                { "option": "Option 3", "number": 3, "votes": 0 },
                { "option": "Option 4", "number": 4, "votes": 1 },
                { "option": "Option 5", "number": 5, "votes": 4 },
                { "option": "Option 6", "number": 6, "votes": 2 },
            ]
        }
        
        expected_result = {
            'message': 'Los escaños son insuficientes'
        }
        
        response = self.client.post("/postproc/", data, format="json")
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_dhondt_mal(self):
        """
            * Definicion: Test negativo que no recibe escaños
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
            * Salida: Codigo 404
        """ 

        data = {
            "type": "DHONDT",
            "options": [
                { "option": "Option 1", "number": 1, "votes": 10 },
                { "option": "Option 2", "number": 2, "votes": 0 },
                { "option": "Option 3", "number": 3, "votes": 0 },
                { "option": "Option 4", "number": 4, "votes": 1 },
                { "option": "Option 5", "number": 5, "votes": 4 },
                { "option": "Option 6", "number": 6, "votes": 2 },
            ]
        }
        
        response = self.client.post('/postproci/', data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_order(self):
        """
            * Definicion: Test para mostrar que aquellas opciones con más votos, son las que menos postprocesado tienen y por tanto son las menos preferidas
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
            * Salida: los datos de entrada junto con el postprocesado, apareciendo primero el partido mas votado, que es a su vez el menos favorito por tener menos postprocesado
        """        

        data = {
            'type': 'ORDER',
            'options': [
                {  'number': 1,'option': 'Option 1', 'votes': 2 },
                {  'number': 2,'option': 'Option 2', 'votes': 5 },
                {  'number': 3,'option': 'Option 3', 'votes': 1 },
                
            ]
        }

        expected_result = [            
           
            { 'number': 2,'option': 'Option 2', 'votes': 5,  'postproc': 2995 },
            { 'number': 1,'option': 'Option 1', 'votes': 2,  'postproc': 2998 },
            { 'number': 3,'option': 'Option 3', 'votes': 1, 'postproc': 2999 },
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
    
        
   
