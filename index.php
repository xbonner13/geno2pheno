<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

/*
    gcloud beta compute --project "rcgrant-training-clarkmu" ssh --zone "us-central1-a" "g2p"

    python sel.py ./unaligned_input.fasta /var/www/html/chromedriver /var/www/html/1/ 0

    curl http://23.236.60.247/ -F file=@./unaligned_input.fasta
*/

    $cwd = "/var/www/html";
    $dir = "$cwd/" . uniqid();
    $file = "$dir/unaligned_input.fasta";

    try{
        $inputFileTmp = $_FILES['file']['tmp_name'];
        $fileInfo = pathinfo($inputFileTmp);
        if( $fileParts['extension'] !== 'fasta' || ! move_uploaded_file($inputFileTmp, $file) ){
            throw new Exception();
        }
    }catch(Exception $e){
        die("No File uploaded.");
    }

    shell_exec("mkdir -p $dir");

    shell_exec("python $cwd/sel.py $file $cwd/chromedriver $dir 0");

    // return file

    if( empty( glob("$dir/*_log") ) ){

        die("Failed to get content from g2p");
    }

    $tar = "$dir/g2p.tar.gz";

    shell_exec("tar -zvcf $tar -C $dir .");

    ob_clean();

    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Length: ' . filesize($tar));
    header('Content-Disposition: attachment; filename=' . basename( $tar ));

    readfile($tar);

    // shell_exec("rm -rf $dir");

?>