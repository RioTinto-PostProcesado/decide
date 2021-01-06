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
    

    def order(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': 0,
            });

        out.sort(key=lambda x: -x['votes'])

        max=len(options)*1000

        a=0

        while a < len(out):
            postproc_a=max-out[a]['votes']
            out[a]['postproc']=postproc_a
            a=a+1

        return out

    def borda(self, options):

        #Añadimos total para todas las opciones
        for opt in options:
            opt['total'] = 0

        #Agrupamos las opciones segun su grupo de votación
        grp = self.groups(options)
        res = []

        #Ordenamos las opciones según el número de votos 
        for g in grp:
            lista = sorted(grp[g], key = lambda x:x["votes"])
            votosTotales = 0

            #Obtenemos la suma todos los votos
            for lis in lista:
                votosTotales +=  lis["votes"]
            
            cont = 1
            #Aplicamos el algoritmo de borda
            for l in lista:
                tot = votosTotales * cont
                l['total'] = tot
                res.append(l)
                cont += 1
        
        #Ordenamos todos los votos según su valot total tras aplicar borda
        res.sort(key=lambda x : x['total'],reverse=True)
        return Response(res)


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

        if typeOfData == 'IDENTITY':
            return self.identity(options)
        
        if typeOfData == 'BORDA':
            return self.borda(options)

        if typeOfData == 'PARIDAD':
            check = self.check_json(options)
            if check:
                return Response(self.paridad(options))
            else:
                return Response({'message' : 'No se cumplen los ratios de paridad 60%-40%'})
        
        if typeOfData == 'ORDER':
            return Response(self.order(options))

        return Response({})
