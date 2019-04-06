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
     $('select').material_select();

     timePicker();

    });


  // Time Picker
   function timePicker(){
    $('#timePicker').timepicker({
      timeFormat: 'h:mm p',
      interval: 30,
      dynamic: false,
      dropdown: true,
      scrollbar: true
  });
   }

   $('#toggle_pois_timepicker').change(function() {   
    if (this.checked) {
      $('.timePicker').show();

    } else {
        $('.timePicker').hide();        
    }
  });

   ////////////////