// MENU ANIMATION EVENT
$( document ).ready(function() {

    var leftMenu = false;
     $("#toogle_left").click(function() {
       if (!leftMenu) {
         $("#toogle_left").animate({left: "0%"});
         $("#layerLegendId").animate({left: "0%"});
         leftMenu = true;
       }
       else {
         $("#toogle_left").animate({left: "23%"});
         $("#layerLegendId").animate({left: "23%"});
         leftMenu = false;     
       }
     });
 
 
 
     var rightMenu = false;
     $("#toogle_right").click(function() {
       if (!rightMenu) {
         $("#toogle_right").animate({right: "0%"});
         rightMenu = true;
       }
       else {
         $("#toogle_right").animate({right: "20%"});
         rightMenu = false;     
       }
     });
 
 });
    
    $(document).ready(function() {

    populate('#timePicker');

     $('select').material_select();


    
    });


  function populate(selector) {
    var select = $(selector);
    var hours, minutes, ampm;
    for (var i = 0; i <= 1450; i += 60) {
        hours = Math.floor(i / 60);
        minutes = i % 60;
        if (minutes < 10) {
            minutes = '0' + minutes; // adding leading zero to minutes portion
        }
        //add the value to dropdownlist
        select.append($('<option></option>')
            .attr('value', hours + ':' + minutes)
            .text(hours + ':' + minutes));
    }
}

   ////////////////