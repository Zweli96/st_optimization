$(document).ready(function () {
  $("#data_table").DataTable();
  $("#data_table_routes").DataTable({
    scrollX: true,
    scrollCollapse: true,
    // fixedHeader: true,
    fixedColumns: {
      left: 2,
    },
  });
  $("#data_table_routes").css("overflow", "unset");
  $(".route_list").sortable({
    opacity: 0.5,
    cursor: "move",
  });

  $(document).on("change", ".addroutes", function () {
    var optionSelected = $(this).find("option:selected");
    var valueSelected = optionSelected.val();
    var textSelected = optionSelected.text();
    var select_item = $(this);
    var parent = $(this).parent().parent();

    var facility_id = parseInt(
      $(select_item).attr("id").replace("choose_route_", "")
    );
    console.log(facility_id);

    var facility_name = parent.find("td:nth-child(2)").text();
    console.log("parent element  " + parent[0].nodeName.toLowerCase());
    console.log("facility name  " + facility_name);

    console.log("html elememnt " + optionSelected);
    console.log("value selected " + valueSelected);
    console.log("text selected " + textSelected);

    console.log("facility id  " + facility_id);
    console.log("facility name  " + facility_name);

    var list_id = "facilities_route_" + valueSelected;
    var list_item = $(
      "<li class='list-group-item d-flex justify-content-between align-items-center'" +
        "id='facility_added_" +
        facility_id +
        "'>" +
        facility_name +
        "<span class='badge badge-danger badge-pill remove_facility'><i class='fas fa-times'></i></span>" +
        "</li>"
    );
    console.log("list id  " + list_id);
    console.log("list item  " + list_item[0].outerHTML);

    $(list_item).appendTo($("#" + list_id));
    $(".route_list").sortable("refresh");
  });

  $(document).on("click", ".remove_facility", function () {
    var facility = $(this).parent();
    console.log(facility.attr("id"));
    $("#choose_route_" + facility.attr("id"))
      .val("")
      .change();
  });
});
