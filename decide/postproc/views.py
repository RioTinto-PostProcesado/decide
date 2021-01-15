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
            })

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)

    def order(self, options):
        """
            * options: [
                {
                 option: str,
                 number: int,
                 votes: int,
                 ...extraparams
                }
            * Definición: Método que devolverá el resultado de las votaciones, asignando mayor valor de
            postprocesado a aquellas opciones con las posiciones más altas en votación. La votación de orden
            consistirá en ordenar las opciones sugeridas siguiendo un criterio determinado (por ejemplo,
            preferencia).
            * Entrada: votos totales por cada eleccion (es decir, la suma total de los puestos obtenidos por
            cada opción en las votaciones, de forma que las opciones con menos votos serán las que obtuvieran
            posiciones más altas).
            * Salida: lista con las opciones y sus valores de postprocesado correspondientes.
        """

        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': 0,
            })

        out.sort(key=lambda x: -x['votes'])

        max = len(options)*1000

        a = 0

        while a < len(out):
            postproc_a = max-out[a]['votes']
            out[a]['postproc'] = postproc_a
            a = a+1

        return out

    def borda(self, options):

        # Añadimos total para todas las opciones
        for opt in options:
            opt['total'] = 0

        # Agrupamos las opciones segun su grupo de votación
        grp = self.groups(options)
        res = []

        # Ordenamos las opciones según el número de votos
        for g in grp:
            lista = sorted(grp[g], key=lambda x: x["votes"])
            votosTotales = 0

            # Obtenemos la suma todos los votos
            for lis in lista:
                votosTotales += lis["votes"]

            cont = 1
            # Aplicamos el algoritmo de borda
            for l in lista:
                tot = votosTotales * cont
                l['total'] = tot
                res.append(l)
                cont += 1

        # Ordenamos todos los votos según su valot total tras aplicar borda
        res.sort(key=lambda x: x['total'], reverse=True)
        return Response(res)

    def sainteLague(self, options, seats):
        """
            * Definicion: Dado un numero de partido con sus votos correspondientes, devuelve los escaños
            o asientos asignados a cada uno utilizando el algoritmo de SainteLague.
            * Entrada: Json de la votacion, y asientos a dividir.
            * Salida: Asientos divididos entre los partidos según sus votos.
        """

        out = []

        for opt in options:

            out.append({
                **opt,

                'postproc': 0,
            })

        out.sort(key=lambda x: -x['votes'])

        asientos = seats

        if(asientos <= 0):

            out = {'message': 'Los escaños son insuficientes'}

            return out

        while asientos > 0:

            actual = 0

            i = 1

            odd = 1

            while i < len(out):

                # Calcula los escaños de los partidos selecionados

                primerValor = out[actual]['votes'] / \
                    (out[actual]['postproc'] + odd)

                segundoValor = out[i]['votes'] / (out[i]['postproc'] + odd)

                if (primerValor >= segundoValor):

                    # Compara el valor de los partidos selecionados

                    i = i + 1

                    odd = odd+2

                else:

                    # Pasa a comparar a los siguientes partidos

                    actual = i

                    i = i + 1

                    odd = odd+2

            out[actual]['postproc'] = out[actual]['postproc'] + \
                1  # Asigna un escaño al partido correspondiente

            asientos = asientos - 1  # Descuenta un asiento a los totales

        return out

    def paridad(self, options):
        """
            * Definicion: Devuelve la lista de candidatos intercalando hombres y mujeres en el caso de que se cumpla la paridad
            * Entrada: Json de la votacion
            * Salida: Lista de candidatos ordenada si hay paridad, mensaje de error si no hay paridad
        """

        out = []

        for opt in options:
            out.append({
                **opt,
                'paridad': [],
            })

        for i in out:
            escanios = i['postproc']
            candidatos = i['candidatos']
            listaHombres = []
            listaMujeres = []
            h = 0
            m = 0
            paridad = True

            # Almacenamos en dos listas los hombres y las mujeres
            for candi in candidatos:
                if candi['sexo'] == 'hombre':
                    listaHombres.append(candi)
                elif candi['sexo'] == 'mujer':
                    listaMujeres.append(candi)

            check = self.checkPorcentajeParidad(listaHombres, listaMujeres)

            if not check:
                out = {'message': 'No se cumplen los ratios de paridad 60%-40%'}
                break

            # Recorremos todos los escanios disponibles
            while escanios > 0:
                # Si existe paridad en ese momento
                if paridad:
                    # Si la cantidad de mujeres incluidas es menor que la cantidad de mujeres
                    if m < len(listaMujeres):
                        i['paridad'].append(listaMujeres[m])
                        m = m + 1
                    # Si no, se aniade un hombre y se pone la paridad a False
                    else:
                        i['paridad'].append(listaHombres[h])
                        h = h + 1
                    paridad = False

                # Si no existe paridad en ese momento
                else:
                    # Si el numero de hombres es menor que el numero de hombres en la lista, se aniade un hombre
                    if h < len(listaHombres):
                        i['paridad'].append(listaHombres[h])
                        h = h + 1
                    # En caso contrario, se aniade una mujer y vuelve a existir paridad en la lista
                    else:
                        i['paridad'].append(listaMujeres[m])
                        m = m + 1
                    paridad = True

                # Cuenta regresiva de los escanios
                escanios -= 1
        return out

    def checkPorcentajeParidad(self, hombres, mujeres):
        """
            * Definicion: Comprueba si se cumplen los porcentajes minimos de hombres y mujeres
            * Entrada: Lista de hombres y de mujeres en la votacion
            * Salida: True si se cumple la paridad, False si no se cumple
        """
        total = len(hombres)+len(mujeres)

        porcentajeHombres = len(hombres)/total
        porcentajeMujeres = len(mujeres)/total

        return not (porcentajeMujeres < 0.4 or porcentajeHombres < 0.4)

    def simple(self, options, seats):

        """
            * Definicion: Devuelve el número de escaños de una votación según los votos recibidos y los escaños a dividir
            * Entrada: Json de la votacion y número de escaños disponibles
            * Salida: Lista ordenada con los resultados de la votación según los escaños conseguidos
        """

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
            * Definicion: Calcula los miembros electos
            * Entrada: Json de la votacion procesada
            * Salida: Lista de candidatos ordenada
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

    def post(self, request):
        """
            * type: IDENTITY | PARIDAD | ORDER
            * options: [
                {
                 option: str,
                 number: int,
                 votes: int,
                 ...extraparams
                }
               ]
        """

        typeOfData = request.data.get('type', 'IDENTITY')
        options = request.data.get('options', [])
        s = request.data.get('seats')

        if typeOfData == 'IDENTITY':
            return self.identity(options)

        elif typeOfData == 'BORDA':
            return self.borda(options)

        elif typeOfData == 'SAINTE':
            return Response(self.sainteLague(options, s))
        elif typeOfData == 'SIMPLE':
            return Response(self.simple(options, s))

        elif typeOfData == 'SIMPLE_SIN_PARIDAD':    
            simple_options = []
            simple_options = self.simple(options, s)
            return Response(self.sin_paridad(simple_options))

        elif typeOfData == 'SAINTE_LAGUE_SIN_PARIDAD':    
            sL_options = []
            sL_options = self.sainteLague(options, s)
            return Response(self.sin_paridad(sL_options))

        elif typeOfData == 'PARIDAD':
            return Response(self.paridad(options))

        elif typeOfData == 'ORDER':
            return Response(self.order(options))

        return Response({})