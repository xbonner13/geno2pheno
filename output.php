<?php

ignore_user_abort(true);

if(! isset($_GET['dir'])){
    exit("error");
}

$tar = "/var/www/html/output/".$_GET['dir'].".tar.gz";

if( ! file_exists($tar) ){
    exit("error");
}

ob_clean();
flush();

header('Content-Description: File Transfer');
header('Content-Type: application/octet-stream');
header('Content-Length: ' . filesize($tar));
header('Content-Disposition: attachment; filename=' . basename( $tar ));

readfile($tar);

unlink($tar);
shell_exec("rm -rf /var/www/html/output/".$_GET['dir']);

?>