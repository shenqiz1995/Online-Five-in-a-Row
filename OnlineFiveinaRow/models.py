from django.db import models

# Create your models here.
class Chessboard(models.Model):
	board_id          = models.IntegerField(default = 0)
	user_id1          = models.IntegerField(default = 0)
	user_id2          = models.IntegerField(default = 0)
	username1         = models.CharField(max_length = 20, default = "Vacant")
	username2         = models.CharField(max_length = 20, default = "Vacant")
	isFirstinaRow     = models.BooleanField()
	isLastinaRow      = models.BooleanField()
	isReady1          = models.BooleanField(default = False)
	isReady2          = models.BooleanField(default = False)
	last_refresh_time = models.DateTimeField()
	current_user      = models.CharField(max_length = 20, default = "Vacant")
	current_chess_id  = models.IntegerField(default = 0)
	endofgame         = models.BooleanField(default = False)

class Chesspiece(models.Model):
	board_index       = models.IntegerField(default = 0)
	sequence_index    = models.IntegerField(default = 0)
	row_index         = models.IntegerField()
	column_index      = models.IntegerField()
	status            = models.IntegerField()
	id_on_board       = models.IntegerField(default=300)
	color             = models.CharField(max_length=20,default='#FFE4B5')

	# user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	def __str__(self):
		return 'id=' + str(self.id) + ',status="' + str(self.status) + '"'


class Gamerecord(models.Model):
	process_record   = models.CharField(max_length=800)
	ending_time      = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
	username     = models.CharField(max_length = 20)
	picture      = models.FileField(blank=True, upload_to='static/images/')
	content_type = models.CharField(max_length=50)
	game_sum     = models.IntegerField()
	win_sum      = models.IntegerField()
	game_records = models.ManyToManyField(Gamerecord, blank=True)