from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.timezone import timedelta
from django.utils.dateparse import parse_datetime

from OnlineFiveinaRow.forms import LoginForm, RegistrationForm, ProfileForm
from OnlineFiveinaRow.models import *

import json

chessboard_sum = 36
row_length = 6
Chessboard.objects.all().delete()
for i in range(chessboard_sum):
    if i % row_length == 0:
        new_chessboard = Chessboard(board_id = i + 1,
                                    isFirstinaRow = True,
                                    isLastinaRow = False,
                                    last_refresh_time = timezone.now())
        new_chessboard.save()
    elif i % row_length == row_length - 1:
        new_chessboard = Chessboard(board_id = i + 1,
                                    isFirstinaRow = False,
                                    isLastinaRow = True,
                                    last_refresh_time = timezone.now())
        new_chessboard.save()
    else:
        new_chessboard = Chessboard(board_id = i + 1,
                                    isFirstinaRow = False,
                                    isLastinaRow = False,
                                    last_refresh_time = timezone.now())
        new_chessboard.save()

# Create your views here.
def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'OnlineFiveinaRow/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'OnlineFiveinaRow/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)

    return redirect(reverse('matchmaking'))

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'OnlineFiveinaRow/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'OnlineFiveinaRow/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'])
    new_user.is_active = False
    new_user.save()

    new_profile = Profile(username=form.cleaned_data['username'],
                          game_sum=0,
                          win_sum=0)
    new_profile.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
Please click the link below to verify your email address and
complete the registration of your account:

  http://{host}{path}
