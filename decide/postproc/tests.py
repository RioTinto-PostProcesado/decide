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

    def test_identity_littleOptions(self):
        """
            * Definición: Test de algoritmo de identidad con una votación con sólo una opción
            * Entrada: Votación
                - Number: id del partido
                - Option: nombre de la opción
                - Votes: Número de votos que recibe en la votación
            * Salida: Mensaje de error indicando que no hay opciones suficientes
        """
        data = {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5},
            ]
        }

        expected_result = {
            'message': 'No hay opciones suficientes'}

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


    def test_borda(self):
        """
            * Definicion: Test que verifica si el algoritmo borda funciona correctamente
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
                - Group: Grupo de votación al que pertenece
            * Salida: los datos de entrada con un nuevo parámetro llamado total
            que supone el valor de esa opción tras aplicar el algoritmo
        """        
        data = {
            "type": "BORDA",	
            "options": [
                { "option": "Option 2", "number": 2, "votes": 10, "group":"g1" },
                { "option": "Option 1", "number": 1, "votes": 5, "group":"g1" },
                { "option": "Option 3", "number": 3, "votes": 7, "group":"g1" },
                { "option": "Option 1", "number": 4, "votes": 8, "group":"g2" },
                { "option": "Option 2", "number": 5, "votes": 3, "group":"g2" },
                { "option": "Option 3", "number": 6, "votes": 2, "group":"g2" }
            ]
        }
        expected_result = [
                { "option": "Option 2", "number": 2, "votes": 10, "group":"g1", "total":66 },
                { "option": "Option 3", "number": 3, "votes": 7, "group":"g1", "total":44},
                { "option": "Option 1", "number": 4, "votes": 8, "group":"g2", "total": 39},
                { "option": "Option 2", "number": 5, "votes": 3, "group":"g2", "total": 26},
                { "option": "Option 1", "number": 1, "votes": 5, "group":"g1", "total": 22},
                { "option": "Option 3", "number": 6, "votes": 2, "group":"g2", "total": 13}
                
            ]

        response = self.client.post("/postproc/", data, format="json")
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

    def test_SainteLagueMal(self):
        data = {
            'type': 'SAINTE',
            'seats': 0,
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

        expected_result = {
            'message': 'Los escaños son insuficientes'}

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_SainteLague_littleOptions(self):
        """
            * Definición: Test de algoritmo de Sainte Lague con una votación con sólo una opción
            * Entrada: Votación
                - Number: id del partido
                - Option: nombre de la opción
                - Votes: Número de votos que recibe en la votación
            * Salida: Mensaje de error indicando que no hay opciones suficientes
        """
        data = {
            'type': 'SAINTE',
            'seats': 12,
            'options': [
                {'option': 'Partido 1', 'number': 1, 'votes': 50},
            ]
        }

        expected_result = {
            'message': 'No hay opciones suficientes'}

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_bordaWrongPath(self):
        """
            * Definicion: Test que verifica que obtenemos un not found al realizar
            un post a una página que no existe
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
                - Group: Grupo de votación al que pertenece
            * Salida: 404, not found
        """        
        data = {
            "type": "BORDA",	
            "options": [
                { "option": "Option 2", "number": 2, "votes": 10, "group":"g1" },
                { "option": "Option 1", "number": 1, "votes": 5, "group":"g1" },
                { "option": "Option 3", "number": 3, "votes": 7, "group":"g1" },
                { "option": "Option 1", "number": 4, "votes": 8, "group":"g2" },
                { "option": "Option 2", "number": 5, "votes": 3, "group":"g2" },
                { "option": "Option 3", "number": 6, "votes": 2, "group":"g2" }  
            ]
        }

        response = self.client.post("/postprocesado/", data, format="json")
        self.assertEqual(response.status_code, 404)
    
    def test_bordaNoType(self):
        """
            * Definicion: Test donde no se especifica type en el json de entrada
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
                - Group: Grupo de votación al que pertenece
            * Salida: los datos de entrada tras aplicarle el type por defecto que es
            la función identity
        """        
        data = {	
            "options": [
                { "option": "Option 2", "number": 1, "votes": 10, "group":"g1" },
                { "option": "Option 3", "number": 2, "votes": 7, "group":"g1" },
                { "option": "Option 1", "number": 3, "votes": 8, "group":"g1" }
                ]
        }

        expected_result = [
            { "option": "Option 2", "number": 1, "votes": 10, "group":"g1", "postproc":10},
            { "option": "Option 1", "number": 3, "votes": 8, "group":"g1" , "postproc":8},
            { "option": "Option 3", "number": 2, "votes": 7, "group":"g1" , "postproc":7} 
            ]

        response = self.client.post("/postproc/", data, format="json")
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def testParidad2(self):
        """
            * Definicion: Test positivo con 2 hombres y 3 mujeres
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
                { 'option': 'Partido Unico', 'number': 1, 'votes': 5 , 'postproc': 5, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'mujer','id':'5'}
                ]}
            ]
        }

        expected_result = [
            { 'option': 'Partido Unico', 'number': 1, 'votes': 5, 'postproc': 5, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'mujer','id':'5'}
                ],
                'paridad': [
                 {'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'5'}
                ]}
        ]
        
        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    
    def testParidad3(self):
        """
            * Definicion: Test positivo con 3 hombres y 2 mujeres
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
                { 'option': 'Partido Unico', 'number': 1, 'votes': 5 , 'postproc': 5, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'mujer','id':'5'}
                ]}

            ]
        }

        expected_result = [
            { 'option': 'Partido Unico', 'number': 1, 'votes': 5, 'postproc': 5, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'mujer','id':'5'}
                ],
                'paridad': [
                 {'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'5'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ]}
        ]
        
        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
        
    def test_SainteLague3(self):

        """
            * Definicion: Comprueba que el método SainteLague devuelve los asientos correctos
            * Entrada: Json de la votacion
            * Salida: Codigo 200 y Json con el resultado de la votación y los asientos correctos
        """

        
        data = {
            'type': 'SAINTE',
            'seats': 15,
            'options': [
                {'option': 'Partido 1', 'number': 1, 'votes': 50},
                {'option': 'Partido 2', 'number': 2, 'votes': 10},
                {'option': 'Partido 3', 'number': 3, 'votes': 5},
                {'option': 'Partido 4', 'number': 4, 'votes': 25},
                {'option': 'Partido 5', 'number': 5, 'votes': 56},
                {'option': 'Partido 6', 'number': 6, 'votes': 120},
                {'option': 'Partido 7', 'number': 7, 'votes': 45},
            ]
        }

        expected_result = [
            {'option': 'Partido 6', 'number': 6, 'votes': 120, 'postproc': 8},
            {'option': 'Partido 5', 'number': 5, 'votes': 56, 'postproc': 3},
            {'option': 'Partido 1', 'number': 1, 'votes': 50, 'postproc': 2},
            {'option': 'Partido 7', 'number': 7, 'votes': 45, 'postproc': 2},
            {'option': 'Partido 4', 'number': 4, 'votes': 25, 'postproc': 0},
            {'option': 'Partido 2', 'number': 2, 'votes': 10, 'postproc': 0},
            {'option': 'Partido 3', 'number': 3, 'votes': 5, 'postproc': 0},
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_bordaGrupoUnico(self):
        """
            * Definicion: Test donde solo existe un grupo de votación
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
                - Group: Grupo de votación al que pertenece
            * Salida: los datos de entrada con un nuevo parámetro llamado total
            que supone el valor de esa opción tras aplicar el algoritmo
        """        
        data = {
            "type": "BORDA",	
            "options": [
                { "option": "Option 2", "number": 2, "votes": 10, "group":"g1" },
                { "option": "Option 3", "number": 3, "votes": 7, "group":"g1" },
                { "option": "Option 1", "number": 4, "votes": 8, "group":"g1" }
                 ]
        }

        expected_result = [

                { "option": "Option 2", "number": 2, "votes": 10, "group":"g1", "total":75 },
                { "option": "Option 1", "number": 4, "votes": 8, "group":"g1", "total": 50},
                { "option": "Option 3", "number": 3, "votes": 7, "group":"g1", "total":25}   
            ]

        response = self.client.post("/postproc/", data, format="json")
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result) 

    def test_SainteLague4(self):

        """
            * Definicion: Comprueba que el método SainteLague devuelve los asientos correctos
            * Entrada: Json de la votacion
            * Salida: Codigo 200 y Json con el resultado de la votación y los asientos correctos
        """

        data = {
            'type': 'SAINTE',
            'seats': 7,
            'options': [
                {'option': 'Partido 1', 'number': 1, 'votes': 50},
                {'option': 'Partido 2', 'number': 2, 'votes': 10},
                {'option': 'Partido 3', 'number': 3, 'votes': 5},
                {'option': 'Partido 4', 'number': 4, 'votes': 25},
                {'option': 'Partido 5', 'number': 5, 'votes': 56},
                {'option': 'Partido 6', 'number': 6, 'votes': 120},
                {'option': 'Partido 7', 'number': 7, 'votes': 45},

            ]
        }

        expected_result = [

            {'option': 'Partido 6', 'number': 6, 'votes': 120, 'postproc': 4},
            {'option': 'Partido 5', 'number': 5, 'votes': 56, 'postproc': 2},
            {'option': 'Partido 1', 'number': 1, 'votes': 50, 'postproc': 1},
            {'option': 'Partido 7', 'number': 7, 'votes': 45, 'postproc': 0},
            {'option': 'Partido 4', 'number': 4, 'votes': 25, 'postproc': 0},
            {'option': 'Partido 2', 'number': 2, 'votes': 10, 'postproc': 0},
            {'option': 'Partido 3', 'number': 3, 'votes': 5, 'postproc': 0},
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
   
    def test_bordaNoGroup(self):
        """
            * Definicion: Test donde los votos no estan agrupados
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
            * Salida: mensaje de error
        """

        data = {
            "type": "BORDA",	
            "options": [
                { "option": "Option 2", "number": 2, "votes": 10},
                { "option": "Option 1", "number": 1, "votes": 5},
                { "option": "Option 3", "number": 3, "votes": 7},
                { "option": "Option 1", "number": 4, "votes": 8},
                { "option": "Option 2", "number": 5, "votes": 3},
                { "option": "Option 3", "number": 6, "votes": 2} 
            ]
        }

        expected_result = {'message': 'Los votos no se pueden agrupar'}

        response = self.client.post("/postproc/", data, format="json")
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_SainteLagueURL(self):

        """
            *Definicion: Comprueba que si no se accede correctamente a la url el método devuelve un 404
            *Entrada: Json de la votacion
            *Salida: Codigo 404
        """
        data = {
            'type': 'SAINTE',
            'seats': 7,
            'options': [
                {'option': 'Partido 1', 'number': 1, 'votes': 50},
                {'option': 'Partido 2', 'number': 2, 'votes': 10},
                {'option': 'Partido 3', 'number': 3, 'votes': 5},
                {'option': 'Partido 4', 'number': 4, 'votes': 25},
                {'option': 'Partido 5', 'number': 5, 'votes': 56},
                {'option': 'Partido 6', 'number': 6, 'votes': 120},
                {'option': 'Partido 7', 'number': 7, 'votes': 45},
            ]
        }

        

        response = self.client.post('/postproco/', data, format='json')

        self.assertEqual(response.status_code, 404)

    def test_bordaMulti(self):
        data = {
            "type": "BORDA",	
            "options": [
                { "option": "Option 2", "number": 2, "votes": 105, "group":"g1" },
                { "option": "Option 1", "number": 1, "votes": 453, "group":"g1" },
                { "option": "Option 3", "number": 3, "votes": 242, "group":"g1" },
                { "option": "Option 1", "number": 4, "votes": 67, "group":"g2" },
                { "option": "Option 2", "number": 5, "votes": 23, "group":"g2" },
                { "option": "Option 3", "number": 6, "votes": 45, "group":"g2" },
                { "option": "Option 1", "number": 7, "votes": 230, "group":"g3" },
                { "option": "Option 2", "number": 8, "votes": 334, "group":"g3" },
                { "option": "Option 3", "number": 9, "votes": 234, "group":"g3" }
                
            ]
        }
        expected_result = [
                { "option": "Option 1", "number": 1, "votes": 453, "group":"g1", "total":2400},
                { "option": "Option 2", "number": 8, "votes": 334, "group":"g3", "total":2394},
                { "option": "Option 3", "number": 3, "votes": 242, "group":"g1", "total":1600},
                { "option": "Option 3", "number": 9, "votes": 234, "group":"g3", "total":1596},
                { "option": "Option 2", "number": 2, "votes": 105, "group":"g1", "total":800},
                { "option": "Option 1", "number": 7, "votes": 230, "group":"g3", "total":798},
                { "option": "Option 1", "number": 4, "votes": 67, "group":"g2","total":405},
                { "option": "Option 3", "number": 6, "votes": 45, "group":"g2", "total":270},
                { "option": "Option 2", "number": 5, "votes": 23, "group":"g2", "total":135}
                
            ]


        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
        
    def test_simple(self):

        """
            * Definicion: Comprueba que el método simple devuelva los resultados esperados
            * Entrada: Json de la votacion
            * Salida: Codigo 200 y Json con el resultado de la votación
        """
        data = {
            'type': 'SIMPLE',
            'seats':10,
            'options': [
                { 'option': 'Mortadelo', 'number': 1, 'votes': 5 },
                { 'option': 'Filemon', 'number': 2, 'votes': 2 },
                { 'option': 'Bacterio', 'number': 3, 'votes': 4 },
                { 'option': 'Ofelia', 'number': 4, 'votes': 3 },
                { 'option': 'Super', 'number': 5, 'votes': 5 },
                { 'option': 'Botones Sacarino', 'number': 6, 'votes': 1 },
        
            ]
        }

        expected_result = [
            { 'option': 'Mortadelo', 'number': 1, 'votes': 5, 'postproc': 3 },
            { 'option': 'Super', 'number': 5, 'votes': 5, 'postproc': 3 },
            { 'option': 'Bacterio', 'number': 3, 'votes': 4, 'postproc': 2 },
            { 'option': 'Ofelia', 'number': 4, 'votes': 3, 'postproc': 1 },
            { 'option': 'Filemon', 'number': 2, 'votes': 2, 'postproc': 1 },
            { 'option': 'Botones Sacarino', 'number': 6, 'votes': 1, 'postproc': 0 },
            

        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


       
    def test_simple_grande(self):
        """
            * Definicion: Comprueba que el método simple devuelva los resultados esperados 
            * Entrada: Json de la votacion
            * Salida: Codigo 200 y Json con el resultado de la votación
        """
        data = {
            'type': 'SIMPLE',
            'seats': 500,
            'options': [
                { 'option': 'Mortadelo', 'number': 1, 'votes': 10000 },
                { 'option': 'Filemon', 'number': 2, 'votes': 20000 },
                { 'option': 'Bacterio', 'number': 3, 'votes': 500 },
                { 'option': 'Ofelia', 'number': 4, 'votes':  400},
                { 'option': 'Super', 'number': 5, 'votes': 15000 },
                { 'option': 'Botones Sacarino', 'number': 6, 'votes': 4100 },

            ]
        }

        expected_result = [
            { 'option': 'Filemon', 'number': 2, 'votes': 20000, 'postproc': 200 },
            { 'option': 'Super', 'number': 5, 'votes': 15000, 'postproc': 150 },
            { 'option': 'Mortadelo', 'number': 1, 'votes': 10000, 'postproc':  100},
            { 'option': 'Botones Sacarino', 'number': 6, 'votes': 4100, 'postproc': 41 },
            { 'option': 'Bacterio', 'number': 3, 'votes': 500, 'postproc': 5 },
            { 'option': 'Ofelia', 'number': 4, 'votes': 400, 'postproc': 4 },
        ]
        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def testSimpleFalla(self):
        
        """
            *Definicion: Comprueba que si no se accede correctamente a la url el método devuelve un 404
            *Entrada: Json de la votacion
            *Salida: Codigo 404
        """

        data = {
            'type': 'SIMPLE',
            'seats':1,
            'options': [
                { 'option': 'Mortadelo', 'number': 1, 'votes': 5 }
            ]
        }

        
        response = self.client.post('/postproci/', data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_simple_sin_paridad(self):
        
        """
            * Definicion: Comprueba que el método sin_paridad devuelve los candidatos electos correctos 
            * Entrada: Json de la votacion
            * Salida: Codigo 200 y Json con el resultado de la votación y los candidatos electos
        """

        data = {
            'type': 'SIMPLE_SIN_PARIDAD',
            'seats':5,
            'options': [
                { 'option': 'Mortadelo', 'number': 1, 'votes': 50,'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]}, 
                { 'option': 'Filemon', 'number': 2, 'votes': 30,'candidatos': [
                {'sexo':'mujer','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]}
            ]
        }

        expected_result = [

            { 'option': 'Mortadelo', 'number': 1, 'votes': 50, 'postproc': 3, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                {'sexo':'hombre','id':'1'},
                {'sexo':'mujer','id':'2'},
                {'sexo':'hombre','id':'3'}
                ]
            },
              
            { 'option': 'Filemon', 'number': 2, 'votes': 30, 'postproc': 2 , 'candidatos': [
                 {'sexo':'mujer','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                {'sexo':'mujer','id':'1'},
                {'sexo':'hombre','id':'2'},
                ]
            }
        ]
        

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.maxDiff = None
        self.assertEqual(values, expected_result)



    def test_simple_sin_paridad_grande(self):
        
        """
            * Definicion: Comprueba que el método sin_paridad devuelve los candidatos electos correctos
            * Entrada: Json de la votacion
            * Salida: Codigo 200 y Json con el resultado de la votación y los candidatos electos
        """

        data = {
            'type': 'SIMPLE_SIN_PARIDAD',
            'seats':10,
            'options': [
                { 'option': 'Mortadelo', 'number': 1, 'votes': 5,'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]}, 
                { 'option': 'Filemon', 'number': 2, 'votes': 2,'candidatos': [
                 {'sexo':'mujer','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]},
                { 'option': 'Bacterio', 'number': 3, 'votes': 4, 'candidatos': [
                 {'sexo':'mujer','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]}, 
                { 'option': 'Ofelia', 'number': 4, 'votes': 3,'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ] },
                { 'option': 'Super', 'number': 5, 'votes': 5 ,'candidatos': [
                 {'sexo':'mujer','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]},
                { 'option': 'Botones Sacarino', 'number': 6, 'votes': 1 ,'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]},
        
            ]
        }

        expected_result = [

            { 'option': 'Mortadelo', 'number': 1, 'votes': 5, 'postproc': 3, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                {'sexo':'hombre','id':'1'},
                {'sexo':'mujer','id':'2'},
                {'sexo':'hombre','id':'3'}
                ]
            },
              
            { 'option': 'Super', 'number': 5, 'votes': 5, 'postproc': 3 , 'candidatos': [
                 {'sexo':'mujer','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                {'sexo':'mujer','id':'1'},
                {'sexo':'hombre','id':'2'},
                {'sexo':'hombre','id':'3'}
                ]
            },
            { 'option': 'Bacterio', 'number': 3, 'votes': 4, 'postproc': 2 , 'candidatos': [
                 {'sexo':'mujer','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                {'sexo':'mujer','id':'1'},
                {'sexo':'hombre','id':'2'}
                ]
            },
            { 'option': 'Ofelia', 'number': 4, 'votes': 3, 'postproc': 1 , 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                {'sexo':'hombre','id':'1'}
                ]
            },
            { 'option': 'Filemon', 'number': 2, 'votes': 2, 'postproc': 1 , 'candidatos': [
                {'sexo':'mujer','id':'1'}
                ,{'sexo':'hombre','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                    {'sexo':'mujer','id':'1'}
                ]},
            { 'option': 'Botones Sacarino', 'number': 6, 'votes': 1, 'postproc': 0 , 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                ]
            }
        ]
        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_simple_littleOptions(self):
        """
            * Definición: Test de algoritmo simple con una votación con sólo una opción
            * Entrada: Votación
                - Number: id del partido
                - Option: nombre de la opción
                - Votes: Número de votos que recibe en la votación
            * Salida: Mensaje de error indicando que no hay opciones suficientes
        """
        data = {
            'type': 'SIMPLE',
            'seats':10,
            'options': [
                { 'option': 'Mortadelo', 'number': 1, 'votes': 5 },
            ]
        }

        expected_result = {
            'message': 'No hay opciones suficientes'}

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    
    def test_saint_lague_sin_paridad(self):
        
        """
            * Definicion: Comprueba que el método sin_paridad devuelve los candidatos electos correctos con el algoritmo Saint Lague
            * Entrada: Json de la votacion
            * Salida: Codigo 200 y Json con el resultado de la votación y los candidatos electos
        """

        data = {
            'type': 'SAINTE_LAGUE_SIN_PARIDAD',
            'seats':12,
            'options': [
                { 'option': 'Partido 1', 'number': 1, 'votes': 50,'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]}, 
                { 'option': 'Partido 2', 'number': 2, 'votes': 10,'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]},
                {'option': 'Partido 3', 'number': 3, 'votes': 34, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]}, 
                { 'option': 'Partido 4', 'number': 4, 'votes': 25,'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ] },
                { 'option': 'Partido 5', 'number': 5, 'votes': 56,'candidatos': [
                {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ]},
                { 'option': 'Partido 6', 'number': 6, 'votes': 170,'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ,{'sexo':'hombre','id':'7'}
                ,{'sexo':'mujer','id':'8'}
                ,{'sexo':'hombre','id':'9'}
                ,{'sexo':'mujer','id':'10'}
                ,{'sexo':'hombre','id':'11'}
                ,{'sexo':'mujer','id':'12'}
                ]},
        
            ]
        }

        expected_result = [

            { 'option': 'Partido 6', 'number': 6, 'votes': 170, 'postproc': 9, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ,{'sexo':'hombre','id':'7'}
                ,{'sexo':'mujer','id':'8'}
                ,{'sexo':'hombre','id':'9'}
                ,{'sexo':'mujer','id':'10'}
                ,{'sexo':'hombre','id':'11'}
                ,{'sexo':'mujer','id':'12'}
                ], 
                'paridad': [
                {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ,{'sexo':'hombre','id':'7'}
                ,{'sexo':'mujer','id':'8'}
                ,{'sexo':'hombre','id':'9'}
                ]
            },
              
            {'option': 'Partido 5', 'number': 5, 'votes': 56, 'postproc': 2, 'candidatos': [
                {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [
                {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ]
            },
            { 'option': 'Partido 1', 'number': 1, 'votes': 50, 'postproc': 1, 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': [{'sexo':'hombre','id':'1'}]
            },
            { 'option': 'Partido 3', 'number': 3, 'votes': 34, 'postproc': 0 , 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': []
            },
            { 'option': 'Partido 4', 'number': 4, 'votes': 25, 'postproc': 0, 'candidatos': [
                {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': []
                },
            { 'option': 'Partido 2', 'number': 2, 'votes': 10, 'postproc': 0 , 'candidatos': [
                 {'sexo':'hombre','id':'1'}
                ,{'sexo':'mujer','id':'2'}
                ,{'sexo':'hombre','id':'3'}
                ,{'sexo':'mujer','id':'4'}
                ,{'sexo':'hombre','id':'5'}
                ,{'sexo':'mujer','id':'6'}
                ], 
                'paridad': []
            }
            
        ]
        

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)



    def test_dhondt(self):
        
        data = {
            "type": "DHONDT",
            "seats": 8,
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
            { "option": "Option 1", "number": 1, "votes": 5, "postproc": 3 },
            { "option": "Option 5", "number": 5, "votes": 5, "postproc": 3 },
            { "option": "Option 3", "number": 3, "votes": 3, "postproc": 1 },
            { "option": "Option 4", "number": 4, "votes": 2, "postproc": 1 },
            { "option": "Option 2", "number": 2, "votes": 0, "postproc": 0 },
            { "option": "Option 6", "number": 6, "votes": 1, "postproc": 0 },
        ]


        data = {
            "type": "DHONDT",
            "seats": 10,
            "options": [
                { "option": "Option 1", "number": 1, "votes": 20 },
                { "option": "Option 2", "number": 2, "votes": 11 },
                { "option": "Option 3", "number": 3, "votes": 0 },
                { "option": "Option 4", "number": 4, "votes": 10 },
                { "option": "Option 5", "number": 5, "votes": 5 },
            ]
        }
        
        expected_result = [
            { "option": "Option 1", "number": 1, "votes": 20, "postproc": 5 },
            { "option": "Option 2", "number": 2, "votes": 11, "postproc": 2 },
            { "option": "Option 4", "number": 4, "votes": 10, "postproc": 2 },
            { "option": "Option 5", "number": 5, "votes": 5, "postproc": 1 },
            { "option": "Option 3", "number": 3, "votes": 0, "postproc": 0 },
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
            "seats": 0,
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
    
    def test_dhondt_noVotes(self):
        """
            * Definición: Test negativo que no recibe votos
            * Entrada: Votación
                - Number: id del partido
                - Option: nombre de la opción
                - Votes: Numero de votos que recibe en la votación
            * Salida: Código 200 con los datos de entrada junto con el postprocesado, de forma
            que ningún partido recibe escaños
        """

        data = {
            "type": "DHONDT",
            "seats": 8,
            "options": [
                { "option": "Option 1", "number": 1, "votes": 0 },
                { "option": "Option 2", "number": 2, "votes": 0 },
                { "option": "Option 3", "number": 3, "votes": 0 },
                { "option": "Option 4", "number": 4, "votes": 0 },
                { "option": "Option 5", "number": 5, "votes": 0 },
                { "option": "Option 6", "number": 6, "votes": 0 },
            ]
        }
        
        expected_result = {
            'message': 'No hay votos'
        }
   
        response = self.client.post("/postproc/", data, format="json")
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
    
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
        
    def test_order_noVotes(self):
        """
            * Definicion: Test para mostrar que aquellas opciones con más votos,en esta ocasion no hay votos
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
            * Salida: los datos de entrada junto con el postprocesado, apareciendo primero el partido mas votado, que es a su vez el menos favorito por tener menos postprocesado
        """        

        data = {
            'type': 'ORDER',
            'options': [
                {  'number': 1,'option': 'Option 1', 'votes': 0 },
                {  'number': 2,'option': 'Option 2', 'votes': 0 },
                {  'number': 3,'option': 'Option 3', 'votes': 0 },
                
            ]
        }

        expected_result = {
            'message': 'Los escaños son insuficientes'
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_order_error(self):
        """
            * Definicion: Test para mostrar que aquellas opciones con más votos, son las que menos postprocesado tienen y por tanto son las menos preferidas
            * Entrada: Votacion
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
            * Salida: Codigo 404
        """        

        data = {
            'type': 'ORDER',
            'options': [
                {  'number': 1,'option': 'Option 1', 'votes': 2 },
                {  'number': 2,'option': 'Option 2', 'votes': 5 },
                {  'number': 3,'option': 'Option 3', 'votes': 1 },
                
            ]
        }

        response = self.client.post('/postproci/', data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_order_tie_littleVotes(self):
        """
            * Definición: Test para mostrar que aquellas opciones con más votos. En esta ocasión, hay
            empate (entre todas las opciones) a una cantidad de votos menor a la suma de todas
            las puntuaciones posibles a recibir por cada opción
            * Entrada: Votación
                - Number: id del partido
                - Option: nombre de la opcion
                - Votes: Numero de votos que recibe en la votación
            * Salida: Código 200 con mensaje de que no hay escaños suficientes para repartir
        """        

        data = {
            'type': 'ORDER',
            'options': [
                {  'number': 1,'option': 'Option 1', 'votes': 2 },
                {  'number': 2,'option': 'Option 2', 'votes': 2 },
                {  'number': 3,'option': 'Option 3', 'votes': 2 },
                
            ]
        }

        expected_result = {
            'message': 'Los escaños son insuficientes'
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_order_littleOptions(self):
        """
            * Definición: Test de algoritmo de orden con una votación con sólo una opción
            * Entrada: Votación
                - Number: id del partido
                - Option: nombre de la opción
                - Votes: Número de votos que recibe en la votación
            * Salida: Mensaje de error indicando que no hay opciones suficientes
        """
        data = {
            'type': 'ORDER',
            'options': [
                {  'number': 1,'option': 'Option 1', 'votes': 2 },
            ]
        }

        expected_result = {
            'message': 'No hay opciones suficientes'}

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
   

    def test_identity_candidatos(self):
        """
            * Definición: 
            * Entrada: Votación
                - Number: id del partido
                - Option: nombre de la opción
                - Votes: Número de votos que recibe en la votación
                - Candidatos: Numero de candidatos por partido
            * Salida: Mensaje de error indicando que no hay candidatos suficientes
        """
        data = {
            'type': 'DEFENSA',
            'options': [
                {'option': 'Partido 1', 'number': 1, 'votes': 5, 'candidatos': [
                 {'sexo':'mujer','id':'1'}
                ,{'sexo':'mujer','id':'3'}
                ]}
            ]
        }
    
        expected_result = {
            'message': 'No hay candidatos suficientes'}
    
        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)
    
        values = response.json()
        self.assertEqual(values, expected_result)
