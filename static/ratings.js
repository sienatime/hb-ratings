$( document ).ready(function(){
   $(".graystar").mouseenter(function(){
        /* get the index of this star (via ID), then put it in a loop that turns it and all previous stars blue. */
        var star = $(this).attr("id");
        star = star.split("star");
        var stop = star[1];

        for (var i = 0; i <= stop; i++) {
            $("#star"+i).attr("src", "/static/bluestar.png");
        }
   });
   $(".graystar").mouseleave(function(){
        for (var i = 0; i <= 5; i++) {
            $("#star"+i).attr("src", "/static/graystar.png");
        }
   });

   $(".graystar").click(function(){
        var star = $(this).attr("id");
        star = star.split("star");
        var value = star[1];

        $('#rating_field').attr("value", parseInt(value, 10)+1);
        $('#rating_form').submit();
   });
});