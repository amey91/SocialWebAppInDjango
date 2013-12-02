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
              while (/(\d+)(\d{3})/.test(val.toString())) {
                  val = val.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
              }
              return val;
          }
          


})