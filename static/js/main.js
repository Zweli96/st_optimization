$(document).ready(function () {
  $("#data_table").DataTable();
});

$(document).ready(function () {
  $("#data_table_routes").DataTable({
    scrollX: true,
    scrollCollapse: true,
    // fixedHeader: true,
    fixedColumns: {
      left: 2,
    },
  });
});

$("#data_table_routes").css("overflow", "unset");
