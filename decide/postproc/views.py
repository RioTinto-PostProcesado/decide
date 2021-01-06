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




def sainteLague(self, options, seats):


    """
    
        * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }

        Definición:   Metodo que devolverá el resultado de las votaciones ordenando los resultados
        por escaños o asientos, pero usando como divisores los números impares, para una mayor representación
        de partidos o canditatos con menos votos. 

        Entrada: votos totales por cada eleccion y el numero de asientos o escaños

        Salida: lista con los partidos y los asientos asignados
    """

        out = []

        for opt in options:

            out.append({
                **opt,

                'postproc': 0,
            })

        out.sort(key=lambda x: -x['votes'])

        se = seats;       #Numero de escaños (asientos) totales

        while se > 0:

            i = 1;

            odd= 1;      #Genera que los dividores sean siempre impares

            actual = 0;

            while i < len(out):

                valor1 = out[actual]['votes'] / (out[actual]['postproc'] + odd);

                comparador = out[i]['votes'] / (out[i]['postproc'] + odd);

                if (valor1 >= comparador):

                    i = i + 1;

                    odd= odd + 2;

                else:

                    actual = i;

                    odd= odd + 2;

                out[actual]['postproc'] = out[actual]['postproc'] + 1;  #Le concede un escaño a la opcion

            se = se - 1;     #Va descontando escaños
            
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

        if typeOfData == 'IDENTITY':
            return self.identity(options)
        
        if typeOfData == 'BORDA':
            return self.borda(options)


        if typeOfData == 'SAINTE':
            return Response(self.sainteLague(opts, s))    

        elif typeOfData == 'PARIDAD':

        if typeOfData == 'PARIDAD':

            check = self.check_json(options)
            if check:
                return Response(self.paridad(options))
            else:
                return Response({'message' : 'No se cumplen los ratios de paridad 60%-40%'})
        
        if typeOfData == 'ORDER':
            return Response(self.order(options))

        return Response({})
