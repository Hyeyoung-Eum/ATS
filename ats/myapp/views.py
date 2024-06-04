from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import User, GameResult, Photo
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import os
# Create your views here.
def home(request):
    users = User.objects.all().order_by('-wins', '-draws', 'losses')
    photos = Photo.objects.all().order_by('-uploaded_at')[:2]

    return render(request, 'home.html', {'users':users, 'photos':photos})


def rankings(request, season):
    if season == "all":
        users = User.objects.all().order_by('-wins', '-draws', 'losses')
    else:
        users = User.objects.filter(
            games_as_player_a__season=season
        ).distinct().order_by('-wins', '-draws', 'losses')
    users_data = [
        {'id': user.id, 'name': user.name, 'wins': user.wins, 'draws': user.draws, 'losses': user.losses}
        for user in users
    ]
    return JsonResponse({'users': users_data})


@csrf_exempt
def add(request):
    users = User.objects.all()
    if request.method =='POST':
        player_a_name = request.POST['player_a_name']
        player_b_name = request.POST['player_b_name']
        score_a = int(request.POST['score_a'])
        score_b = int(request.POST['score_b'])
        season = int(request.POST['season'])

        player_a = User.objects.get(name=player_a_name)
        player_b = User.objects.get(name=player_b_name)
        if score_a > score_b:
            player_a.wins += 1
            player_b.losses += 1
        elif score_a < score_b:
            player_b.wins += 1
            player_a.losses += 1
        else:
            player_a.draws += 1
            player_b.draws += 1

        player_a.save()
        player_b.save()

        # GameResult 모델에 데이터 저장
        game_result = GameResult(
            datetime=timezone.now(),
            player_a=player_a,
            player_b=player_b,
            score_a=score_a,
            score_b=score_b,
            season=season  # season 필드에 폼에서 받은 값을 사용
        )
        game_result.save()

        return redirect('home')
                # 점수 비교 및 User 데이터 업데이트
    else:
        return render(request, 'add.html', {'users':users})

def addplayer(request):
    if request.method == 'POST':
        player_name = request.POST['player_name']
        # 사용자 이름이 이미 존재하는지 확인
        messages=''
        if User.objects.filter(name=player_name).exists():
            message = '이름이 이미 존재합니다.'
            return render(request, 'addplayer.html', {'message':message})
        else:
            new_user = User.objects.create(name=player_name)
            return redirect('home')
    return render(request, 'addplayer.html')

def resultlist(request):
    today = timezone.localtime(timezone.now()).date()
    todays_games = GameResult.objects.filter(datetime__date=today)
    past_games = GameResult.objects.filter(datetime__date__lt=today)
    return render(request, 'resultlist.html', {'todays_games':todays_games, 'past_games':past_games})

def personal(request, personal_id):
    personal_data=User.objects.get(id=personal_id)
    users = User.objects.all().order_by('id')
    user_index_map = {user.id: index for index,user in enumerate(users)}

    personal_results = GameResult.objects.filter(
        player_a=personal_data.id
    ) | GameResult.objects.filter(
        player_b=personal_data.id
    )

    score_matrix=[[0,0,0] for _ in range(len(users))] #승무패

    for result in personal_results:
        if result.player_a.id == personal_data.id: #player_a일 때
            row_num=user_index_map[result.player_b.id]
            if result.score_a > result.score_b:
                score_matrix[row_num][0] +=1 #승리
            elif result.score_a == result.score_b:
                score_matrix[row_num][1] +=1 #무승부
            else: #패배
                score_matrix[row_num][2] +=1
        elif result.player_b.id == personal_data.id: #player_b일 때
            row_num=user_index_map[result.player_a.id]
            if result.score_a > result.score_b:
                score_matrix[row_num][2] +=1 #패배
            elif result.score_a == result.score_b:
                score_matrix[row_num][1] +=1
            else: #승리
                score_matrix[row_num][0] +=1

    personal_results = personal_results.order_by("datetime")

    users_scores = zip(users, score_matrix)

    return render(request, 'personal.html',{'personal_data':personal_data, 'personal_results':personal_results, 'users_scores':users_scores } )

def photo_gallery(request):
    photos = Photo.objects.all().order_by('-uploaded_at')
    return render(request, 'photo_gallery.html', {'photos':photos})

def upload_photo(request):
    if request.method == 'POST':
        title = request.POST['title']
        image = request.FILES['image']
        photo = Photo(title=title, image=image)
        photo.save()
        return redirect('/photos')
    return render(request, 'upload_photo.html')