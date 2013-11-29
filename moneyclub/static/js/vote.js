$(document).ready(function(){

	var upvote = function(){
		event.preventDefault();
		var article_id = $(this).parent().id()

		var upvoted = function (response){
			if (response.status=="success"){
				var count = $(this).html()
				$(this).html(count+1)
			} else{
				alert(response.errors)
			}
		}
		var data={'article_id': article_id};
		var args = {type:"POST", url: "/moneyclub/member/upvote", data:data,  success:upvoted};
    	$.ajax(args);
        
	}

	var downvote = function(){
		event.preventDefault();
		var article_id = $(this).parent().id()

		var downvoted = function (response){
			if (response.status=="success"){
				var count = $(this).html()
				$(this).html(count+1)
			}else{
				alert("downvote failed!")
			}
		}
		var data={'article_id': article_id};
		var args = {type:"POST", url: "/moneyclub/member/downvote", data:data,  success:downvoted};
    	$.ajax(args);
        
	}
	

	$("#upvote").on('click', upvote);
	$("#downvote").on('click', downvote);
	
    return false;
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

})