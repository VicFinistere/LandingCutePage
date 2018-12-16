/* Event listener : Getting answer using button */
$(function() { $('#tchat_button').on('click', function() { sending_text(); }); });

/* Event listener : Getting answer pressing enter */
$(function () { $(document).keypress(function (e) { if (e.which === 13){ sending_text(); }}); });

/* Robot Introduction */
$(function(){ introduction();});

function scroll()
{
    //Debug
    console.debug("Scrolling down the conversation (messaging.js)");

    var tchat_area = document.getElementById('tchat_area');
    tchat_area.scrollTop = tchat_area.scrollHeight;
}

function introduction()
{
    //Debug
    console.debug("Message introduction (messaging.js)");
    var d = new Date();
    var timer = d.toLocaleTimeString();
    $('<p>', {class: 'robot_white_msg', text: "Hello !"}).appendTo('#tchat_area');
    $("<p class='text-center'><small style='font-size:10px;margin-right: 65%;'>"+timer+"</small></p>").appendTo('#tchat_area');
    $('<p>', {class: 'robot_white_msg', text: "Let's tchat !"}).appendTo('#tchat_area');
    $("<p class='text-center'><small style='font-size:10px;margin-right: 65%;'>"+timer+"</small></p>").appendTo('#tchat_area');

    scroll();
}

function clear_text()
{
    //Debug
    console.debug("clear_text (messaging.js)");

    if ($("#text_error").not(':empty'))
    {
        //Debug
        console.debug("Text_error is cleared (messaging.js)");
        $("#text_error").empty();
    }

    if ($("#text_place_area").not(':empty'))
    {
        //Debug
        console.debug("Text_place is cleared (messaging.js)");
        $("#text_place_area").empty();
    }
}

function sending_text()
{
    //Debug
    console.debug("sending_text (messaging.js)");

    clear_text();

    //Getting the input value
    var input_text = $("#input_text").val();

    //Getting the content in page
    var content = $("#answer").html();

    //If the input is filled
    if(input_text !== "")
    {
        //We append the input text
        $('<p>', { class: 'user_blue_msg', text: input_text}).appendTo('#tchat_area');
        var d = new Date();
        var timer = d.toLocaleTimeString();
        $("<small style='font-size:10px;margin:0 auto; margin-left: 65%;'>"+timer+"</small>").appendTo('#tchat_area');
        scroll();
        answer();
    }

    //If the input if empty
    else
    {
        //Warn
        console.debug("No message in input text ! (messaging.js)");

        //It has to be something in input
        var text = "Ask something!...";

        //If it's not already said
        if(content !== text)
        {
            //Debug
            console.debug("Giving empty input text error(messaging.js)");

            //Say it!
            $("#text_error").html(text);
        }
    }
}

function answer()
{
    //Debug
    console.debug("answer (messaging.js))");

    var user_input = $('#tchat_area').children('p.user_blue_msg').last();
    var user_text = user_input.html();
    var user_checked_text = user_text.toLowerCase();

    bot_answering(user_checked_text);

    //Input text value to null
    $("#input_text").val("");

}
