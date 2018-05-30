function openGroup(groupName, elmnt) {
    // Hide all elements with class="tabcontent" by default */
    var i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Show the specific tab content
    document.getElementById(groupName).style.display = "block";
}

function openGroupPanel(groupName, elmnt) {
    var i, group_content;
    group_content = document.getElementsByClassName("group_content");
    for (i = 0; i < group_content.length; i++) {
        group_content[i].style.display = "none";
    }

    // Show the specific tab content
    document.getElementById(groupName).style.display = "block";
}

function toggle(id, elmnt) {
  var ele_id = document.getElementById(id);
  if(ele_id.style.display == "inline-block") {
    ele_id.style.display = "none";
  } else {
    ele_id.style.display = "inline-block";
  }
}
