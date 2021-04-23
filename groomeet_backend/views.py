from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from groomeet_backend.models import *
from django.contrib.auth import logout,authenticate
from django.contrib.auth.decorators import login_required
from datetime import date
from django.utils.safestring import mark_safe
import json
from groomeet_backend.models import Message
from django.db.models import Q

# Create your views here.
def base(request):
    return render(request, 'base.html')

def days_between(d1, d2):
    return abs(d2 - d1).days

@login_required(login_url='/login/')
def index(request):

    context = listadoMusicos(request)
    return render(request, '../templates/index.html', context)

@login_required(login_url='/login/')
def musico(request):
    if request.user.musico.isGold==False and request.user.musico.isSilver==False:
        fechaUltimaRenovacion = request.user.musico.ultimaRenovacionLikes
        today = date.today()
        dias = days_between(fechaUltimaRenovacion, today)
        if dias >= 1:
            request.user.musico.likesDisponibles = 10
            request.user.musico.ultimaRenovacionLikes = today
            request.user.musico.save()
    try:
        compra = Compra.objects.filter(usuario=request.user).order_by('-fecha_compra').first()
        today = date.today()
        dias = days_between(compra.fecha_compra, today)
        if(dias>30):
            request.user.musico.isGold=False
            request.user.musico.isSilver=False
            request.user.musico.save()
    except:
        pass
    return render(request, '../templates/index.html')

@login_required(login_url='/login/')
def banda(request, pkBanda):
    banda = get_object_or_404(Banda, id=pkBanda) #ESTO HAY QUE DARLE UN REPASO
    usuario = request.user
    if (banda.administrador.usuario.id == usuario.id):
        return render(request, '../templates/index.html')
    else:
        return redirect("/")

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required(login_url='/login/')
def chat(request):
    return render(request, 'chat.html')

@login_required(login_url='/login/')
def getMusico(request):
    musicos = Musico.objects.all().order_by('-isBoosted', '-usuario__last_login')
    result = []
    usuario = request.user

    for musico in musicos:
        if usuario.id is not musico.usuario.id and usuario not in musico.likesRecibidos.all() and usuario not in musico.noLikesRecibidos.all():
            result.append(musico)

    musico = result[0]
    nombre = musico.usuario.username + ";"
    generosList = musico.generos.values_list("nombre", flat=True)
    generos = ", ".join(generosList) + ";"
    video = musico.enlaceVideoFormateado + ";"
    id = str(musico.id)

    response = nombre + generos + video + id
    print(response)
    return HttpResponse(response)

@login_required(login_url='/login/')
def getMusico2(request, pkBanda):
    musicos = Musico.objects.all()
    result = []
    banda = get_object_or_404(Banda, id=pkBanda) #ESTO HAY QUE DARLE UN REPASO
    for musico in musicos:
        if banda.administrador.id is not musico.id and musico not in banda.miembros.all() and banda not in musico.likesRecibidosBanda.all() and banda not in musico.noLikesRecibidosBanda.all():
            result.append(musico)

    musico = result[0]
    nombre = musico.usuario.username + ";"
    generosList = musico.generos.values_list("nombre", flat=True)
    generos = ", ".join(generosList) + ";"
    video = musico.enlaceVideoFormateado + ";"
    id = str(musico.id)

    response = nombre + generos + video + id
    print(response)
    return HttpResponse(response)

@login_required(login_url='/login/')
def getBanda(request):
    bandas = Banda.objects.all()
    result = []
    user = request.user
    musico = Musico.objects.get(usuario=user)
    for banda in bandas:
        if musico.id is not banda.administrador.id and user not in banda.likesRecibidosMusico.all() and user not in banda.noLikesRecibidosMusico.all():
            result.append(banda)
    banda = result[0]
    nombre = banda.nombre + ";"
    generosList = banda.generos.values_list("nombre", flat=True)
    generos = ", ".join(generosList) + ";"
    video = banda.enlaceVideoFormateado + ";"
    id = str(banda.id)

    response = nombre + generos + video + id
    return HttpResponse(response)

@login_required(login_url='/login/')
def getBanda2(request, pkBanda):
    bandas = Banda.objects.all()
    result = []
    banda = get_object_or_404(Banda, id=pkBanda) #ESTO HAY QUE DARLE UN REPASO
    usuario = request.user
    for b in bandas:
        if usuario.id is not b.administrador.usuario.id and banda not in b.likesRecibidosBanda.all() and banda not in b.noLikesRecibidosBanda.all():
            result.append(b)
    banda = result[0]
    nombre = banda.nombre + ";"
    generosList = banda.generos.values_list("nombre", flat=True)
    generos = ", ".join(generosList) + ";"
    video = banda.enlaceVideoFormateado + ";"
    id = str(banda.id)

    response = nombre + generos + video + id
    return HttpResponse(response)

@login_required(login_url='/login/')
def listadoMusicos(request):
    musicos = Musico.objects.all().order_by('-isBoosted')
    result = []
    usuario = request.user
    for musico in musicos:
        if usuario.id is not musico.usuario.id and usuario not in musico.likesRecibidos.all() and usuario not in musico.noLikesRecibidos.all():
            result.append(musico)
    print(result)        
    context = {
        'musicos': result,
        'usuario': usuario,
    }

    return context

