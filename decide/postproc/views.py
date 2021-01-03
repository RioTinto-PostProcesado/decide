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


    def dhont(self, options, escanio):
        #Añadimos escaños para todas las opciones
        for opt in options:
            opt['escanio'] = 0

        #Para cada escaño se hacen los calculos para averiguar que opción tiene el mayor cociente, el que tenga el mayor, se lleva el escaño
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

        t = request.data.get('type', 'IDENTITY')
        opts = request.data.get('options', [])


        if t == 'IDENTITY':
            return self.identity(opts)

        if t == 'DHONDT':
            escanio = int(float(request.data.get('escanio', '5')))
            return self.dhont(opts, escanio)


        return Response({})