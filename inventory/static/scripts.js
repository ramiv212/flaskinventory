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
var table = document.querySelector('#inv-table').addEventListener
('click',buttonClick);

function buttonClick(e){
  console.log(e)

  if (!("path" in e))
    Object.defineProperty(e, "path", {
      get: function() {
        var path = [];
        var currentElem = this.target;
        while (currentElem) {
          path.push(currentElem);
          currentElem = currentElem.parentElement;
        }
        if (path.indexOf(window) === -1 && path.indexOf(document) === -1)
          path.push(document);
        if (path.indexOf(window) === -1)
          path.push(window);
        return path;
      }
    });

  var clickedRow = e.path[1].id
  if (clickedRow != ""){
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

  // if Home search bar is in the page
  if (!(document.getElementById('item-search') == null)){

  // run the function every time a letter is added to search bar
  document.getElementById('item-search').addEventListener('input', (e) => {
    var inv_table = document.getElementsByClassName("inventory-table")

    // get the children of the inventory table
    var children = inv_table[0].childNodes[5].childNodes

    // get the letters in the search bar
    search_var = document.getElementById('item-search').value.toLowerCase()
    console.clear()

    // for every child
    for (let i = 1; i < children.length; i++) {

            // if the child is a tr 
            if (children[i].nodeName == "TR")

              // name of item in tr
            var name_tr = children[i].childNodes[19]
            var tr2 = children[i]

                // if the child has more than 0 nodes
                if(tr2.childNodes.length != 0) {

                  // if the child has more than 1 node
                  if (tr2.childNodes.length != 1){

                  // manufacturer of item in tr
                  manufacturer_tr = tr2.childNodes[11].innerHTML

                  // barcode of item in tr
                  barcode_tr = tr2.childNodes[23].innerHTML
                }
              }
                // concatenate manufacturer, name and barcode
                full_item = manufacturer_tr.toLowerCase() + " " + name_tr.innerHTML.toLowerCase() + " " + barcode_tr

                // check if the search var is in the concatenated item string
                if (full_item.includes(search_var)){
                  // show the searched items
                  name_tr.parentNode.style.visibility = "visible"
                  $("#button" + i).html("Expand");
                  // hide all other items
                } else {
                  name_tr.parentNode.style.visibility = "collapse"
                }

              }
            })
}

// Event Item Search

  // if Home search bar is in the page
  if (!(document.getElementById('item-search2') == null)){

  // run the function every time a letter is added to search bar
  document.getElementById('item-search2').addEventListener('input', (e) => {
    var inv_table = document.getElementsByClassName("inventory-table2")

    // get the children of the inventory table
    var children = inv_table[0].childNodes[5].childNodes

    // get the letters in the search bar
    search_var = document.getElementById('item-search2').value.toLowerCase()
    console.clear()

    // for every child
    for (let i = 1; i < children.length; i++) {

            // if the child is a tr 
            if (children[i].nodeName == "TR")

              // name of item in tr
            var name_tr = children[i].childNodes[19]
            var tr2 = children[i]

                // if the child has more than 0 nodes
                if(tr2.childNodes.length != 0) {

                  // if the child has more than 1 node
                  if (tr2.childNodes.length != 1){

                  // manufacturer of item in tr
                  manufacturer_tr = tr2.childNodes[11].innerHTML

                  // barcode of item in tr
                  barcode_tr = tr2.childNodes[23].innerHTML
                }
              }
                // concatenate manufacturer, name and barcode
                full_item = manufacturer_tr.toLowerCase() + " " + name_tr.innerHTML.toLowerCase() + " " + barcode_tr

                // check if the search var is in the concatenated item string
                if (full_item.includes(search_var)){
                  // show the searched items
                  name_tr.parentNode.style.visibility = "visible"
                  $("#button" + i).html("Expand");
                  // hide all other items
                } else {
                  name_tr.parentNode.style.visibility = "collapse"
                }

              }
            })
}