// Event listener : Getting answer using button
$(function() { $('#list_button').on('click', function() { sending_text(); }); });
$(function() { $('#mail_button').on('click', function() { send_list(); }); });

// Event listener : Getting answer pressing enter
$(function () { $(document).keypress(function (e) { if (e.which === 13){ sending_text(); }}); });

//Click on a item button
$(document).on("click", ".item", function() { var element = $(event.target); manage_item(element);});

var list_items = [];

// Robot Introduction
$(function(){ introduction();});

//Robot introduction
function introduction()
{

    //Debug
    console.debug("Message introduction (messaging.js)");

    $('<p>', {class: 'robot_white_msg', text: "Hello !"}).appendTo('#text_area');
    $('<p>', {class: 'robot_white_msg', text: "Write something to start a new list!"}).appendTo('#text_area');

    scroll();
}


// Scroll function
function scroll()
{

    //Debug
    console.debug("Scrolling down the conversation (messaging.js)");

    var text_area = document.getElementById('text_area');
    text_area.scrollTop = text_area.scrollHeight;

}

function clear_text()

{

    //Debug
    console.debug("clear_text (messaging.js)");

    // language=JQuery-CSS
    if ($("#text_error").not(':empty'))
    {
        //Debug
        console.debug("Text_error is cleared (messaging.js)");
        $("#text_error").empty();
    }
}

function sending_text()
{
    //Debug
    console.debug("sending_text (messaging.js)");

    clear_text();

    // language=JQuery-CSS
    var input_text = $("#input_text").val();
    $('#input_text').val('');

    //If the input is filled
    if(input_text !== "")
    {

        if(isValidEmailAddress(input_text) )
        {
           send_list();
        }
        else
        {
            $("#text_area").empty();
            //We append the input text
            list_items.push(input_text);
            var counter = -1;
            var item_amount_list = [];

            list_items.forEach(function(element) {
                counter += 1;
                var current_amount = item_amount_list[counter];
                if(current_amount == null){
                    $('<button>', {class: 'item', text: element }).appendTo('#text_area');
                } else {
                    $('<button>', {class: 'item', text: element }).appendTo('#text_area');
                }
            });
        }
    }

    //If the input is empty
    else
    {
        //Warn
        console.debug("No message in input text ! (messaging.js)");

        //It has to be something in input
        var text = "Enter a product name !...";



        //If it's not already said
        if(content !== text)

        {
            //Debug
            console.debug("Giving empty input text error(messaging.js)");

            //Say it!
            // language=JQuery-CSS
            $("#text_error").html(text);

        }

    }

}


function send_list(){
    alert("We will send the list");
    var list = get_list();
    alert(list);
       $.getJSON($SCRIPT_ROOT+'/list', {list:list},
        function (feedback)
        {
            //Debug
            console.debug("Using mail personal API");
            if (feedback == 'Sent')
            {
                $("#text_area").empty();
                $('<p>', {class: 'robot_white_msg', text: "Your list has been sent !"}).appendTo('#text_area');
            }
            else
            {
                $('<p>', {class: 'robot_white_msg', text: "Hum...error..."}).appendTo('#text_area');
                $('<p>', {class: 'robot_white_msg', text: "Your list has not been sent..."}).appendTo('#text_area');
            }
        });
}

function get_list() {
    var current_list = "";
    $.each($('.item'),function()
    {
        current_list += $(this).text() + ",";
    });
    return current_list;
}

//Checking if input is valid email
function isValidEmailAddress(emailAddress) {
    var pattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i;
    return pattern.test(emailAddress);
}

function manage_item(element)
{
    var text = $(element).text();
    $('button:contains('+text+')').remove();
    var i = list_items.indexOf(text);
    if(i != -1) {
    list_items.splice(i, 1);
    }
    $('#input_text').val(text);
}
