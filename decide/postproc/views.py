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

        elif t == 'SAINTE':
            return Response(self.sainteLague(opts, s))    

        elif typeOfData == 'PARIDAD':
            check = self.check_json(options)
            if check:
                return Response(self.paridad(options))
            else:
                return Response({'message' : 'No se cumplen los ratios de paridad 60%-40%'})

        return Response({})