@login_required(login_url='/login/')
def listadoBandas(request):
    bandas = Banda.objects.all()
    result = []
    usuario = request.user
    for banda in bandas:
        if usuario.id is not banda.administrador.id and usuario not in banda.likesRecibidosMusico.all() and usuario not in banda.noLikesRecibidosMusico.all():
            result.append(banda)
    context = {
        'bandas': result,
        'usuario': usuario,
    }
    return render(request, "../templates/listadoBandas.html", context)

@login_required(login_url='/login/')
def listadoBandasMusicos(request, pkBanda):
    banda = get_object_or_404(Banda, id=pkBanda)
    usuario = request.user
    if(banda.administrador == usuario):
        musicos = Musico.objects.all()
        result = []
        for musico in musicos:
            if banda.administrador.id is not musico.id and musico not in banda.miembros.all() and banda not in musico.likesRecibidosBanda.all() and banda not in musico.noLikesRecibidosBanda.all():
                result.append(musico)
        context = {
            'musicos': result,
            'usuario': usuario,
            'pkBanda': pkBanda,
        }
        return render(request, "../templates/listadoBandasMusicos.html", context)
    else:
        return redirect("/")
@login_required(login_url='/login/')
def listadoBandasBandas(request, pkBanda):
    bandas = Banda.objects.all()
    banda = get_object_or_404(Banda, id=pkBanda)
    result = []
    usuario = request.user
    for b in bandas:
        if usuario.id is not b.administrador.usuario.id and banda not in b.likesRecibidosBanda.all() and banda not in b.noLikesRecibidosBanda.all():
            result.append(b)
    context = {
        'bandas': result,
        'usuario': usuario,
        'pkBanda': pkBanda,
    }
    return render(request, "../templates/listadoBandasBandas.html", context)

@login_required(login_url='/login/')
def listadoMisBandas(request):
    misBandas = Banda.objects.all().filter(administrador=request.user.musico).order_by('-nombre')
    bandasMiembro = Banda.objects.all().filter(miembros__id__contains=request.user.musico.id).order_by('-nombre')
    return render(request, "misBandas.html", {'misBandas': misBandas, 'bandasMiembro':bandasMiembro})

@login_required(login_url='/login/')
def listadoMiembrosNoRegistrados(request):
    misMiembrosNoRegistrados = MiembroNoRegistrado.objects.all().filter(banda=request.user.pk).order_by('-nombre')
    return render(request, "misBandas.html", {'misMiembrosNoRegistrados': misMiembrosNoRegistrados})

@login_required(login_url='/login/')
def listadoGeneros(request):
    currentUser = Musico.objects.get(id=request.user.pk)
    generos = Genero.objects.all()
    context = {'generos': generos}
    return render(request, '../templates/generos.html', context)

@login_required(login_url='/login/')
def listadoMisInvitaciones(request):
    misInvitaciones = Invitacion.objects.all().filter(receptor=request.user.musico)
    return render(request, "misInvitaciones.html", {'misInvitaciones': misInvitaciones})

@login_required(login_url='/login/')
def listadoChats(request):
    musico = Musico.objects.get(id=request.user.pk)
    chats = Chat.objects.all()
    result = [] 
    for chat in chats:
        if chat in musico.chat.all():
            result.append(chat)
    return result

@login_required(login_url='/login/')
def chat_room(request, room_name):
    print(room_name)
    if room_name == "listado":
        aux = ""
    else:
        lista = room_name.split("-")
        if lista[0] == str(request.user.id):
            aux = User.objects.get(id=int(lista[1]))
        elif lista[0] != str(request.user.id):
            aux = User.objects.get(id=int(lista[0]))

    user_o=User.objects.get(id=request.user.id)
    musico = Musico.objects.get(usuario=user_o)
    chats = Chat.objects.all()
    loged_id = request.user.id
    result = []
    for chat in chats:
        if chat in musico.chat.all():
            chat_name=chat.nombre.split("/")
            users_id=chat_name[-1].split("-")
            if users_id[0] == str(loged_id):
                other_id=users_id[1]
            elif users_id[0] != str(loged_id):
                other_id=users_id[0]
            other_user = User.objects.get(id=other_id)
            other_musico = Musico.objects.get(usuario=other_user)
            url_name_chat = [chat.nombre+'/', other_musico]
            result.append(url_name_chat)
            
    if room_name == "listado":
        aux = ""
        return render(request, 'chat_room.html', {
        'room_name': room_name, 'chat_list': result, 'path': request.path, 'username': mark_safe(json.dumps(request.user.username)),
})
    else:
        lista = room_name.split("-")
        if lista[0] == str(request.user.id):
            aux = User.objects.get(id=int(lista[1]))
        elif lista[0] != str(request.user.id):
            aux = User.objects.get(id=int(lista[0]))
        return render(request, 'chat_room.html', {
        'room_name': room_name, 'chat_list': result, 'path': request.path, 'username': mark_safe(json.dumps(request.user.username)),'other': mark_safe(json.dumps(aux.username)),
})
    
    
def last_30_messages(sender, receiver):
        return Message.objects.filter(Q(author=sender) | Q(author=receiver)).filter(Q(receptor=sender) | Q(receptor=receiver)).order_by('timestamp').all()[:30]

@login_required(login_url='/login/')
def error(request):
    return render(request, 'error.html')

def showBanda(request, id):
    banda = Banda.objects.filter(pk=id)
    return render(request, "showBanda.html", {'banda': banda})