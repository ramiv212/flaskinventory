// get the item that is clicked on in the table and
// populate the inspector
var table = document.querySelector('#mobile-inv-table').addEventListener
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

  var clickedRow = e.path[0].id
  if (clickedRow != ""){
    console.log(clickedRow)
    $("#" + clickedRow + "info").slideToggle("fast");
  }
}