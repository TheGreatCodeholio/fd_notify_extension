<?php
/**
 * header.php for iCAD
 * @license      Apache License v2.0
 * @author       Smashedbotatos <ian@icarey.net>
 * @copyright    Copyright © 2009-2022 iCarey Computer Services.
 *
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

$config = parse_ini_file('includes/config.ini.php', 1, true);
require_once 'classes/basic.php';
require_once 'classes/calls_class.php';
?>

<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset="utf-8">
    <title>iCAD Dispatch</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css?family=Ubuntu:300,300i,400,400i,500,500i,700,700i" rel="stylesheet">
    <!-- Icon Fonts -->
    <script defer src="js/all.min.js"></script>
    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/icad.css">
    <!-- Favicon Configuration -->
    <link rel="apple-touch-icon" sizes="180x180" href="img/icon/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="img/icon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="img/icon/favicon-16x16.png">
    <link rel="manifest" href="img/icon/site.webmanifest">
    <link rel="mask-icon" href="img/icon/safari-pinned-tab.svg" color="#c50000">
    <link rel="shortcut icon" href="img/icon/favicon.ico">
    <meta name="apple-mobile-web-app-title" content="BC Fire">
    <meta name="application-name" content="BC Fire">
    <meta name="msapplication-TileColor" content="#525252">
    <meta name="msapplication-config" content="img/icon/browserconfig.xml">
    <meta name="theme-color" content="#ffffff">
    <!-- JavaScript -->
    <script src="js/icad.js"></script>
</head>
<body>
<?php
// Add nws-alerts alert box cache file
include_once("nws-alerts-config.php");
include($cacheFileDir.$aboxFileName);
// Insert nws-alerts alert box
echo $alertBox;
?>
<div>
</div>
<div class="fle">
<img src="/img/header.png" class="rounded mx-auto d-block img-fluid" alt="iCAD Dispatch">
</div>
<div class="container"> <!-- Main Container -->
    <nav class="navbar navbar-expand-md navbar-dark">
        <div class="container-fluid">
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/index.php">Home</a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            Call Statistics
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
                            <li><a class="dropdown-item" href="/stats.php?time=today">Today</a></li>
                            <li><a class="dropdown-item" href="/stats.php?time=week">Week</a></li>
                            <li><a class="dropdown-item" href="/stats.php?time=month">Month</a></li>
                            <li><a class="dropdown-item" href="/stats.php?time=year">Year</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <!-- Popup Div Starts Here -->
    <div id="TransWindow">
        <div id="popupTrans">
            <!-- Registration Form -->
            <div class="container">
                <form id="view-form">
                    <div class="row">
                        <div class="col-10">
                            <h2 id="TransTitle">Call Transcription</h2>
                        </div>
                        <div class="col-2">
                            <i id="popup-close" class="fa fa-2x fa-times-circle" onclick ="div_hide_trans()" title="Close" ></i>
                        </div>
                    </div>
                    <div class="form-group">
                        <textarea readonly class="form-control" id="transcription" name="transcription" placeholder="None" rows="4" cols="50"></textarea>
                    </div>
                </form>
            </div>
        </div>
    </div>
