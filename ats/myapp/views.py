from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import User, GameResult, Photo
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q, F
from django.utils.timezone import localtime


import os
# Create your views here.
def home(request):
    # 시즌 2의 랭킹 데이터를 불러옴
    season = '2'  # 시즌 2를 기본값으로 설정
    users = get_season_rankings(season)  # 시즌 2의 랭킹 데이터 불러오기
    photos = Photo.objects.all().order_by('-uploaded_at')[:2]
    return render(request, 'home.html', {'users': users, 'photos': photos, 'selected_season': season})

def rankings(request, season):
    users_data = get_season_rankings(season)  # 이 함수는 이제 사전 리스트를 직접 반환
    return JsonResponse({'users': users_data})


def get_season_rankings(season):
    if season == "all":
        users = User.objects.all().order_by('-wins', '-draws', 'losses')
        return [
            {'id': user.id, 'name': user.name, 'wins': user.wins, 'draws': user.draws, 'losses': user.losses}
            for user in users
        ]
    else:
        season = int(season)  # 시즌 값이 문자열로 들어올 경우를 대비하여 정수로 변환
        # 특정 시즌에 해당하는 게임 결과만 가져오기
        game_results = GameResult.objects.filter(season=season)
        user_stats = {}
        # 각 게임 결과에 대해 승, 무, 패 집계
        for result in game_results:
            if result.score_a > result.score_b:
                user_stats[result.player_a_id] = user_stats.get(result.player_a_id, {'wins': 0, 'draws': 0, 'losses': 0})
                user_stats[result.player_a_id]['wins'] += 1
                user_stats[result.player_b_id] = user_stats.get(result.player_b_id, {'wins': 0, 'draws': 0, 'losses': 0})
                user_stats[result.player_b_id]['losses'] += 1
            elif result.score_a == result.score_b:
                user_stats[result.player_a_id] = user_stats.get(result.player_a_id, {'wins': 0, 'draws': 0, 'losses': 0})
                user_stats[result.player_a_id]['draws'] += 1
                user_stats[result.player_b_id] = user_stats.get(result.player_b_id, {'wins': 0, 'draws': 0, 'losses': 0})
                user_stats[result.player_b_id]['draws'] += 1
            else:
                user_stats[result.player_a_id] = user_stats.get(result.player_a_id, {'wins': 0, 'draws': 0, 'losses': 0})
                user_stats[result.player_a_id]['losses'] += 1
                user_stats[result.player_b_id] = user_stats.get(result.player_b_id, {'wins': 0, 'draws': 0, 'losses': 0})
                user_stats[result.player_b_id]['wins'] += 1
        
        # 사용자 정보와 승, 무, 패 정보 매핑
        users = User.objects.filter(id__in=user_stats.keys())
        ranked_users = [
            {'id': user.id, 'name': user.name, 'wins': user_stats[user.id]['wins'], 'draws': user_stats[user.id]['draws'], 'losses': user_stats[user.id]['losses']}
            for user in users
        ]
        # 승수에 따라 내림차순 정렬
        ranked_users.sort(key=lambda x: (-x['wins'], -x['draws'], x['losses']))
        return ranked_users

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
    season = request.GET.get('season', '2')  # 기본적으로 시즌 2를 보여줌
    today = localtime().date()
    
    if season == "all":
        todays_games = GameResult.objects.filter(datetime__date=today).order_by('-datetime')
        past_games = GameResult.objects.filter(datetime__date__lt=today).order_by('-datetime')
    else:
        season = int(season)  # 시즌 번호는 정수로 변환
        todays_games = GameResult.objects.filter(season=season, datetime__date=today).order_by('-datetime')
        past_games = GameResult.objects.filter(season=season, datetime__date__lt=today).order_by('-datetime')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        games = [
            {
                'game_number': game.game_number,
                'datetime': game.datetime.strftime("%Y-%m-%d %H:%M"),
                'player_a': game.player_a.name,
                'player_b': game.player_b.name,
                'score_a': game.score_a,
                'score_b': game.score_b,
            }
            for game in list(todays_games) + list(past_games)
        ]
        return JsonResponse({'games': games})

    return render(request, 'resultlist.html', {
        'todays_games': todays_games, 
        'past_games': past_games,
        'selected_season': season
    })


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