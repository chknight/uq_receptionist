$(document).ready(function(){
    $("#submit").click(function(event) {
      var text = $("#test-text").val();
      console.log(text);
      $.post("http://104.131.35.172:8888/",
        {
            name: text,
            target : 'description'
        },
        function(data, status){
            alert("Data: " + data + "\nStatus: " + status);
        });
    });
});
