$(document).ready(function(){
// Animate the element's value from x to y:

          var from = 0;
          var to = parseInt($(".count").text());
          $({count:from}).animate({count: to}, {
              duration: 2500,
              easing: 'swing', // can be anything
              
              step: function () { // called on every step
                  // Update the element's text with rounded-up value:
                  $('.count').text(commaSeparateNumber(Math.round(this.count)));
                                      
              }


          });

          function commaSeparateNumber(val) {
              console.log(val)
              while (/(\d+)(\d{3})/.test(val.toString())) {
                  val = val.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
              }
              return val;
          }
          

  /*
counts = {};
 
      function format_number(text){
          
          return text.replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
      };
       
      function magic_number(element_name, value) {
          var elem = $(element_name);
          var current = counts[element_name] || 0;
          $({count: current}).animate({count: value}, {
                                      duration: 2000,
                                      easing: 'swing',
                                      step: function() {
                                        var text=format_number(String(parseInt(this.count)))
                                        console.log(text)
                                          elem.text(format_number(String(Math.round(parseInt(this.count)))));
                                      }});
                                      counts[element_name] = value;
      };
magic_number('.count', $('.count').text());
*/
})