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

    
    def dhondt(self, options, escanio):
        """
            * Definicion: Asigna escaños en las listas electorales
            * Entrada: Json de la votación asignando los escaños según corresponda
            * Salida: Lista de la opciones ordenadas según el número de escaños que posean,
            de mayor a menor
        """
        
        #Para cada opcion se le añaden escaños
        for opt in options:
            opt['escanio'] = 0

        #Para asignar escaños, se realiza la división entre los vosotros que tiene cada opción y los escaños (inicialmente se divide entre 1)
        #El mayor cociente se lleva el escaño
        for i in range(escanio):
            max(options, 
                key = lambda x : x['votes'] / (x['escanio'] + 1.0))['escanio'] += 1

        #Se ordenan las opciones según los escaños
        options.sort(key=lambda x: -x['escanio'])
        return Response(options)

        

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

        
        elif typeOfData == 'DHONDT':
            escanio = int(float(request.data.get('escanio', int )))
            return self.dhondt(options, escanio)
        
        return Response({})
        