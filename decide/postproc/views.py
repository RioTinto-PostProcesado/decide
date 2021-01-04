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

            for candi in candidatos:
                if candi['sexo'] == 'hombre':
                    listaHombres.append(cand)
                elif candi['sexo'] == 'mujer':
                    listaMujeres.append(cand)
                    
            
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
            check = self.check_json(options)
            if check:
                return Response(self.paridad(options))
            else:
                return Response({'message' : 'No se cumplen los ratios de paridad 60%-40%'})

        return Response({})
