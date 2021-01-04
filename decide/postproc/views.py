from rest_framework.views import APIView
from rest_framework.response import Response


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


    def paridad(self, options):

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
            h=0
            m=0
            paridad = True

            # Almacenamos en dos listas los hombres y las mujeres
            for candi in candidatos:
                if candi['sexo'] == 'hombre':
                    listaHombres.append(candi)
                elif candi['sexo'] == 'mujer':
                    listaMujeres.append(candi)

            check = self.checkPorcentajeParidad(listaHombres, listaMujeres)

            if ~check:
                out = {'message' : 'No se cumplen los ratios de paridad 60%-40%'}
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


    def post(self, request):
        """
         * type: IDENTITY | EQUALITY | WEIGHT
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

        if typeOfData == 'IDENTITY':
            return self.identity(options)

        elif typeOfData == 'PARIDAD':
            return Response(self.paridad(options))
            
        return Response({})
