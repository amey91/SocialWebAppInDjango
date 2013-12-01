$(document).ready(function(){

	var post_article = function(){
		event.preventDefault();
		var form = $("#post-article");
		alert(form)
		var group_id = $(this).attr("id")
		//var data = form.serializeArray();
		var data = new FormData(form);
		console.log(data)
		var post = function (response){
			//console.log(response)
			//window.location.href = "/moneyclub/groups/article/"+response.article_id;
			
			
			if (response.stat=="success"){
				if(response.redirect){
					window.location.href = response.redirect;
				}
				
			} else {
				alert(response.errors);
			}
		}

		var args = {type:"POST", url: "/moneyclub/groups/post_article", 
					data:data,  
					enctype: "multipart/form-data",
					success: post,
					cache: false,
        			processData:false,
					fail: function(response){
						//console.log(response)
						alert("fail!")
					},
					error: function(response){
						alert(response.errors)
					}
					
				};
		$.ajax(args);

		return false;

	}

	var start_event = function(){
		event.preventDefault();
		var form = $("#start-event");
		var group_id = $(this).attr("id")
		var data = { 'group_id': group_id,
					'form':form.serializeArray()};
		var post = function (response){
			if (response.status=="success"){

			} else {
				alert(response.errors);
			}
		}

		var args = {type:"POST", url: "/moneyclub/groups/start_event", 
					data:data,  
					success:post,
					always: function (response){
						alert("returned!")
					},
					error: function(response){
						console.log(response)
						alert("error!")
					},
					fail: function(response){
						console.log(response)
						alert("fail!")
					}

					};
		$.ajax(args);

		return false;

	}
	var f = $("#post-article");
	var b = $("button.post-article");
	b.click(function(){
    // implement with ajaxForm Plugin
    f.ajaxForm({
      beforeSend: function(){
      	console.log(e)
        l.show();
        b.attr('disabled', 'disabled');
        p.fadeOut();
      },
      success: function(e){
        if (response.stat=="success"){
				if(response.redirect){
					window.location.href = response.redirect;
				}
				
			} else {
				alert(response.errors);
			}
      },
      error: function(e){
      	alert(e)
        b.removeAttr('disabled');
        p.html(e).fadeIn();
      }
    });
  });
	//$("button.post-article").on('click', post_article);
	$("button.start-event").on('click',start_event);

})