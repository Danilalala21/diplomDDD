<?php

require_once 'setting.php';

//Подключение к MySQL

$connection = new mysqli($host, $user, $pass, $data;)
if ($connection->connect_error) die('error connection');