<?php
/**
 * Admin page bcfirewire.com
 * @license      Apache License v2.0
 * @author       Smashedbotatos <ian@icarey.net>
 * @copyright    Copyright © 2009-2022 iCarey Computer Services.
 *
 */

?>
<!-- Header Import -->
<?php include_once('header.php');
if (isset($_GET["page"])) {
    $page  = $_GET["page"];
    if($page == 0){
        $page = 1;
    }
} else {
    $page=1;
};
$results_per_page = 10;
$start_from = ($page-1) * $results_per_page;

if (!isset($_GET['time'])) {
    echo '<div class="alert alert-danger" role="alert">Please set a timeframe.</div>';
    header( "refresh:3;url=index.php" );
} else {
    if ($_GET['time'] == "week"){
        $timeframe = "Week";
        $calls_list_sql = "SELECT * FROM fd_notify_detections WHERE YEARWEEK(detection_timestamp, 1) = YEARWEEK(CURDATE(), 1) ORDER BY detection_timestamp DESC LIMIT $start_from," . $results_per_page;
        $most_calls_sql = "SELECT detection_tone_name, detection_timestamp, COUNT(*) AS total FROM fd_notify_detections WHERE YEARWEEK(detection_timestamp, 1) = YEARWEEK(CURDATE(), 1) GROUP BY detection_tone_name ORDER BY total DESC LIMIT 5";
        $total_calls_sql = "SELECT COUNT(*) AS total FROM fd_notify_detections WHERE YEARWEEK(detection_timestamp, 1) = YEARWEEK(CURDATE(), 1)";

    } elseif ($_GET['time'] == "today") {
        $timeframe = "Day";
        $calls_list_sql = "SELECT * FROM fd_notify_detections WHERE detection_timestamp >= CURDATE() AND detection_timestamp < CURDATE() + INTERVAL 1 DAY ORDER BY detection_timestamp DESC LIMIT $start_from," . $results_per_page;
        $most_calls_sql = "SELECT detection_tone_name, detection_timestamp, COUNT(*) AS total FROM fd_notify_detections WHERE detection_timestamp >= CURDATE() AND detection_timestamp < CURDATE() + INTERVAL 1 DAY GROUP BY detection_tone_name ORDER BY total DESC LIMIT 5";
        $total_calls_sql = "SELECT COUNT(*) AS total FROM fd_notify_detections WHERE detection_timestamp >= CURDATE() AND detection_timestamp < CURDATE() + INTERVAL 1 DAY";

    } elseif ($_GET['time'] == "month"){
        $timeframe = "Month";
        $calls_list_sql = "SELECT * FROM fd_notify_detections WHERE MONTH(detection_timestamp) = MONTH(CURDATE()) AND YEAR(detection_timestamp) = YEAR(CURDATE()) ORDER BY detection_timestamp DESC LIMIT $start_from," . $results_per_page;
        $most_calls_sql = "SELECT detection_tone_name, detection_timestamp, COUNT(*) AS total FROM fd_notify_detections WHERE MONTH(CURDATE()) AND YEAR(detection_timestamp) = YEAR(CURDATE()) GROUP BY detection_tone_name ORDER BY total DESC LIMIT 5";
        $total_calls_sql = "SELECT COUNT(*) AS total FROM fd_notify_detections WHERE MONTH(detection_timestamp) = MONTH(CURDATE()) AND YEAR(detection_timestamp) = YEAR(CURDATE())";

    } elseif ($_GET['time'] == "year"){
        $timeframe = "Year";
        $calls_list_sql = "SELECT * FROM fd_notify_detections WHERE YEAR(detection_timestamp) = YEAR(CURDATE()) ORDER BY detection_timestamp DESC LIMIT $start_from," . $results_per_page;
        $most_calls_sql = "SELECT detection_tone_name, detection_timestamp, COUNT(*) AS total FROM fd_notify_detections WHERE YEAR(detection_timestamp) = YEAR(CURDATE()) GROUP BY detection_tone_name  ORDER BY total DESC LIMIT 5";
        $total_calls_sql = "SELECT COUNT(*) AS total FROM fd_notify_detections WHERE YEAR(detection_timestamp) = YEAR(CURDATE())";
    } else {
        header( "refresh:0;url=index.php" );
    }
}
$most_labels = [];
$most_data = [];
$calls_class = new calls_class();
$call_total = $calls_class->get_calls_total($total_calls_sql);
$most_labels[] = "Total";
$most_data[] = $call_total;
$calls_list = $calls_class->get_calls_list($calls_list_sql);

$database = new DatabaseConnect($config['mysql']['host'], $config['mysql']['user'], $config['mysql']['password'], $config['mysql']['database'], $config['mysql']['port']);
$most_result = $database->query($most_calls_sql);

while ($row = $database->fetch($most_result)) {
    $most_labels[] = $row['detection_tone_name'];
    $most_data[] = $row['total'];

}
?>
<!-- Page Content -->
<div class="container">
    <div class="row">
        <div class="col-12">
            <h3 class="align-content-center pagetitle">Statistics this <?php echo $timeframe ?>.</h3>
            <hr />
        </div>
    </div>
    <div class="row">
        <div class="col mt-4">

        </div>
        <div class="col mt-4">
            <h6 style="color: #c24c4c">Most Calls this <?php echo $timeframe ?>.</h6>
            <canvas id="most_chart"></canvas>
        </div>
        <div class="col mt-4">

        </div>
    </div>
    <div class="row">
        <div class="col-12">
            <h6 class="mt-3" style="color: #c24c4c">Call list for this <?php echo $timeframe ?>.</h6>
            <hr />
            <?php
            echo '<div class="row mb-3">';
            echo '<div class="col-3"><h5 style="display: inline; width: 100%;">Name:</h5></div>';
            echo '<div class="col-3"><h5 style="display: inline; width: 100%;">Call Time:</h5></div>';
            echo '<div class="col-3"><h5 style="display: inline; width: 100%;">Audio:</h5></div>';
            echo '<div class="col-3"><h5 style="display: inline; width: 100%;">Options:</h5></div>';
            echo '</div>';
            echo $calls_list;

            $total_pages = ceil($call_total / $results_per_page); // calculate total pages with results

            echo '<div class="mt-3 col-4"></div>';
            echo '<div class="mt-3 col-4">Pages</br>';
            for ($i=1; $i<=$total_pages; $i++) {  // print links for all pages
                echo "<a href='stats.php?time=".$_GET['time']."&page=".$i."'";
                if ($i==$page)  echo " class='curPage'";
                echo ">".$i."</a> ";
            };
            echo '</div>';
            echo '<div class="mt-3 col-4"></div>';
            ?>

        </div>
    </div>
</div>

<!-- Chart JS -->
<script src="/js/chart.min.js"></script>
<script>

    Chart.defaults.font.size = 14;
    Chart.defaults.color = "#B7C2C0FF";
    const ctx_most = document.getElementById('most_chart');
    const mostChart = new Chart(ctx_most, {
        type: 'bar',
        data: {
            labels: <?php echo json_encode($most_labels);?>,
            datasets: [{
                label: '# of Calls',
                barThickness: "flex",
                data: <?php echo json_encode($most_data);?>,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)'

                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    ticks: {
                        color: "#B7C2C0FF"
                    }
                },
                y: {
                    ticks: {
                        color: "#B7C2C0FF"
                    },
                    beginAtZero: true
                }
            }
        }
    });
</script>
<!-- Footer Import -->
<?php include_once('footer.php'); ?>