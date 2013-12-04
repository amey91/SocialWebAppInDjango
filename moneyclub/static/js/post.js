$(document).ready(function(){



        var start_event = function(){
                event.preventDefault();
                console.log('start-event')
                var form = $("#start-event");
                var group_id = $(this).attr("id")
                var data = form.serializeArray();
                console.log(form)
                var post = function (response){
                        if (response.stat=="success"){
                                if(response.redirect){
                                        window.location.href = response.redirect;
                                }
                                
                        } else {
                                alert(response.errors);
                        }
                }

                var args = {type:"POST", 
                            url: "/moneyclub/groups/start_event", 
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

        //$("#post-article").submit();
        //$("button.post-article").on('click', post_article);
        $("button.start-event").on('click',start_event);

});