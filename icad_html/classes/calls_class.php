<?php

class calls_class
{

    public function get_last_calls(): string
    {
        $config = parse_ini_file('includes/config.ini.php', 1, true);
        $database = new DatabaseConnect($config['mysql']['host'], $config['mysql']['user'], $config['mysql']['password'], $config['mysql']['database'], $config['mysql']['port']);
        $resultcalls = $database->query("SELECT * FROM fd_notify_detections WHERE detection_timestamp >= CURDATE() AND detection_timestamp < CURDATE() + INTERVAL 1 DAY ORDER BY detection_timestamp DESC LIMIT 5");
        if ($database->num_rows($resultcalls) == 0) {
           $resultfinal = '<div class="alert alert-danger" role="alert">No Calls Today</div>';
        } else {
            $resultfinal = '';
            while ($row = $database->fetch($resultcalls)) {
                $call_id = $row['detection_id'];
                $call_department = $row['detection_tone_name'];
                $call_mp3 = $row['detection_mp3_url'];
                $call_time = $row['detection_timestamp'];
                $call_transcription = $row['detection_transcription'];

                $resultfinal .= '<div class="row mb-3">';
                $resultfinal .= '<div class="col-3"><h6 style="display: inline; color: #9a3a3a">' . $call_department . '</h6></div>';
                $resultfinal .= '<div class="col-3"><h6 style="display: inline;">' . $call_time . '</h6></div>';
                $resultfinal .= '<div class="col-3"><audio style="width: 100%;" controls>';
                $resultfinal .= '<source src="' . $call_mp3 . '" type="audio/mpeg">';
                $resultfinal .= 'Your browser does not support the audio element.';
                $resultfinal .= '</audio></div>';
                $resultfinal .='<div class="col-3"><div class="dropdown">';
                $resultfinal .='<button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton' . $call_id . '" data-bs-toggle="dropdown" aria-expanded="false">';
                $resultfinal .='Menu';
                $resultfinal .='</button>';
                $resultfinal .='<ul class="dropdown-menu" aria-labelledby="dropdownMenuButton' . $call_id . '">';
                $resultfinal .='<li><a class="dropdown-item" href="#" onclick="div_show_trans(\'' . $call_transcription . '\')"><button class="btn btn-outline-warning">Transcription</button></a></li>';
                $resultfinal .='</ul>';
                $resultfinal .='</div>';
                $resultfinal .='</div>';
                $resultfinal .='</div>';
            }
        }
        return $resultfinal;
    }

    public function get_calls_list($sql): string
    {
        $config = parse_ini_file('includes/config.ini.php', 1, true);
        $database = new DatabaseConnect($config['mysql']['host'], $config['mysql']['user'], $config['mysql']['password'], $config['mysql']['database'], $config['mysql']['port']);
        $resultcalls = $database->query($sql);
        if ($database->num_rows($resultcalls) == 0) {
            $resultfinal = '<div class="alert alert-danger" role="alert">No Calls</div>';
        } else {
            $resultfinal = '';
            while ($row = $database->fetch($resultcalls)) {
                $call_id = $row['detection_id'];
                $call_department = $row['detection_tone_name'];
                $call_mp3 = $row['detection_mp3_url'];
                $call_time = $row['detection_timestamp'];
                $call_transcription = $row['detection_transcription'];

                $resultfinal .= '<div class="row mb-3">';
                $resultfinal .= '<div class="col-3"><h6 style="display: inline; color: #9a3a3a">' . $call_department . '</h6></div>';
                $resultfinal .= '<div class="col-3"><h6 style="display: inline;">' . $call_time . '</h6></div>';
                $resultfinal .= '<div class="col-3"><audio style="width: 100%;" controls>';
                $resultfinal .= '<source src="' . $call_mp3 . '" type="audio/mpeg">';
                $resultfinal .= 'Your browser does not support the audio element.';
                $resultfinal .= '</audio></div>';
                $resultfinal .='<div class="col-3"><div class="dropdown">';
                $resultfinal .='<button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton' . $call_id . '" data-bs-toggle="dropdown" aria-expanded="false">';
                $resultfinal .='Menu';
                $resultfinal .='</button>';
                $resultfinal .='<ul class="dropdown-menu" aria-labelledby="dropdownMenuButton' . $call_id . '">';
                $resultfinal .='<li><a class="dropdown-item" href="#" onclick="div_show_trans(\'' . $call_transcription . '\')"><button class="btn btn-outline-warning">Transcription</button></a></li>';
                $resultfinal .='</ul>';
                $resultfinal .='</div>';
                $resultfinal .='</div>';
                $resultfinal .='</div>';
            }
        }
        return $resultfinal;
    }

    public function get_calls_total($sql): string
    {
        $config = parse_ini_file('includes/config.ini.php', 1, true);
        $database = new DatabaseConnect($config['mysql']['host'], $config['mysql']['user'], $config['mysql']['password'], $config['mysql']['database'], $config['mysql']['port']);
        $result = $database->query($sql);
        $calls_total = $result->fetch_assoc();

        return $calls_total['total'];
    }

}