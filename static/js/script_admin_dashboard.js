$(document).ready(function () {  

  $.ajax({
    url : '/displayusers',
        type : 'POST',
        contentType: "application/json",
        
        success: function(data){

          console.log(data.users);

          var user_data =  ""; 
            $.each(data.users, function(key,value){
                user_data += '<tr>';
                user_data += '<td>' + value.username + '</td>';
                user_data += '<td>' + value.email + '</td>';
                user_data += '<td> <button class="btn" id = "delete-user-btn"><i class="fa fa-trash"></i></button></td>';
                user_data += '</tr>';
              });

              $('.user-table').find("tr:gt(0)").remove();
              $('.user-table').append(user_data);

              
              $(document).on('click', '#delete-user-btn', function(){ 

                var $item = $(this).closest("tr")
                $tds = $item.find("td");
                var list = new Array();
                $.each($tds, function() {   
    
                list.push( $(this).text() );       
                console.log($(this).text());       
            });
    
            console.log(list);
            var x =  {'username' : list[0] };
            $.ajax({
                url : '/removeuser',
                type :'POST',
                data : JSON.stringify(x),
                contentType : 'application/json ;charset=UTF-8',
         
                success : function(data)
                {
                    console.log(data.status);
         
         
                } });
               });
              }
            });


  $.ajax({
    url : '/allresources',
        type : 'POST',
        contentType: "application/json",
        
        success: function(data){

          console.log(data.resources);

          var resource_data =  ""; 
            $.each(data.resources, function(key,value){
              resource_data += '<tr>';
              resource_data += '<td>' + value.resource + '</td>';
              resource_data += '<td>' + value.status + '</td>';
              resource_data += '<td>' + value.booked_by + '</td>';
              resource_data += '<td>' + value.end_time + '</td>';

              if(value.status == "booked"){
              resource_data += '<td> <button class="btn" id = "delete-resource-btn" style="margin:15px;"><i class="fa fa-trash"></i></button>      <button type="button" class="btn btn-warning" id = "request-behalf" data-toggle="modal" data-target="#book-resource-admin">Request on behalf</button></td>';
              }
              else
              {
                resource_data += '<td> <button class="btn" id = "delete-resource-btn" style="margin:15px;"><i class="fa fa-trash" ></i></button>    <button type="button" class="btn btn-success" id = "book-behalf"  data-toggle="modal" data-target="#book-resource-admin">Book On behalf</button></td>';
              }
              resource_data += '</tr>';
              });

              $('.resource-table').find("tr:gt(0)").remove();
              $('.resource-table').append(resource_data);

              //Delete resource on button click
              $(document).on('click', '#delete-resource-btn', function(){ 

                var $item = $(this).closest("tr")
                $tds = $item.find("td");
                var list = new Array();
                $.each($tds, function() {   
    
                list.push( $(this).text() );       
                console.log($(this).text());       
            });
    
            console.log(list);
            var x =  {'resource_name' : list[0] };
            $.ajax({
                url : '/removeresource',
                type :'POST',
                data : JSON.stringify(x),
                contentType : 'application/json ;charset=UTF-8',
         
                success : function(data)
                {
                    console.log(data.status);
         
         
                } });
               });
              
              
               $(document).on('click', '#request-behalf , #book-behalf', function(){ 
                $('#book-resource-date').datetimepicker({ minDate: 0});
                var $item = $(this).closest("tr")
                $tds = $item.find("td");
                var list = new Array();
                $.each($tds, function() {   
    
                list.push( $(this).text() );       
                console.log($(this).text());       
            });

            window.list2 = list
            console.log(list);
              
              });

            //Book or Request Resource on behalf of other user
            $(document).on('click', '#submit-book-resource', function(){ 

              
              var user = $("#book-resource-user").val();
              var new_time = $('#endtimetext').val();
              
              var list = window.list2



  
          console.log(list);
          var x =  {'resource_name' : list[0] , 'status' : list[1] , 'blocked_by' : list[2], 'end_time' : list[3] , 'new_owner' : user , 'new_end_time' : new_time};
          console.log(x)
          $.ajax({
              url : '/bookonbehalf',
              type :'POST',
              data : JSON.stringify(x),
              contentType : 'application/json ;charset=UTF-8',
       
              success : function(data)
              {
                  console.log(data.status);
       
       
              } 
            });
             
            });

           


            }
  });

  $.ajax({
    url : '/admintasks',
        type : 'POST',
        contentType: "application/json",
        
        success: function(data){

          console.log(data.tasks);

          var task_data =  ""; 
            $.each(data.tasks, function(key,value){
              task_data += '<tr>';
              task_data += '<td>' + value.resource + '</td>';
              task_data += '<td>' + value.requested_by + '</td>';
              task_data += '<td>' + value.requested_to + '</td>';
              task_data += '<td>' + value.request_time + '</td>';
              task_data += '<td> <button class="btn"><i class="fa fa-trash"></i></button> <button class="btn"><i class="fa fa-check-circle"></i></button></td>';
              task_data += '</tr>';
              });

              $('.task-table').find("tr:gt(0)").remove();
              $('.task-table').append(task_data);


            }
  });
//Add user
  $(document).on('click', '#adduser', function(){

    
    var user = $("#add-username").val();
    var email = $("#add-email").val();
    var password = $("#add-password").val();
    var data = {'username' : user , 'email' : email, 'password' : password};

    console.log(data);
    $.ajax({
      url : '/addusername',
          type : 'POST',
          data : JSON.stringify(data),
          contentType: "application/json",
          
          success: function(data){

            if (data.status) {

              setTimeout(function(){// wait for 5 secs(2)
                location.reload(); // then reload the page.(3)
           }, 5000); 
              
             
          }

          }
        
        });  

    });

//add resource

$(document).on('click', '#addresource', function(){

    
  var r_name = $("#add-resourcename").val();
  var data = {'r_name' : r_name  };

  console.log(data);
  $.ajax({
    url : '/addresource',
        type : 'POST',
        data : JSON.stringify(data),
        contentType: "application/json",
        
        success: function(data){

          if (data.status) {
            setTimeout(function(){// wait for 5 secs(2)
              location.reload(); // then reload the page.(3)
         }, 5000);  
           
        }

        }
      
      });  

  });

  




// Switch between menus
var $content = $('.menu-content');

function showContent(type) {
  $content.hide().filter('.' + type).show();
}

$('.navbar-nav').on('click', '.nav-link', function(e) {
  showContent(e.currentTarget.hash.slice(1));
  e.preventDefault();
}); 

// show 'about' content only on page load (if you want)
showContent('user');

});