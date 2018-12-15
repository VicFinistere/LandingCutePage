var eventsArray = [];
{% for event in my_events %}
var title = '{{event.title}}';
var start = '{{event.start}}';
var end = '{{event.end}}';
eventsArray.push({ title: title, start: start, end: end });
{% endfor %}
alert(eventsArray);


$('#calendar').fullCalendar({
    header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,basicWeek,basicDay'
    },
    defaultDate: '2018-03-12',
    navLinks: true, // can click day/week names to navigate views
    editable: true,
    eventLimit: true, // allow "more" link when too many events
    events: eventsArray
});