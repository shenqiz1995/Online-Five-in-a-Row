function refreshMatchmaking() {
	console.log("enter refreshMatchmaking");
	var nowTime = new Date();
	var nowISOTime = nowTime.toISOString();

	$.ajax({
		url: "/OnlineFiveinaRow/matchmaking_refresh",
		data: "last_refresh_time=" + nowISOTime,
		dataType: "json",
		success: function(response) {
			console.log(response);
			if (Array.isArray(response)) {
                updateMatchmaking(response);
            } else {
                displayError(response.error);
            }
		}
	});
	console.log("leave refreshMatchmaking");
}

function updateMatchmaking(chessboards) {
	console.log("enter updateMatchmaking")
	console.log(chessboards);

	$(chessboards).each(function() {
		tagId1 = "id_position_" + this.fields.board_id + "_1";
		tagElement1 = document.getElementById(tagId1)
		tagElement1.value = this.fields.username1;
		buttonId1 = "id_button_" + this.fields.board_id + "_1";
		buttonElement1 = document.getElementById(buttonId1)
		if (this.fields.user_id1 == 0) {
			buttonElement1.disabled = false;
		} else {
			buttonElement1.disabled = true;
		}
		tagId2 = "id_position_" + this.fields.board_id + "_2";
		tagElement2 = document.getElementById(tagId2)
		tagElement2.value = this.fields.username2;
		buttonId2 = "id_button_" + this.fields.board_id + "_2";
		buttonElement2 = document.getElementById(buttonId2)
		if (this.fields.user_id2 == 0) {
			buttonElement2.disabled = false;
		} else {
			buttonElement2.disabled = true;
		}
	});
}

function refreshRoom() {
	console.log("enter refreshRoom");
	currentUrl = window.location.href;
	lastIndexSlashUrl = currentUrl.lastIndexOf("/");
	subString1 = currentUrl.substring(0, lastIndexSlashUrl);
	lastIndexSlashSub1 = subString1.lastIndexOf("/");
	strTestRoom = subString1.substring(lastIndexSlashSub1 + 1, lastIndexSlashUrl);
	if (strTestRoom == "room") {
		boardId = parseInt(currentUrl.substring(lastIndexSlashUrl + 1, currentUrl.length));
		$.ajax({
			url: "/OnlineFiveinaRow/room_refresh",
			data: "board_id=" + boardId,
			dataType: "json",
			success: function(response) {
				beginGame = response['begin_game']
				if (beginGame == "yes") {
					window.location.href='/OnlineFiveinaRow/initiate/' + boardId;
				} else {
					window.location.href='/OnlineFiveinaRow/room/' + boardId;
				}
			}
		});
	}
}

function loadcheckerboard(){
	document.writeln("<table class='checkerboard'>")
	var id=1;
	for (var i=1;i<=15;i++){
		document.writeln("<tr>");
		for (var j=1;j<=15;j++){
			id=(i-1)*15+j;
			document.writeln("<td><button class='chesspiece' name='chess' id="+id+" value="+id+" style='background-color:#FFE4B5' onclick='putchess("+id+")'></td>");
		}
		document.writeln("</tr>");
	}
	document.writeln("</table>");
}

function testcolor(){
	current_chess=document.getElementById("1");
	current_chess.style.backgroundColor='black';
}


function putchess(chess_id){
	// boardId=parseInt(currentUrl.substring(lastIndexSlashUrl + 1, currentUrl.length));
	boardid=document.getElementsByName("currentboardid")[0].value;
	console.log(chess_id)
	console.log("putchess board id")
	console.log(boardid)
	$.ajax({
        url: "/OnlineFiveinaRow/playchess",
        type: "POST",
        dataType: "json",
        data: "chessid="+chess_id+"&boardid="+boardid+"&csrfmiddlewaretoken="+getCSRFToken(), 
        success: changecolor
        });
}


function changecolor(items){
	console.log("enter_change color");
	console.log(items["alert"]);
	// new_color=jQuery.parseJSON(items["new_color"]);
	if (items["alert"]=="yes"){
		alert("It is not your turn!");
	}
	else{
		endofgame=items["endofgame"];
		if (endofgame=='yes'){
			winner=items["winner"];
			boardid=items["boardid"];
			console.log("end of game!!!!!");
			console.log(boardid);
			window.location.href='/OnlineFiveinaRow/endofgame?winner='+winner+"&board_id="+boardid;
		}
		new_color=items["new_color"];
		chessid=items["chessid"];
		console.log("new_color in next function")
		console.log(new_color)
		console.log("chessid")
		console.log(chessid)
		current_chess=document.getElementById(chessid);
		current_chess.style.backgroundColor=new_color;
		current_chess.disabled=true;
	}		
}


