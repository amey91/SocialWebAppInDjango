$(document).ready(function(){

	$("#upvote").each(function(){
		if (!$(this).html())
			$(this).html(0)
	});
	$("#downvote").each(function(){
		if (!$(this).html())
			$(this).html(0)
	});
	var upvote = function(){
		event.preventDefault();
		var article_id = $(this).parent().attr("id")
		var e = $(this)
		var upvoted = function (response){
			console.log(response)
			if (response.status=="success"){
				if (!e.html()){
					//console.log('set button')
					e.html(1)
				} else{
					var count = parseInt(e.html())
					e.html(count+1)
				}

				if ( response.downvoted){
					$("#downvote").each(function(){
						var count = $(this).html()
						$(this).html(count-1)
					});	
				}
				
			} else{
				alert(response.errors)
			}
		}
		var data={'article_id': article_id};
		var args = {type:"POST", url: "/moneyclub/member/upvote", data:data,  success:upvoted};
    	$.ajax(args);
        return false;
	}

	var downvote = function(){
		event.preventDefault();
		var article_id = $(this).parent().attr("id")
		var e = $(this)
		var downvoted = function (response){
			console.log(response)
			if (response.status=="success"){
				if (!e.html()){
					//console.log('set button')
					e.html(1)
				} else{
					var count = parseInt(e.html())
					e.html(count+1)
				}
				if ( response.upvoted){
					$("#upvote").each(function(){
						var count = $(this).html()
						$(this).html(count-1)
					});	
				}
			}else{
				alert(response.errors)
			}
		}
		var data={'article_id': article_id};
		var args = {type:"POST", url: "/moneyclub/member/downvote", data:data,  success:downvoted};
    	$.ajax(args);
        return false;
	}
	

	$("#upvote").on('click', upvote);
	$("#downvote").on('click', downvote);
	
    
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