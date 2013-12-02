$(document).ready(function(){

	$(".stock tbody tr").each(function(){
		var tds=$(this).find("td");
		if (tds.eq(2).html() < 0){
			 tds.eq(2).attr("style", "color:red")
            tds.eq(3).attr("style", "color:red")
        } else{
            tds.eq(2).attr("style", "color:green")
            tds.eq(3).attr("style", "color:green")
        }
	});

	var add_stock = function(){
		event.preventDefault();
		var stock_name = $("input.form-control.add-stock").val();
		console.log(stock_name)

		if (stock_name){
			var stock_table = $(".stock  table")

			stock_name = stock_name.toUpperCase();
			var data = {"stock_name": stock_name}
			var add_new_stock=function(response){
				//console.log("response:")
				//console.log(response)

				if (response.status=="success"){
					//console.log(response)
					var info = new Array();
					info[0] = response.stock_name;
					info[1] = response.price;
			        info[2] = response.change;
			        info[3] = response.pctchange;
			        info[4] = response.stock_id;
			        //console.log("price"+price+",change"+change+",pctchange"+pctchange)
			        var tablerow = $("<tr>");
			        for (i=0; i<4; i++){
			        	var td=$("<td>").html(info[i]);
			        	td.appendTo(tablerow)
			        }
			        var span=$("<span>").attr({
			        	class:"glyphicon glyphicon-minus delete-stock",
			        	id: info[4],
			        	style: "color:red;font-size:75%"
			        })
			        var th=$("<th>").append(span)
			        th.appendTo(tablerow)

			        var tds = tablerow.find("td");
			        if (info[2]<0){
			            tds.eq(2).attr("style", "color:red")
			            tds.eq(3).attr("style", "color:red")
			        } else{
			            tds.eq(2).attr("style", "color:green")
			            tds.eq(3).attr("style", "color:green")
			        }

			        tablerow.appendTo(stock_table);
			    	$("span.delete-stock").on('click', delete_stock);

				} else{
					alert(response.errors);
				}
				
			}
		}
		var data={'stock_name': stock_name};
        var args = {type:"POST", 
        			url: "/moneyclub/member/add-stock", 
        			//data:data,  

        			success:add_new_stock,
        			error: function (xhr, ajaxOptions, thrownError) {
				           alert(xhr.status);
				           alert(xhr.responseText);
				           alert(thrownError);
				       }};
        $.ajax(args);
        return false;
	}

	var delete_stock = function(){
		event.preventDefault();
		var e = $(this);
		var id= e.attr("id");
		console.log(e)
		
		var deleted = function(response){
			
			if (response.status=="success"){
                e.parent().parent().remove();

            } else{
            	alert(response.errors)
            }
		}
		
		var data={'stock_id': id};
        var args = {type:"POST", url: "moneyclub/member/delete-stock", data:data,  success:deleted};
        $.ajax(args);
        
        return false;

	}
	$("span.delete-stock").on('click', delete_stock);
	$("div.add-stock span button").on('click', add_stock);

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

});