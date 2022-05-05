function hideAlert(){
  var alert = document.querySelector("#alert-message")
  alert.style.display = "none";
}


// these functions are to hide and show the sidebar windows when clicking on their banner
function hideInspector(){
  var inspector = document.querySelector("#inspector-window")
  if (inspector.style.display != "none")
    $("#inspector-window").slideUp("fast");
  else{
    $("#inspector-window").slideDown("fast");
    $("#create-item-window").slideUp("fast");
    $("#events-window").slideUp("fast");
    $("#create-event-window").slideUp("fast");
  }
}


function hideCreateItem(){
  var inspector = document.querySelector("#create-item-window")
  if (inspector.style.display != "none")
    $("#create-item-window").slideUp("fast");
  else{
    $("#create-item-window").slideDown("fast");
    $("#inspector-window").slideUp("fast");
    $("#events-window").slideUp("fast");
    $("#create-event-window").slideUp("fast");
  }
}


function hideEvents(){
  var inspector = document.querySelector("#events-window")
  if (inspector.style.display != "none")
    $("#events-window").slideUp("fast");
  else{
    $("#events-window").slideDown("fast");
    $("#create-item-window").slideUp("fast");
    $("#inspector-window").slideUp("fast");
    $("#create-event-window").slideUp("fast");

  }
}


function hideCreateEvent(){
  var inspector = document.querySelector("#create-event-window")
  if (inspector.style.display != "none")
    $("#create-event-window").slideUp("fast");
  else{
    $("#create-event-window").slideDown("fast");
    $("#events-window").slideUp("fast");
    $("#create-item-window").slideUp("fast");
    $("#inspector-window").slideUp("fast");

  }
}


// scan barcode into textbox
let scanned = [];
var items_to_add_span_element = document.getElementById("items-to-add-list")

$("#scan-item").keyup(function(event) {
  var input_field = document.getElementById("scan-item")
  var input = document.getElementById("scan-item").value;

  console.log(typeof input)
// check for 'return' key press
if (event.keyCode === 13) {

// check if input value is length of 8
if (input.length === 8) {

// open the barcode json file
$.getJSON( "/json/barcodes", function(json){

// check if the barcode is already in the array
if (!(scanned.includes(json[input][0]))){

        // append each scanned item to the span element
        items_to_add_span_element.innerHTML = items_to_add_span_element.innerHTML + json[input][4] + "<br>";

        // append item's ID into the array
        scanned.push(json[input][0]);

        // add array of barcode numbers into a hidden input in the event form
        document.getElementById('scanned-item-list').value = scanned;
        console.log( document.getElementById('scanned-item-list').value)

        input_field.value = "" 

      }
    })
  }
}

});


// populate the event items in the item scanner
var event_select_field = document.getElementById('event_select');
var event_items_element = document.getElementById('items-in-event-list');

if (!(event_select_field === null))
  event_select_field.addEventListener('change', (e) => {
    var selected_event = event_select_field.value
    console.log(selected_event)
    $.getJSON( "/json/events", function(json){
      var event_items = JSON.parse(json[selected_event][5])['items'];
      console.log(event_items)
      event_items_element.innerHTML = ""
      $.getJSON( "/json/itemdict2", function(json2){ 
        for (var i of event_items) {
          event_items_element.innerHTML = event_items_element.innerHTML + json2[i][4] + " | " + json2[i][1] + "<br>"
      // console.log(json2[i])

    }
  })
    }) 
  });


function collapse(button) {

              // console.log(button)

              // select the row of the current python loop
              var x = document.querySelectorAll(".row" + button);

              // turn the button to "collapse" when pushed, then "expand" when pushed again
              if ($("#button" + button).html() == "Expand") {
                $("#button" + button).html("Collapse");
              }else {
                $("#button" + button).html("Expand");
              }

              // function to collapse and expand rows that have duplicates inside of them
              x.forEach(x => {
                $(x).children().slideToggle("fast");
              });

            }

// this function is to add a clicked item from the JSON file to the inspector fields and open the inspector when button is clicked
function inspectAndHide(index){
  $("#inspector-window").slideDown("fast");
  $("#create-item-window").slideUp("fast");
  $("#events-window").slideUp("fast");

  getItem(index);
  function getItem(index){
    $.getJSON('/json/itemdict2', function(jd) {
      console.log(index)
      $("#idnumber").val(jd[index][0]);
      $("#barcode").val(jd[index][1]);
      $("#serial").val(jd[index][2]);
      $("#manufacturer").val(jd[index][3]);
      $("#name").val(jd[index][4]);
      $("#category").val(jd[index][5]);
      $("#storage").val(jd[index][6]);
      $("#status").val(jd[index][7]);
      $("#notes").val(jd[index][8]);
    });
  }
}

// get the item that is clicked on in the table and
// populate the inspector
var table = document.getElementById('inv-table').addEventListener
('click',buttonClick);

function buttonClick(e){
  var clickedRow = e.path[1].id
  if (clickedRow != ""){
    console.log(e)
    inspectAndHide(clickedRow)
  }
}


// This will create a confirm pop-up for an item to be added that is
// already reserved in another event during those dates
function conflictingItem(events,item){
  if (confirm("Are you sure? This item is already reserved in one of the following events during one of the event dates: " + events)) {
    addItemToEvent(item)
  } else {
  }
}


// Home Item Search
  document.getElementById('item-search').addEventListener('input', (e) => {
    var inv_table = document.getElementsByClassName("inventory-table")

    var children = inv_table[0].childNodes[5].childNodes

    search_var = document.getElementById('item-search').value.toLowerCase()
    console.clear()

    for (let i = 1; i < children.length; i++) {
            if (children[i].nodeName == "TR")
              var tr = children[i].childNodes[19]
              // console.log(tr.innerHTML)
              
                if (tr.innerHTML.toLowerCase().includes(search_var)){
                  // console.log(tr.innerHTML)
                  tr.parentNode.style.visibility = "visible"
                } else {
                  tr.parentNode.style.visibility = "collapse"
                }

          }
    })


// Event Item Search
  document.getElementById('item-search').addEventListener('input', (e) => {
    var inv_table = document.getElementsByClassName("inventory-table2")

    // console.log(inv_table)

    var children = inv_table[0].childNodes[5].childNodes

    search_var = document.getElementById('item-search').value.toLowerCase()
    // console.clear()

    for (let i = 1; i < children.length; i++) {
            if (children[i].nodeName == "TR")
              var tr = children[i].childNodes[19]
              // console.log(tr.innerHTML)
              
                if (tr.innerHTML.toLowerCase().includes(search_var)){
                  // console.log(tr.innerHTML)
                  tr.parentNode.style.visibility = "visible"
                } else {
                  tr.parentNode.style.visibility = "collapse"
                }

          }
    })
