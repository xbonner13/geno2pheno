<?php

ignore_user_abort(true);

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

if( empty($_FILES['file']) ){
    exit("error");
}

$base = "/var/www/html";
$id = uniqid();
$dir = "$base/output/$id";

shell_exec("mkdir -p $dir");

$file = "$dir/unaligned_input.fasta";

move_uploaded_file($_FILES['file']['tmp_name'], $file);

shell_exec("python $base/selenium_python_geno2pheno.py $file $base/chromedriver $dir/ 0");

if( empty( glob("$dir/*_log") ) ){

    exit("error");
}

unlink($file);

$tar = "$base/output/$id.tar.gz";

shell_exec("tar -czf $tar -C $dir .");

header("Location: output.php?dir=$id");
?>