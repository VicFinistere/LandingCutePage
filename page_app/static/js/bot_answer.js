var user_input = $('#tchat_area').children('p.user_blue_msg').last();
var robot_input = $('#tchat_area').children('p.robot_white_msg').last();

var sentences = ['bonjour', 'salut', 'coucou'];
var answers = [['coucou', 'bonjour', 'salut'], [], []];

function bot_answering(user_checked_text)
{
    //Log
    console.log("bot_answering (bot_answer.js)");
    $.getJSON($SCRIPT_ROOT + '/get_dialog', {input:user_checked_text},
            function (response)
            {
                //Debug
                console.debug("Using mail personnal API");
                if (response)
                {
                    bot_response(response);
                    scroll();

                }
                else
                {
                    bot_response(user_checked_text);
                    scroll();
                }
            });
    // function get_random_answer(user_checked_text) {
    //     for(var i = 0; i < sentences.length; i++){
    //         if(sentences[i] === user_checked_text ){
    //             var options = answers[i];
    //             var response = options[Math.floor(Math.random() * options.length)];
    //         }
    //     }
    //     if(response){
    //         return response
    //     } else {
    //         return user_checked_text;
    //     }
    // }

    if (true === user_checked_text.indexOf(sentences) !== -1) {
        var random_answer = get_random_answer(user_checked_text);
        bot_response(random_answer);
    } else {
        bot_response('...');
    }
    scroll();
}

function bot_response(response){
    if(user_input.css('color') !== 'rgb(230, 230, 230)'){
        $('<p>', {class: 'robot_white_msg', text:response}).appendTo('#tchat_area');
        var d = new Date();
        var timer = d.toLocaleTimeString();
        $("<p class='text-center'><small style='font-size:10px;margin-right: 65%;'>"+timer+"</small></p>").appendTo('#tchat_area');
        user_input.css('color', 'rgb(230, 230, 230)');
    }
}