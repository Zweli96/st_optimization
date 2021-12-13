function facility_count() {
  $(".route_list").each(function () {
    var route_list = $(this);
    var id = route_list.attr("id");
    console.log(id);
    var count_id = route_list.attr("id").replace("facilities_route_", "");
    var count = $("#" + id + " li").length;
    var route_list_count = $("#route_facilities_count_" + count_id);
    route_list_count.text(count);
    console.log(count); // if it is an input/select/textarea field
    // TODO: do something with the value
  });
}

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

    if ($("#facility_added_" + facility_id).length) {
      $("#facility_added_" + facility_id).remove();
    }

    var facility_name = parent.find("td:nth-child(2)").text();

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

    facility_count();
  });

  $(document).on("click", ".remove_facility", function () {
    var facility = $(this).parent();
    var facility_id = facility.attr("id").replace("facility_added_", "");
    console.log(facility.attr("id"));
    $("#choose_route_" + facility_id)
      .val("")
      .change();
    console.log($("#choose_route_" + facility_id).find("option:selected"));
    facility.remove();
    facility_count();
  });
});