function refreshBoard(){
	currentUrl = window.location.href;
	lastIndexSlashUrl = currentUrl.lastIndexOf("/");
	subString1 = currentUrl.substring(0, lastIndexSlashUrl);
	lastIndexSlashSub1 = subString1.lastIndexOf("/");
	strTestBoard = subString1.substring(lastIndexSlashSub1 + 1, lastIndexSlashUrl);
	console.log("print refresh board temp variable")
	console.log(currentUrl)
	console.log(lastIndexSlashUrl)
	console.log(subString1)
	console.log(lastIndexSlashSub1)
	console.log(strTestBoard)
	if (strTestBoard=="initiate"){
		boardId=parseInt(currentUrl.substring(lastIndexSlashUrl + 1, currentUrl.length));
		console.log("refresh board 111")
		console.log(boardId)
		$.ajax({
			url:"/OnlineFiveinaRow/refreshboard",
			data:"boardid=" + boardId,
			dataType: "json",
			success: changecolor2
		});
	}
}

function changecolor2(items){
	console.log("successfully enter changecolor2");
	console.log(items["chessid"]);
	if (items["endofgame"]=="yes"){
		winner=items["winner"]
		board_id=items["board_id"]
		window.location.href='/OnlineFiveinaRow/endofgame?winner='+winner+"&board_id="+boardid;
	}
	else{
		new_color=items["new_color"];
		chessid=items["chessid"];
		current_chess=document.getElementById(chessid);
		current_chess.style.backgroundColor=new_color;
		current_chess.disabled=true;
	}
}
	

function rebuildboard(){
	document.writeln("<table class='checkerboard'>")
	var id=1;
	for (var i=1;i<=15;i++){
		document.writeln("<tr>");
		for (var j=1;j<=15;j++){
			id=(i-1)*15+j;
			document.writeln("<td><button class='chesspiece' name='chess' id="+id+" style='background-color:#FFE4B5'></td>");
		}
		document.writeln("</tr>");
	}
	document.writeln("</table>");
}

function rebuildcolor(){
	// console.log(record_array);
	for(i in record_array){
		// setTimeout("alert('对不起, 要你久候')", 3000 )
        console.log(record_array[i]);
        var cur_i=record_array[i]
        console.log(cur_i)
        current_chess=document.getElementById(cur_i);
        if (i%2==1){
        	current_chess.style.backgroundColor='white';
        	console.log(cur_i)
        	console.log('white')
        	// sleep(1000);
        }
        else{
        	current_chess.style.backgroundColor='black';
        	// sleep(1000);
        }
        current_chess.innerHTML=""+i;
        // sleep(1000);
    }
}

// function rebuildcolor_test(cur_i){
// 	// console.log(record_array);
// 	// for(i in record_array){
// 		// setTimeout("alert('对不起, 要你久候')", 3000 )
//         // console.log(record_array[i]);
//     // var cur_i=record_array[i]
//     //     console.log(cur_i)
//     current_chess=document.getElementById(cur_i);
//         // if (i%2==1){
//     current_chess.style.backgroundColor='white';
//         	// console.log(cur_i)
//         	// console.log('white')
//         	// sleep(1000);
//         // }
//         // else{
//         // 	current_chess.style.backgroundColor='black';
//         // 	// sleep(1000);
//         // }
//         // current_chess.value=""+i;
//         // // sleep(1000);
//     // }
// }


// get from internet source
// sleep(1000); sleep 1s
function sleep(numberMillis) {
    var now = new Date();
    var exitTime = now.getTime() + numberMillis;
    while (true) {
        now = new Date();
        if (now.getTime() > exitTime)
            return;
    }
}



function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
}

function displayError(message) {
    $("#error").html(message);
}

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        c = cookies[i].trim();
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length);
        }
    }
    return "unknown";
}

window.setInterval(refreshMatchmaking, 20000);
window.setInterval(refreshRoom, 5000);
window.setInterval(refreshBoard,2000);