""".format(host=request.get_host(), 
           path=reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="shenqiz@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'OnlineFiveinaRow/needs-confirmation.html', context)

def confirm_action(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()

    return render(request, 'OnlineFiveinaRow/confirmed.html', {})

def matchmaking_action(request):
    if request.method == 'GET':
        chessboards = Chessboard.objects.all()
        context = {'chessboards': chessboards}
        return render(request, 'OnlineFiveinaRow/matchmaking.html', context)

    if request.method == 'POST':
        board_id = request.POST['board_id']
        chessboard = Chessboard.objects.get(board_id = board_id)
        position_id = request.POST['position_id']
        # print(board_id, position_id)
        if position_id == '1':
            chessboard.user_id1 = request.user.id
            chessboard.username1 = request.user.username
            print(chessboard.user_id1, chessboard.username1, chessboard.current_user)
        elif position_id == '2':
            chessboard.user_id2 = request.user.id
            chessboard.username2 = request.user.username
        else:
            print('Invalid position_id!')
        chessboard.last_refresh_time = timezone.now()
        chessboard.save()
        return redirect(reverse('room', kwargs={'board_id':board_id}))

def matchmaking_refresh_action(request):
    if request.method == 'GET':
        last_refresh_time = parse_datetime(request.GET['last_refresh_time'])
        chessboards_to_add = Chessboard.objects.filter(last_refresh_time__gte = last_refresh_time + timedelta(seconds=-20))
        response_text = serializers.serialize('json', chessboards_to_add)
        return HttpResponse(response_text, content_type='application/json')

def room_action(request, board_id):
    if request.method == 'GET':
        chessboard = Chessboard.objects.get(board_id = board_id)
        context = {}
        try:
            profile1 = Profile.objects.get(username = chessboard.username1)
            context['profile1'] = profile1
        except Profile.DoesNotExist:
            context['profile1'] = "none"
        try:
            profile2 = Profile.objects.get(username = chessboard.username2)
            context['profile2'] = profile2
        except Profile.DoesNotExist:
            context['profile2'] = "none"
        if request.user.id == chessboard.user_id1:
            isReady = chessboard.isReady1
        elif request.user.id == chessboard.user_id2:
            isReady = chessboard.isReady2
        if isReady == True:
            context['disabled'] = "true"
        else:
            context['disabled'] = "false"
        return render(request, 'OnlineFiveinaRow/room.html', context)
    if request.method == 'POST':
        print(request.POST)
        chessboard = Chessboard.objects.get(board_id = board_id)
        if 'quit_button' in request.POST:
            if request.user.id == chessboard.user_id1:
                chessboard.user_id1 = 0
                chessboard.username1 = "Vacant"
                chessboard.isReady1 = False
            elif request.user.id == chessboard.user_id2:
                chessboard.user_id2 = 0
                chessboard.username2 = "Vacant"
                chessboard.isReady2 = False
            chessboard.last_refresh_time = timezone.now()
            chessboard.save()
            return redirect(reverse('matchmaking'))
        elif 'ready_button' in request.POST:
            if request.user.id == chessboard.user_id1:
                chessboard.isReady1 = True
            elif request.user.id == chessboard.user_id2:
                chessboard.isReady2 = True
            chessboard.last_refresh_time = timezone.now()
            chessboard.save()
            context = {}
            try:
                profile1 = Profile.objects.get(username = chessboard.username1)
                context['profile1'] = profile1
            except Profile.DoesNotExist:
                context['profile1'] = "none"
            try:
                profile2 = Profile.objects.get(username = chessboard.username2)
                context['profile2'] = profile2
            except Profile.DoesNotExist:
                context['profile2'] = "none"
            context['disabled'] = "true"
            return render(request, 'OnlineFiveinaRow/room.html', context)

def room_refresh_action(request):
    print("enter room_refresh_action")
    board_id = request.GET['board_id']
    chessboard = Chessboard.objects.get(board_id = board_id)
    if chessboard.isReady1 == True and chessboard.isReady2 == True:
        response_text = {'begin_game': "yes"}
        chessboard.current_user = chessboard.username1
        chessboard.save()
    else:
        response_text = {'begin_game': "no"}
    return HttpResponse(json.dumps(response_text), content_type='application/json')

def profile_me_action(request):
    if request.method == 'GET':
        profile_me = Profile.objects.get(username=request.user.username)
        record_col = profile_me.game_records.all()
        context={'profile': profile_me, 'all_record': record_col}
        return render(request, 'OnlineFiveinaRow/profile_me.html', context)

    if request.method == 'POST':
        profile_me = Profile.objects.get(username=request.user.username)
        record_col = profile_me.game_records.all()
        if 'picture' not in request.POST:
            profile_me.picture.delete()
            form = ProfileForm(request.POST, request.FILES, instance=profile_me)
            if form.is_valid():
                pic = form.cleaned_data['picture']
                print('Uploaded picture: {} (type={})'.format(pic, type(pic)))
                profile_me.content_type = form.cleaned_data['picture'].content_type
                form.save()
        context = {'profile': profile_me, 'all_record': record_col}
        return render(request, 'OnlineFiveinaRow/profile_me.html', context)

def get_photo(request, profile_id):
	profile = get_object_or_404(Profile, id=profile_id)
	print('Picture #{} fetched from db: {} (type={})'.format(id, profile.picture, type(profile.picture)))

	# Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
	if not profile.picture:
		raise Http404
	return HttpResponse(profile.picture, content_type=profile.content_type)

def InitiateBoard(request,boardid):
    context={}
    Current_chess_col=Chesspiece.objects.filter(board_index=boardid)
    cur_board = Chessboard.objects.get(board_id=boardid)
    username_left = cur_board.username1
    username_right = cur_board.username2
    if len(Current_chess_col)==0:
        id=1
        row_index=1
        column_index=1
        while row_index<=15:
            column_index=1
            while column_index<=15:
                new_chess_piece = Chesspiece(board_index=boardid,
            	                    row_index=row_index,
                                    column_index=column_index,
                                    status = 0,
                                    id_on_board = (row_index-1)*15+column_index,
                                    color = '#FFE4B5')
                new_chess_piece.save()
                print(row_index)
                print(column_index)
                column_index=column_index+1
            row_index=row_index+1
        all_chess=Chesspiece.objects.all()
        context={'all_chess':all_chess,'board_id':boardid,'u_l':username_left,'u_r':username_right}
        return render(request,'OnlineFiveinaRow/OnlineFiveinaRow.html',context)
    else:
        context={'board_id':boardid,'u_l':username_left,'u_r':username_right}
        print("other board transfer borad id")
        print(boardid)
        return render(request,'OnlineFiveinaRow/OnlineFiveinaRow.html',context)


    

    

def OnlineFiveinaRow(request):
    context={}
    if request.method=='POST':
        # boardid=request.POST['boardid']
        boardid=request.POST['boardid']
        chessid=request.POST['chessid']
        currentchess=get_object_or_404(Chesspiece,id_on_board=chessid,board_index=boardid)
        print("find chess")
        print(currentchess.id_on_board)
        print("current board id ")
        print(boardid)
        cur_user=User.objects.get(username=request.user.username)
        cur_board=Chessboard.objects.get(board_id=boardid)
        last_chess_id=cur_board.current_chess_id
        print("current user")
        print(cur_user.username)
        print(cur_board.board_id)
        print(cur_board.current_user)

        if cur_user.username==cur_board.current_user:
            print(cur_user.username)
            if cur_user.username==cur_board.username1:
                currentchess.color="black"
                currentchess.status=1
                current_status=1
                current_color="black"
                cur_board.current_user=cur_board.username2
            else:
            	currentchess.color="white"
            	currentchess.status=2
            	current_status=2
            	current_color="white"
            	cur_board.current_user=cur_board.username1

            currentchess.sequence_index=last_chess_id+1
            cur_board.current_chess_id=last_chess_id+1
            print("current chess amount")
            print(cur_board.current_chess_id)
            print("newest chess id")
            print(currentchess.sequence_index)

            currentchess.save()
            cur_board.save()
        # all_chess=Chesspiece.objects.all()
        
        # decide whether the game ends
            c_row_index=currentchess.row_index
            c_column_index=currentchess.column_index
            endofgame='no'
            winner='notyet'
            print("place")
            print(c_row_index)
            print(c_column_index)


        # first direction - -
            f_row_index=c_row_index
            f_column_index=c_column_index-1
            num_1=0
            num_2=0
            while f_column_index>=1:
                if Chesspiece.objects.get(board_index=boardid,column_index=f_column_index, row_index=f_row_index).status==current_status:
                    num_1=num_1+1
                    f_column_index=f_column_index-1
                else:
                    break
            print("left number")
            print(num_1)
            f_column_index=c_column_index+1
            while f_column_index<=15:
                if Chesspiece.objects.get(board_index=boardid,column_index=f_column_index, row_index=f_row_index).status==current_status:
                    num_2=num_2+1
                    f_column_index=f_column_index+1
                else:
                    break
            print("right number")
            print(num_2)
            print("endofcalculation")
    
            if num_1+num_2+1>=5:
                winner=cur_user.username
                cur_board.endofgame=True
                context={'winner':winner}
                endofgame='yes'
            # print("endofgame")
            # return render(request,'OnlineFiveinaRow/endofgame.html',context)

        # second direction
            f_row_index=c_row_index-1
            f_column_index=c_column_index
            num_1=0
            num_2=0
            while f_row_index>=1:
                if Chesspiece.objects.get(board_index=boardid,column_index=f_column_index, row_index=f_row_index).status==current_status:
                    num_1=num_1+1
                    f_row_index=f_row_index-1
                else:
                    break
            print("left number")
            print(num_1)
            f_row_index=c_row_index+1
            while f_row_index<=15:
                if Chesspiece.objects.get(board_index=boardid,column_index=f_column_index, row_index=f_row_index).status==current_status:
                    num_2=num_2+1
                    f_row_index=f_row_index+1
                else:
                    break
            print("right number")
            print(num_2)
            print("endofcalculation")
        
            if num_1+num_2+1>=5:
                winner=cur_user.username
                cur_board.endofgame=True
                context={'winner':winner}
                endofgame='yes'

        # third direction
            f_row_index=c_row_index-1
            f_column_index=c_column_index-1
            num_1=0
            num_2=0
            while (f_column_index>=1 and f_row_index>=1):
                if Chesspiece.objects.get(board_index=boardid,column_index=f_column_index, row_index=f_row_index).status==current_status:
                    num_1=num_1+1
                    f_column_index=f_column_index-1
                    f_row_index=f_row_index-1
                else:
                    break
            print("left number")
            print(num_1)
            f_column_index=c_column_index+1
            f_row_index=c_row_index+1
            while (f_column_index<=15 and f_row_index<=15):
                if Chesspiece.objects.get(board_index=boardid,column_index=f_column_index, row_index=f_row_index).status==current_status:
                    num_2=num_2+1
                    f_column_index=f_column_index+1
                    f_row_index=f_row_index+1
                else:
                    break
            print("right number")
            print(num_2)
            print("endofcalculation")
        
            if num_1+num_2+1>=5:
                winner=cur_user.username
                cur_board.endofgame=True
                context={'winner':winner}
                endofgame='yes'

        # forth direction
            f_row_index=c_row_index+1
            f_column_index=c_column_index-1
            num_1=0
            num_2=0
            while (f_column_index>=1 and f_row_index<=15):
                if Chesspiece.objects.get(board_index=boardid,column_index=f_column_index, row_index=f_row_index).status==current_status:
                    num_1=num_1+1
                    f_column_index=f_column_index-1
                    f_row_index=f_row_index+1
                else:
                    break
            print("left number")
            print(num_1)
            f_column_index=c_column_index+1
            f_row_index=c_row_index-1
            while (f_column_index<=15 and f_row_index>=1):
                if Chesspiece.objects.get(board_index=boardid,column_index=f_column_index, row_index=f_row_index).status==current_status:
                    num_2=num_2+1
                    f_column_index=f_column_index+1
                    f_row_index=f_row_index-1
                else:
                    break
            print("right number")
            print(num_2)
            print("endofcalculation")
        
            if num_1+num_2+1>=5:
                winner=cur_user.username
                cur_board.endofgame=True
                context={'winner':winner}
                endofgame='yes'


        # no match, game continue
            new_color=current_color
            cur_board.save()
            response_text={"new_color":new_color,"chessid":chessid,"endofgame":endofgame,"winner":winner,"alert":"no","boardid":boardid}
        # context={'all_chess':all_chess}
            return HttpResponse(json.dumps(response_text),content_type='application/json')
        else:
        	response_text={"alert":'yes'}
        	return HttpResponse(json.dumps(response_text),content_type='application/json')
    return render(request,'OnlineFiveinaRow/OnlineFiveinaRow.html',context)


def refresh_board(request):
    print("refresh board id")
    print(request.GET['boardid'])
    cur_board=Chessboard.objects.get(board_id=request.GET['boardid'])
    cur_username=cur_board.current_user
    cur_board_id=request.GET['boardid']

    if cur_board.endofgame==True:
        if cur_username==request.user.username:
            response_text={"endofgame":"yes","winner":"not you","board_id":request.GET['boardid']}
        else:
            response_text={"endofgame":"yes","winner":"you","board_id":request.GET['boardid']}
        # game ends, reset the state to the initial parameters
        cur_board.endofgame = False
        # cur_board.current_user = "Vacant"
        cur_board.current_chess_id = 0
        cur_board.save()
        return HttpResponse(json.dumps(response_text),content_type='application/json')
    else:
        newest_chess_index=cur_board.current_chess_id
        if newest_chess_index==0:
            new_color="#FFE4B5"
            newest_chess_id=1
        else:
            newest_chess=Chesspiece.objects.get(board_index=request.GET['boardid'],sequence_index=newest_chess_index)
            new_color=newest_chess.color
            newest_chess_id=newest_chess.id_on_board
        response_text={"new_color":new_color,"chessid":newest_chess_id,"endofgame":"no","board_id":request.GET['boardid']}
        return HttpResponse(json.dumps(response_text),content_type='application/json')

        # new_color="#FFE4B5"
        # newest_chess_id=1
        # response_text={"new_color":new_color,"chessid":newest_chess_id,"endofgame":"no"}
        # return HttpResponse(json.dumps(response_text),content_type='application/json')




def endofgame(request):
    print("reach the view function of endofgame")
    context={}
    winner = request.GET["winner"]
    board_id = request.GET["board_id"]
    print("winner = " + str(winner))
    print("board_id = " + str(board_id))
    chessboard = Chessboard.objects.get(board_id = board_id)
    
    if chessboard.current_user != "Vacant":
        all_pieces = Chesspiece.objects.filter(board_index = board_id,sequence_index__gt=0).order_by('sequence_index')
        print("number of pieces")
        print(len(all_pieces))
        result_string = ''
        for each_piece in all_pieces:
            print(each_piece.id_on_board)
            print(each_piece.sequence_index)
            result_string = result_string + str(each_piece.id_on_board) + ' '
        new_game_record = Gamerecord(process_record=result_string)
        new_game_record.save()

        profile_a = Profile.objects.get(username=chessboard.username1)
        profile_b = Profile.objects.get(username=chessboard.username2)
        profile_a.game_sum = profile_a.game_sum + 1;
        profile_b.game_sum = profile_b.game_sum + 1;
        profile_a.game_records.add(new_game_record)
        profile_b.game_records.add(new_game_record)
        profile_a.save()
        profile_b.save()

        profile_winner = Profile.objects.get(username=request.user.username)
        profile_winner.win_sum = profile_winner.win_sum + 1
        profile_winner.save()

        Chesspiece.objects.filter(board_index = board_id).delete()
        chessboard.isReady1 = False
        chessboard.isReady2 = False
        chessboard.current_user = "Vacant"
        chessboard.save()



    # update in version 19
    # add replay board on end of game page.
    profile_me = Profile.objects.get(username=request.user.username)
    record_col = profile_me.game_records.all().order_by("-ending_time")
    re_game_record = record_col[0];
    record_array=re_game_record.process_record.split(" ")
    record_array_temp=record_array
    record_array_temp.pop()
    counter=0
    while counter<len(record_array_temp):
        record_array_temp[counter]=int(record_array[counter])
        counter=counter+1
    context['winner']= winner
    context['board_id']= board_id
    context['record_array']=json.dumps(record_array_temp)
    return render(request,'OnlineFiveinaRow/endofgame.html',context)


def refresh_page(request):
    all_chess=Chesspiece.objects.all()
    # filter
    context={'all_chess':all_chess}
    return render(request,'OnlineFiveinaRow/Ingame.html',context)


def rebuild_game(request,id):
    re_game_record=Gamerecord.objects.get(id=id)
    time = re_game_record.ending_time
    participant_a=re_game_record.profile_set.all()[0].username
    participant_b=re_game_record.profile_set.all()[1].username
    print(re_game_record.process_record)
    record_array=re_game_record.process_record.split(" ")
    record_array_temp=record_array
    record_array_temp.pop()
    counter=0
    while counter<len(record_array_temp):
        record_array_temp[counter]=int(record_array[counter])
        counter=counter+1
    context={'record_array':json.dumps(record_array_temp), 'p_a':participant_a,'p_b':participant_b, 'time':time}
    return render(request,'OnlineFiveinaRow/gamerebuilding.html',context)
