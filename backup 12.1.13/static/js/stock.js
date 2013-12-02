var req;

// Sends a new request to update the grumbl list in home page                                                                     
function sendRequest() {
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
    req.onreadystatechange = handleResponse;
    req.open("GET", "/moneyclub/member/get-stock-info", true);
    req.send();
}

// This function is called for each request readystatechange,                                                       
// and it will eventually parse the XML response for the request                                                    
function handleResponse() {
    if (req.readyState != 4 || req.status != 200) {
        return;
    }
    var stock_table = $(".stock  table")
    var stock_list = stock_table.find("tbody tr")
    var stock=$(".well.sidebar-nav#stock").find("tbody").find("tr").eq(0)
     var xmlData = req.responseXML;
     
     
     var stocks = xmlData.getElementsByTagName("stock")
     console.log(stocks.length)
     for (var i=0; i<stocks.length; i++){
        var info = new Array();
        info[0] = stocks[i].getElementsByTagName("stockname")[0].textContent;
        info[1] = stocks[i].getElementsByTagName("price")[0].textContent;
        info[2] = stocks[i].getElementsByTagName("change")[0].textContent;
        info[3] = stocks[i].getElementsByTagName("pctchange")[0].textContent;
        var stock_id = stocks[i].getElementsByTagName("stock_id")[0].textContent;
        console.log("price"+info[1]+",change"+info[2]+",pctchange"+info[3])
        //console.log("stock id: "+stock_id);
        //console.log(stock_list.eq(i).attr("id"));
        for (j=0; j<stock_list.length;j++){
            if (parseInt(stock_list.eq(i).attr("id"))==stock_id){
                //console.log ( info[0])
                var tds = stock_list.eq(i).find("td")
                tds.eq(1).html(info[1])
                tds.eq(2).html(info[2])
                tds.eq(3).html(info[3])
                if (info[2]<0){
                    tds.eq(2).attr("style", "color:red")
                    tds.eq(3).attr("style", "color:red")
                } else{
                    tds.eq(2).attr("style", "color:green")
                    tds.eq(3).attr("style", "color:green")
                }
                break;
            } 
        }
        
     }


}

// causes the sendRequest function to run every 10 seconds                                                          
window.setInterval(sendRequest, 10000);



