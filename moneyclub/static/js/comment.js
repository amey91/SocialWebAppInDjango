$(document).ready(function(){

	var comment = function (){
		event.preventDefault();
		var form = $("form#comment")
		var url =form.attr("action")
		var data = form.serializeArray();

		var commented = function(response){
			console.log(response)
			if (response.stat=="success"){
				if(response.redirect){
					window.location.href = response.redirect;
				}
				
			} else {
				alert(response.errors);
			} 
		}

		var args = {type:"POST", url: url, 
					data:data,  
					success: commented,
					done: commented,
					cache: false,
        			//processData:false,
					fail: function(response){
						console.log('fail')
						alert("comment failed!")
					},
					error: function(response){
						console.log('errors')
						alert(response.errors)
					}
					
				};
		$.ajax(args);

		return false;
	}	
	//$("form#comment").submit(comment);

	$("button.comment").on('click', comment);


})