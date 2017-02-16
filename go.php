<?php
$postdata = file_get_contents('php://input');
$request = json_decode($postdata);

if (!isset($request->username) ||
	!isset($request->password)) {
	die();
}

$username = trim($request->username);
$password = trim($request->password);

$cmd = "python go.py $username $password";
exec($cmd, $output, $ret);
