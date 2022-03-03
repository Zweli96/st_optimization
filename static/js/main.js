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

function getCookie(name) {
  var dc = document.cookie;
  var prefix = name + "=";
  var begin = dc.indexOf("; " + prefix);
  if (begin == -1) {
    begin = dc.indexOf(prefix);
    if (begin != 0) return null;
  } else {
    begin += 2;
    var end = document.cookie.indexOf(";", begin);
    if (end == -1) {
      end = dc.length;
    }
  }
  // because unescape has been deprecated, replaced with decodeURI
  //return unescape(dc.substring(begin + prefix.length, end));
  return decodeURI(dc.substring(begin + prefix.length, end));
}

$(document).ready(function () {
  // Turn tables into data tables
  $("#data_table").DataTable();

  
  // Modal on the dashboard to put in the samples
  $(document).on('show.bs.modal','#editModal', function (e) {
    console.log('Activated')
    var reportedBy = $(e.relatedTarget).attr("data-name");
    var sample_volumes = $(e.relatedTarget).attr("data-volumes");
    var sample_volumes = sample_volumes.split("_"); 
    $(e.currentTarget).find('input[id="vl-samples"]').val(sample_volumes[0]);
    $(e.currentTarget).find('input[id="eid-samples"]').val(sample_volumes[1]);
    $(e.currentTarget).find('input[id="tb-samples"]').val(sample_volumes[2]);
    $(e.currentTarget).find('input[id="other-samples"]').val(sample_volumes[3]);
  });

  var groupColumn = 2;
  // Turn the routes table into a data table with defined settings
  $("#data_table_routes").DataTable({
    scrollX: true,
    scrollCollapse: true,
    // fixedHeader: true,
    fixedColumns: {
      left: 2,
    },
    ///////////////////////////////////////////////
    columnDefs: [{ visible: false, targets: groupColumn }],
    order: [[groupColumn, "asc"]],
    displayLength: 10,
    drawCallback: function (settings) {
      var api = this.api();
      var rows = api.rows({ page: "current" }).nodes();
      var last = null;

      api
        .column(groupColumn, { page: "current" })
        .data()
        .each(function (group, i) {
          if (last !== group) {
            $(rows)
              .eq(i)
              .before(
                '<tr class="group" style="background-color:#89CFF0"><td colspan="12"><strong>' +
                  group +
                  "</strong></td></tr>"
              );

            last = group;
          }
        });
    },
  });

  // Order by the grouping
  $("#data_table_routes tbody").on("click", "tr.group", function () {
    var currentOrder = table.order()[0];
    if (currentOrder[0] === groupColumn && currentOrder[1] === "asc") {
      table.order([groupColumn, "desc"]).draw();
    } else {
      table.order([groupColumn, "asc"]).draw();
    }
  });

  // I'm not sure if this is working
  $("#data_table_routes").css("overflow", "unset");

  // sortable list for the routes
  $(".route_list").sortable({
    opacity: 0.5,
    cursor: "move",
  });

  // adding the routes from the facilities list into the specific route list
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
      "<li class='route_list_item list-group-item d-flex justify-content-between align-items-center'" +
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

  // when you click the x on a facility that has already been added into route list
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

  // Save the routes when the
  $(document).on("click", "#save_routes", function () {
    var csrftoken = getCookie("csrftoken");

    var routes = [];

    $(".route_list").each(function (route_index) {
      var route_facilities = { route: route_index + 1, facilities: [] };
      $(this)
        .sortable("refreshPositions")
        .children(".route_list_item")
        .each(function () {
          console.log($(this).attr("id"));
          facility_id = parseInt(
            $(this).attr("id").replace("facility_added_", "")
          );
          route_facilities.facilities.push(facility_id);
        });
      routes.push(route_facilities);
    });

    console.log(routes);
    $.ajax({
      url: "",
      type: "post",
      headers: {
        "X-CSRFToken": csrftoken,
      },
      data: {
        routes: JSON.stringify(routes),
        selected_district: JSON.stringify(parseInt(selected_district)),
        courier_count: JSON.stringify(courier_count),
        user_id: JSON.parse(document.getElementById("user_id").textContent),
      },
      success: function (data) {
        // console.log(data.created_routes);
        alert(
          "Routes for " +
            selected_district_name +
            " have been successfully created"
        );
      },
      content_type: "application/json",
    });
  });

  // Get todays date for the date picker
  if (document.getElementById("selected_date")) {
    if (JSON.parse(document.getElementById("selected_date").textContent)) {
      $("#datePicker").val(
        JSON.parse(document.getElementById("selected_date").textContent).slice(
          0,
          10
        )
      );
    } else {
      $("#datePicker").val(new Date().toJSON().slice(0, 10));
    }
  } else {
    $("#datePicker").val(new Date().toJSON().slice(0, 10));
  }

  // Make the facilities group a select 2
  $("#facility_group_facilities_select").select2();

  if (JSON.parse(document.getElementById("fg_facilities").textContent)) {
    $("#facility_group_facilities_select").val(
      JSON.parse(document.getElementById("fg_facilities").textContent)
    );
    $("#facility_group_facilities_select").trigger("change");
  }

});
