$(document).ready(function () {  
    $.ajax({
        url : '/displaymyresource',
        type : 'POST',
        contentType: "application/json",
        
        success: function(data){
            console.log(data.my_resource_length)
            $ ("#myresourcelen").text(data.my_resource_length)
    
        $('.myresource')
        .mouseover(function(){
    
            var resource_data =  ""; 
            $.each(data.resources, function(key,value){
                resource_data += '<tr>';
                resource_data += '<td>' + value.resource + '</td>';
                resource_data += '<td>' + value.status + '</td>';
                resource_data += '<td>' + value.end_time + '</td>';
                resource_data += '<td> <button type="button" class="btn btn-primary-release" id = "release-btn" >Release</button></td>';
                resource_data += '</tr>';
        
         });
            $('.hidden-table-myresource').find("tr:gt(0)").remove();
            $('.hidden-table-myresource').append(resource_data);
            $('.hidden-table').css({'display' : "none"});
            $('.hidden-table-tasks').css({'display' : "none"});
           $('.hidden-table-myresource').css({'display' : 'inline-block'});
        
        
        
        });
    
        $(document).on('click', '#release-btn', function(){ 
            console.log("hello");
            $(this).prop('disabled', true);
            
            var $item = $(this).closest("tr")
            $tds = $item.find("td");
            var list = new Array();
            $.each($tds, function() {   
    
                list.push( $(this).text() );       
                console.log($(this).text());       
            });
    
            console.log(list);
    
            var x =  {'r_name' : list[0] };
            $.ajax({
                url : '/releaseresource',
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
    url : '/allresources',
    type : 'POST',
    contentType: "application/json",
    
    success: function(data){
        console.log(data.resources)
        
        $ ("#allresourcelen").text(data.all_resource_length)

    $('.resource')
    .mouseover(function(){



        var resource_data =  ""; 
        $.each(data.resources, function(key,value){
            resource_data += '<tr>';
            resource_data += '<td>' + value.resource + '</td>';
            resource_data += '<td>' + value.status + '</td>';
            resource_data += '<td>' + value.booked_by + '</td>';
            resource_data += '<td>' + value.end_time + '</td>';
            if(value.session == value.booked_by)
            {
                resource_data += '<td style="color:#0000FF" class = "active">' + "Blocked by you" + '</td>';

            }
            else if(value.status == "booked" && value.request_status == "not-requested")
            {
            resource_data += '<td> <button type="button" class="btn btn-primary-request" id = "request-btn" data-toggle="modal" data-target="#myModal" >Request</button></td>';
        
            }

           else if(value.status == "booked" && value.request_status == "pending")
            {
                resource_data += '<td style="color:#FF0000" class = "active">' + "Status Pending" + '</td>';
        
            }

            

            else{
                resource_data += '<td> <button type="button" class="btn btn-primary-book" id = "book-btn" data-toggle="modal" data-target="#myModal" >Book</button></td>'
            }
            resource_data += '</tr>';
    
     });
        $('.hidden-table').find("tr:gt(0)").remove();
        $('.hidden-table').append(resource_data);
        $('.hidden-table-tasks').css({'display' : 'none'});
        $('.hidden-table-myresource').css({'display' : "none"});
        $('.hidden-table').css({'display' : 'inline-block'});
    
    
    
    });

    $(document).on('click', '#request-btn ,#book-btn', function(){ 
        $('#datetimepicker1').datetimepicker({ minDate: 0});
        $(this).prop('disabled', true);
        console.log("hello");
        var $item = $(this).closest("tr")
        $tds = $item.find("td");
        var list = new Array();
        $.each($tds, function() {   

            list.push( $(this).text() );       
            console.log($(this).text());       
        });

        window.list1 = list;

        console.log(list);

     
     
     });
        
        
   

   $(document).on('click', '#bookdate', function(){ 


    var list_copy = window.list1;
    console.log(list_copy);
    console.log("hahha");
    var $endtimetext = $("#endtimetext").val();
    console.log($endtimetext);

    var x =  {'r_name' : list_copy[0] , 'status' : list_copy[1] , 'blocked_by' : list_copy[2] , 'end_time' : $endtimetext };
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
    
}

});


   
    $.ajax({
        url : '/alltasks',
        type : 'POST',
        contentType: "application/json",
        
        success: function(data){
            $ ("#alltasklen").text(data.all_task_length)
    
        $('.tasks')
        .mouseover(function(){
    
    
    
            var resource_data =  ""; 
            $.each(data.resources, function(key,value){
                resource_data += '<tr>';
                resource_data += '<td>' + value.resource + '</td>';
                resource_data += '<td>' + value.status + '</td>';
                resource_data += '<td>' + value.requested_by + '</td>';
                resource_data += '<td>' + value.requested_time + '</td>';
                resource_data += '<td> <button type="button" class="btn btn-primary-approve" id = "approve-btn" >Approve</button></td>';
                resource_data += '</tr>';
        
         });
            $('.hidden-table-tasks').find("tr:gt(0)").remove();
            $('.hidden-table-tasks').append(resource_data);
            $('.hidden-table').css({'display' : "none"});
            $('.hidden-table-myresource').css({'display' : "none"});
            $('.hidden-table-tasks').css({'display' : 'inline-block' });
        
        
        
        });

        $(document).on('click', '#approve-btn', function(){ 
            console.log("hello");
            $(this).prop('disabled', true);

             
            
            var $item = $(this).closest("tr")
            $tds = $item.find("td");
            var list = new Array();
            $.each($tds, function() {   
    
                list.push( $(this).text() );       
                console.log($(this).text());       
            });
    
            console.log(list);
    
            var x =  {'r_name' : list[0] , 'status' : list[1] , 'requested_by' : list[2] , 'request_time' : list[3]};
            $.ajax({
                url : '/approveresource',
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




});