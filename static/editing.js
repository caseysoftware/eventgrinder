
$(function(){
    
    $('#events .editing').each(function(){
        var expose=$('<a href="" class="editlink">edit</a>');
        var hide=$('<a href="">hide</a>');
        var form = this;
        hide.click(function(){
            $(form).hide();
            expose.show();
            hide.hide();
            return false;
        })
        expose.click(function(){
            $(form).show();
            hide.show();
            expose.hide();
            return false;
        })
        $(this).before(expose);
        $(this).before(hide);
        hide.hide()
        
    })
    
})


