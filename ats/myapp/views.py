from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User, GameResult
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
# Create your views here.
def home(request):
    users = User.objects.all().order_by('-wins', '-draws', 'losses')
    return render(request, 'home.html', {'users':users})

@csrf_exempt
def add(request):
    users = User.objects.all()
    if request.method =='POST':
        player_a_name = request.POST['player_a_name']
        player_b_name = request.POST['player_b_name']
        score_a = int(request.POST['score_a'])
        score_b = int(request.POST['score_b'])

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
            score_b=score_b
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




