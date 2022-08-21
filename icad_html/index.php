<?php
/**
 * Home Page for the main site
 * @license      Apache License v2.0
 * @author       Smashedbotatos <ian@icarey.net>
 * @copyright    Copyright © 2009-2018 iCarey Computer Services.
 *
 */

?>

<!-- Header Import -->
<?php include_once('header.php'); ?>
    <div class="row">
      <div class="col-12">
        <h3 class="align-content-center pagetitle">Last 5 Calls Today</h3>
        <hr />
          <?php
            echo '<div class="row mb-3">';
            echo '<div class="col-3"><h5 style="display: inline; width: 100%;">Name:</h5></div>';
            echo '<div class="col-3"><h5 style="display: inline; width: 100%;">Call Time:</h5></div>';
            echo '<div class="col-3"><h5 style="display: inline; width: 100%;">Audio:</h5></div>';
            echo '<div class="col-3"><h5 style="display: inline; width: 100%;">Options:</h5></div>';
            echo '</div>';
          $calls = new calls_class();
          $result = $calls->get_last_calls();
          echo $result;
        ?>
      </div>
    </div>

<!-- Footer Import -->
<?php include_once('footer.php'); ?>