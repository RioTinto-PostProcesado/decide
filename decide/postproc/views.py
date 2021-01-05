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
    
    def groups(self, options):
        groups = set()
        grpOptions = {}
        
        #Obtener grupos
        for opt in options:
            groups.add(opt["group"])
             
        #Inicializar listas de opciones
        for group in groups:
            grpOptions[group] = []      

        #Categorizar opciones por grupo
        for opt in options:
            grpOptions[opt.get("group")].append(opt)

        return grpOptions
        

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
        
        if typeOfData == 'BORDA':
            return self.borda(options)

        elif typeOfData == 'PARIDAD':
            check = self.check_json(options)
            if check:
                return Response(self.paridad(options))
            else:
                return Response({'message' : 'No se cumplen los ratios de paridad 60%-40%'})

        return Response({})
