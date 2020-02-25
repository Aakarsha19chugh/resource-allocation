$(document).ready(function () {  

$.ajax({
    url : '/allresources',
    type : 'POST',
    contentType: "application/json",
    
    success: function(data){
  
      console.log(data.resources)
    //console.log(data.resources);
    // console.log(data.resources[0]);


      var s = '<option value="-1">Please Select a Resource</option>';  
      for (var i = 0; i < data.resources.length; i++) {  

        s += '<option value="' + data.resources[i] + '">' + data.resources[i] + '</option>'; 
      }  
      $("#resourcesDropdown").html(s);  
      
     }


});

$("#request_button").click(function()

{
   var x =  {'text' : $('#resourcesDropdown').val()}
   console.log(x);
   $.ajax({
       url : '/requestresource',
       type :'POST',
       data : JSON.stringify(x),
       contentType : 'application/json ;charset=UTF-8',

       success : function(data)
       {
           console.log(data.status);

       }


});
});

$("#logout").click(function()

{
    $.ajax({
       url : '/logout',
       type :'POST',
       contentType : 'application/json ;charset=UTF-8',

       success : function(data)
       {
           console.log(data.status);

       }


});
   


});


  
});