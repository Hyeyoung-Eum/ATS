from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=5)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Wins: {self.wins}, Draws: {self.draws}, Losses: {self.losses})"
    
class GameResult(models.Model):
    game_number = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()
    player_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_player_a')
    player_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_player_b')
    score_a = models.IntegerField()
    score_b = models.IntegerField()

    def __str__(self):
        return f"Game {self.game_number} on {self.datetime}: {self.player_a.name} vs {self.player_b.name} ({self.score_a}-{self.score_b})"
