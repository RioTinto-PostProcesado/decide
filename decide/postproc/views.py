from rest_framework.views import APIView
from rest_framework.response import Response
import math

class PostProcView(APIView):

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            });

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)

        
    def simple(self, options, seats):

        out = []

        for opt in options:

            out.append({
                **opt,
                'postproc': 0,
            })

        out.sort(key=lambda x: -x['votes'])

        numeroEscanyos = seats
        numeroVotos = 0

        for votes in out:
            numeroVotos= numeroVotos + votes['votes']

        # Valor del escaño es igual al número de votos entre el número de escaños
        valor_escanyo = numeroVotos/numeroEscanyos

        x = 0;        

        #Mientras el número de escaños sea mayor a cero
        while numeroEscanyos > 0:
            
            #Si contador es menor que la longitud de out que intuyo es la cantidad de partidos que se presentan
            if x < len(out):
                
                #Los escaños se sacan truncando los votos entre el valor del escaño 
                escanyos = math.trunc(out[x]['votes']/valor_escanyo)

                #Voy asignando los escaños según el contador
                out[x]['postproc'] = escanyos

                #Actualizo el número de escaños
                numeroEscanyos = numeroEscanyos - escanyos 
                
                #Actualizo el contador
                x = x + 1
           
            else:

                #Controlo el partido actual
                actual = 0
                i = 1

                while i < len(out):

                    #El valor actual es el valor de los votos del partido del valor actual del escaño menos los escaños actuales del partido 
                    valor_Actual = out[actual]['votes']/valor_escanyo - out[actual]['postproc']
                    valor_Comparado = out[i]['votes']/valor_escanyo - out[i]['postproc']

                    if (valor_Actual >= valor_Comparado):

                        i = i + 1

                    else:

                        actual = i
                        i = i + 1


                out[actual]['postproc'] = out[actual]['postproc'] + 1

                numeroEscanyos = numeroEscanyos - 1

        return out

    def sin_paridad(self, options):

        """
        Metodo que devolverá el resultado de las votaciones sin tener en 
        cuenta la paridad de las personas presentadas a la votación

        * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
        """

        out = []

        for opt in options:

            out.append({
                **opt,
                'paridad': [],
            })

        for i in out:

            escanyos = i['postproc']
            presentados = i['candidatos']
            x = 0

            while escanyos > 0:
              
                i['paridad'].append(presentados[x])
                x = x + 1

                escanyos = escanyos - 1 

        return out

    def porcentaje_hombre_mujer(self, hombres, mujeres):
        
        """
        Metodo que devolverá:
            True: Si el porcentaje de hombres y mujeres está equilibrado entre 60%-40%
            False: En caso contrario

        Inputs: 
            hombres: Array con los hombres candidatos en la votación
            mujeres: Array con las mujeres candidatas en la votación
        """

        #Obtenemos el total de participantes y sus porcentajes según sexo
        total = len(hombres) + len(mujeres)
        porcentaje_hombres = len(hombres)/total
        porcentaje_mujeres = len(mujeres)/total

        #Si se cumplen las estadísticas determinadas devolveremos True, en caso contrario, False
        if (porcentaje_hombres < 0.4) | (porcentaje_mujeres < 0.4):
            return False
        else:
            return True


    def post(self, request):
        """
         * type: IDENTITY | EQUALITY | WEIGHT | SIMPLE
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
        """

        typeOfData = request.data.get('type')
        options =  request.data.get('options', [])
        seats = request.data.get('seats')

        if typeOfData == 'IDENTITY':
            return self.identity(options)

        elif typeOfData == 'SIMPLE':
            return Response(self.simple(options, seats))

        elif typeOfData == 'SIMPLE_SIN_PARIDAD':    
            simple_options = []
            simple_options = self.simple(options, seats)
            return Response(self.sin_paridad(simple_options))
           
        return Response({})

